#!/usr/bin/env node
/**
 * Upload the latest BillManiac Pro release APK to R2 for /downloads/billmaniac-pro.apk.
 */
import { existsSync, statSync } from "node:fs";
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

if (!existsSync(SRC)) {
  console.error(
    `APK not found at ${SRC}\n` +
      "Build it first: cd ../billmaniac-pro && flutter build apk --release\n" +
      "Or set BILLMANIAC_APK_SRC to the APK path.",
  );
  process.exit(1);
}

function run(cmd, args, { optional = false } = {}) {
  const res = spawnSync(cmd, args, {
    cwd: ROOT,
    stdio: "inherit",
    env: { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT },
  });
  if (res.status !== 0 && !optional) process.exit(res.status || 1);
}

const mb = (statSync(SRC).size / (1024 * 1024)).toFixed(1);
console.log(`Uploading APK (${mb} MB) → r2://${BUCKET}/${OBJECT_KEY}`);

run(
  "npx",
  ["wrangler", "r2", "bucket", "create", BUCKET],
  { optional: true },
);

run("npx", [
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
]);

console.log(`APK ready at https://billmaniac.win/downloads/${OBJECT_KEY}`);
