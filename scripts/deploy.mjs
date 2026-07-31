#!/usr/bin/env node
/**
 * Full website deploy pipeline:
 * 1) regenerate sitemap + IndexNow key file
 * 2) wrangler pages deploy
 * 3) submit sitemap URLs to IndexNow (and optional Bing)
 */
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync, readFileSync } from "node:fs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || "9345927ca3f495f89fdaddea61a5e3f9";

function run(cmd, args, opts = {}) {
  console.log(`\n$ ${cmd} ${args.join(" ")}`);
  const res = spawnSync(cmd, args, {
    cwd: ROOT,
    stdio: "inherit",
    env: { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT },
    ...opts,
  });
  if (res.status !== 0) process.exit(res.status || 1);
}

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

run(process.execPath, [join(ROOT, "scripts/copy-android-apk.mjs")]);
run("python3", [join(ROOT, "scripts/patch-android-download.py")]);
run("python3", [join(ROOT, "scripts/patch-contact-form.py")]);
run("python3", [join(ROOT, "scripts/patch-analytics.py")]);

run(process.execPath, [join(ROOT, "scripts/generate-sitemap.mjs")]);

run("npx", [
  "wrangler",
  "pages",
  "deploy",
  "dist",
  "--project-name=billmaniac-website",
  "--commit-dirty=true",
]);

// Prefer hitting the live notify API after deploy (uses CF secrets).
if ((process.env.SITEMAP_NOTIFY_SECRET || "").trim()) {
  run(process.execPath, [join(ROOT, "scripts/submit-sitemap.mjs"), "--via-api", "--force"]);
} else {
  console.log("\nNo SITEMAP_NOTIFY_SECRET — submitting IndexNow directly from this machine…");
  run(process.execPath, [join(ROOT, "scripts/submit-sitemap.mjs"), "--force"]);
}

console.log("\nDeploy + sitemap notify complete.");
