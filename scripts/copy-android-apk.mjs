#!/usr/bin/env node
/**
 * Upload the latest BillManiac Pro release APK to R2 for /downloads/billmaniac-pro.apk.
 */
import { existsSync, readFileSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || "9345927ca3f495f89fdaddea61a5e3f9";
const BUCKET = process.env.BILLMANIAC_DOWNLOADS_BUCKET || "billmaniac-website-downloads";
const OBJECT_KEY = "billmaniac-pro.apk";
const DEFAULT_SRC = join(
  __dirname,
  "..",
  "..",
  "billmaniac-pro",
  "build",
  "app",
  "outputs",
  "flutter-apk",
  "app-release.apk",
);
const SRC = process.env.BILLMANIAC_APK_SRC || DEFAULT_SRC;
const UPLOAD_URL =
  process.env.BILLMANIAC_APK_UPLOAD_URL || "https://billmaniac.win/api/upload-apk";

function loadEnvFile() {
  for (const name of [".env", ".env.local"]) {
    const path = join(ROOT, name);
    if (!existsSync(path)) continue;
    for (const line of readFileSync(path, "utf8").split("\n")) {
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

if (!existsSync(SRC)) {
  console.error(
    `APK not found at ${SRC}\n` +
      "Build it first: cd ../billmaniac-pro && flutter build apk --release\n" +
      "Or set BILLMANIAC_APK_SRC to the APK path.",
  );
  process.exit(1);
}

function run(cmd, args, { optional = false, oauth = false } = {}) {
  const env = { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT };
  if (oauth) {
    delete env.CLOUDFLARE_API_TOKEN;
    delete env.CF_API_TOKEN;
  }
  const res = spawnSync(cmd, args, {
    cwd: ROOT,
    stdio: "pipe",
    encoding: "utf8",
    env,
  });
  if (res.status !== 0 && !optional) {
    const detail = res.stderr?.trim() || res.stdout?.trim();
    throw new Error(detail || `${cmd} ${args.join(" ")} failed`);
  }
  return res.status === 0;
}

async function uploadViaPagesApi() {
  const secret = process.env.SITEMAP_NOTIFY_SECRET?.trim();
  if (!secret) {
    throw new Error(
      "R2 upload failed and SITEMAP_NOTIFY_SECRET is missing for /api/upload-apk fallback.",
    );
  }

  const body = readFileSync(SRC);
  console.log(`Uploading APK via ${UPLOAD_URL} …`);
  const res = await fetch(UPLOAD_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secret}`,
      "Content-Type": "application/vnd.android.package-archive",
    },
    body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.ok) {
    throw new Error(data.error || `HTTP ${res.status}`);
  }
}

const mb = (statSync(SRC).size / (1024 * 1024)).toFixed(1);
console.log(`Uploading APK (${mb} MB) → r2://${BUCKET}/${OBJECT_KEY}`);

let uploaded = false;
try {
  run(
    "npx",
    ["wrangler", "r2", "bucket", "create", BUCKET],
    { optional: true, oauth: true },
  );

  uploaded = run(
    "npx",
    [
      "wrangler",
      "r2",
      "object",
      "put",
      `${BUCKET}/${OBJECT_KEY}`,
      "--file",
      SRC,
      "--content-type",
      "application/vnd.android.package-archive",
      "--remote",
    ],
    { oauth: true },
  );
} catch (err) {
  console.warn(`Direct R2 upload failed: ${err.message}`);
}

if (!uploaded) {
  await uploadViaPagesApi();
}

console.log(`APK ready at https://billmaniac.win/downloads/billmaniac-pro-v8.apk`);
console.log(`(cache-safe) https://billmaniac.win/downloads/billmaniac-pro.apk?build=8`);
