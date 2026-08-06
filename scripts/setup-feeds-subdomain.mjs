#!/usr/bin/env node
/**
 * Serve sitemap/robots on a DNS-only (grey cloud) subdomain so Cloudflare zone
 * bot checks (JS Detections) do not block Google Search Console fetches.
 *
 * Setup:
 *   1. CNAME feeds.billmaniac.win → billmaniac-website.pages.dev (proxied: OFF)
 *   2. Add feeds.billmaniac.win as a Cloudflare Pages custom domain
 *
 * Usage:
 *   npm run gsc:setup-feeds
 *   npm run deploy
 *
 * Then submit in GSC (Domain property billmaniac.win):
 *   https://feeds.billmaniac.win/sitemap.xml
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

const ZONE_NAME = "billmaniac.win";
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || "9345927ca3f495f89fdaddea61a5e3f9";
const PAGES_PROJECT = "billmaniac-website";
const PAGES_TARGET = `${PAGES_PROJECT}.pages.dev`;
const FEEDS_HOST = "feeds.billmaniac.win";
const FEEDS_LABEL = "feeds";
const SITEMAP_GSC_URL = `https://${FEEDS_HOST}/sitemap.xml`;

function loadEnvFile() {
  for (const name of [".env", ".env.local"]) {
    const envPath = join(ROOT, name);
    if (!existsSync(envPath)) continue;
    for (const line of readFileSync(envPath, "utf8").split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
      const i = trimmed.indexOf("=");
      const k = trimmed.slice(0, i).trim();
      let v = trimmed.slice(i + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      if (!(k in process.env)) process.env[k] = v;
    }
  }
}

loadEnvFile();

let apiToken = (
  process.env.CLOUDFLARE_SETUP_TOKEN ||
  process.env.CLOUDFLARE_API_TOKEN ||
  process.env.CLOUDFLARE_WAF_TOKEN ||
  ""
).trim();

async function cf(path, init = {}) {
  const res = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${apiToken}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  return res.json();
}

async function ensureGreyCloudCname(zoneId) {
  const list = await cf(`/zones/${zoneId}/dns_records?type=CNAME&name=${FEEDS_LABEL}`);
  if (!list.success) {
    throw new Error(list.errors?.[0]?.message || "DNS list failed");
  }

  const existing = (list.result || []).find((r) => r.name === FEEDS_HOST);
  if (existing) {
    if (existing.content === PAGES_TARGET && existing.proxied === false) {
      console.log(`DNS OK: ${FEEDS_HOST} → ${PAGES_TARGET} (DNS only / grey cloud)`);
      return;
    }
    const update = await cf(`/zones/${zoneId}/dns_records/${existing.id}`, {
      method: "PATCH",
      body: JSON.stringify({
        type: "CNAME",
        name: FEEDS_LABEL,
        content: PAGES_TARGET,
        proxied: false,
        ttl: 1,
      }),
    });
    if (!update.success) {
      throw new Error(update.errors?.[0]?.message || "DNS update failed");
    }
    console.log(`Updated DNS: ${FEEDS_HOST} → ${PAGES_TARGET} (DNS only)`);
    return;
  }

  const create = await cf(`/zones/${zoneId}/dns_records`, {
    method: "POST",
    body: JSON.stringify({
      type: "CNAME",
      name: FEEDS_LABEL,
      content: PAGES_TARGET,
      proxied: false,
      ttl: 1,
    }),
  });
  if (!create.success) {
    throw new Error(create.errors?.[0]?.message || "DNS create failed");
  }
  console.log(`Created DNS: ${FEEDS_HOST} → ${PAGES_TARGET} (DNS only / grey cloud)`);
}

function addPagesDomain() {
  const env = { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT };
  delete env.CLOUDFLARE_API_TOKEN;
  delete env.CLOUDFLARE_WAF_TOKEN;
  delete env.CLOUDFLARE_SETUP_TOKEN;

  const res = spawnSync(
    "npx",
    ["wrangler", "pages", "project", "domain", "add", FEEDS_HOST, "--project-name", PAGES_PROJECT],
    { cwd: ROOT, stdio: "inherit", env },
  );
  if (res.status !== 0) {
    console.warn(
      "\nCould not add Pages domain via Wrangler (may already exist). Add manually:\n" +
        `  Cloudflare → Workers & Pages → ${PAGES_PROJECT} → Custom domains → ${FEEDS_HOST}`,
    );
  } else {
    console.log(`Pages custom domain added: ${FEEDS_HOST}`);
  }
}

async function verifyFeed() {
  console.log("\nWaiting for DNS/SSL (15s)…");
  await new Promise((r) => setTimeout(r, 15000));

  for (const ua of ["Googlebot/2.1", "Python-urllib/3.14"]) {
    try {
      const res = await fetch(SITEMAP_GSC_URL, {
        headers: { "User-Agent": ua, Accept: "application/xml,*/*" },
      });
      const body = (await res.text()).slice(0, 40);
      console.log(
        `${ua.slice(0, 24).padEnd(24)} → HTTP ${res.status} ${body.startsWith("<?xml") ? "XML OK" : body}`,
      );
    } catch (e) {
      console.log(`${ua} → ERROR ${e.message}`);
    }
  }
}

async function main() {
  const tokens = [
    process.env.CLOUDFLARE_SETUP_TOKEN,
    process.env.CLOUDFLARE_API_TOKEN,
    process.env.CLOUDFLARE_WAF_TOKEN,
  ].filter(Boolean);

  if (tokens.length === 0) {
    console.error("Set CLOUDFLARE_API_TOKEN or CLOUDFLARE_WAF_TOKEN in .env for DNS (needs Zone.DNS Edit).");
    process.exit(1);
  }

  let zone;
  let dnsOk = false;
  for (const t of tokens) {
    apiToken = t.trim();
    const zones = await cf(`/zones?name=${ZONE_NAME}&account.id=${ACCOUNT}`);
    if (!zones.success) {
      console.warn(`Zone list failed: ${zones.errors?.[0]?.message || "unknown"}`);
      continue;
    }
    zone = zones.result?.find((z) => z.name === ZONE_NAME) || zones.result?.[0];
    if (!zone) continue;

    try {
      await ensureGreyCloudCname(zone.id);
      dnsOk = true;
      break;
    } catch (e) {
      if (!String(e.message).includes("Authentication")) throw e;
      console.warn(`DNS API skipped (${e.message}) — add record manually in dashboard.`);
    }
  }

  if (!zone) throw new Error(`Zone not found: ${ZONE_NAME}`);

  if (!dnsOk) {
    console.log(`
Manual DNS (Cloudflare → billmaniac.win → DNS):
  Type: CNAME
  Name: feeds
  Target: ${PAGES_TARGET}
  Proxy status: DNS only (grey cloud) — required
`);
  }
  addPagesDomain();

  console.log(`
Next:
  1. npm run deploy
  2. Google Search Console → Domain property billmaniac.win
  3. Delete old sitemap rows
  4. Submit: ${SITEMAP_GSC_URL}
  5. URL Inspection → Test live URL on that address
`);

  await verifyFeed();
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
