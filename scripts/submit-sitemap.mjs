#!/usr/bin/env node
/**
 * Submit current sitemap URLs to search engines (IndexNow + optional Bing).
 *
 * Usage:
 *   node scripts/submit-sitemap.mjs
 *   node scripts/submit-sitemap.mjs --via-api   # hit production /api/sitemap-notify
 *   node scripts/submit-sitemap.mjs --force
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const CONFIG_DIR = join(ROOT, "config");
const STATE_PATH = join(CONFIG_DIR, "sitemap-submit.state.json");

const args = new Set(process.argv.slice(2));
const viaApi = args.has("--via-api");
const force = args.has("--force");

function loadEnvFile() {
  const envPath = join(ROOT, ".env");
  if (!existsSync(envPath)) return;
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const i = trimmed.indexOf("=");
    if (i < 0) continue;
    const k = trimmed.slice(0, i).trim();
    let v = trimmed.slice(i + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    if (!(k in process.env)) process.env[k] = v;
  }
}

loadEnvFile();

const libMod = await import(pathToFileURL(join(ROOT, "functions/sitemap-lib.js")).href);
const seoMod = await import(pathToFileURL(join(ROOT, "functions/seo-config.js")).href);

const indexNowKey = (
  process.env.INDEXNOW_KEY ||
  (existsSync(join(CONFIG_DIR, "indexnow.key"))
    ? readFileSync(join(CONFIG_DIR, "indexnow.key"), "utf8")
    : "")
).trim();

const lastmod = process.env.SITEMAP_LASTMOD || new Date().toISOString().slice(0, 10);
const entries = libMod.listSitemapEntries(lastmod);
const fingerprint = createHash("sha256")
  .update(entries.map((e) => e.loc).join("\n") + "\n" + lastmod)
  .digest("hex");

mkdirSync(CONFIG_DIR, { recursive: true });
const prev = existsSync(STATE_PATH)
  ? JSON.parse(readFileSync(STATE_PATH, "utf8"))
  : null;

if (!force && prev?.fingerprint === fingerprint) {
  console.log("Sitemap unchanged since last successful submit — skipping (use --force).");
  process.exit(0);
}

if (viaApi) {
  const secret = (process.env.SITEMAP_NOTIFY_SECRET || "").trim();
  if (!secret) {
    console.error("SITEMAP_NOTIFY_SECRET required for --via-api");
    process.exit(1);
  }
  const endpoint = `${seoMod.SITE_ORIGIN}/api/sitemap-notify`;
  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      authorization: `Bearer ${secret}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({ force: true }),
  });
  const text = await res.text();
  console.log(`API ${res.status}:`, text);
  let payload = {};
  try {
    payload = JSON.parse(text);
  } catch {
    /* ignore */
  }
  if (!res.ok) process.exit(1);
  if (payload.rateLimited) {
    console.warn("IndexNow rate-limited (429). Key + sitemap are live; retry later if needed.");
  }
  writeFileSync(
    STATE_PATH,
    JSON.stringify({ fingerprint, submittedAt: new Date().toISOString(), via: "api", rateLimited: Boolean(payload.rateLimited) }, null, 2),
  );
  process.exit(0);
}

if (!indexNowKey) {
  console.error("INDEXNOW_KEY missing (config/indexnow.key or env)");
  process.exit(1);
}

const result = await libMod.notifySearchEngines(
  {
    INDEXNOW_KEY: indexNowKey,
    BING_WEBMASTER_API_KEY: process.env.BING_WEBMASTER_API_KEY,
    GOOGLE_SITEMAP_PING_URL: process.env.GOOGLE_SITEMAP_PING_URL,
    SITEMAP_LASTMOD: lastmod,
  },
  { lastmod },
);

console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exit(1);

writeFileSync(
  STATE_PATH,
  JSON.stringify(
    {
      fingerprint,
      submittedAt: new Date().toISOString(),
      via: "direct",
      urlCount: result.urlCount,
    },
    null,
    2,
  ),
);
console.log("Saved submit state → config/sitemap-submit.state.json");
