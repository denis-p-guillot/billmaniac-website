#!/usr/bin/env node
/**
 * Probe which Cloudflare API capabilities the current token has.
 *
 * Usage:
 *   node scripts/cloudflare-token-check.mjs
 *   CLOUDFLARE_WAF_TOKEN=... node scripts/cloudflare-token-check.mjs
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const ZONE_NAME = "billmaniac.win";
const ACCOUNT =
  process.env.CLOUDFLARE_ACCOUNT_ID || "9345927ca3f495f89fdaddea61a5e3f9";

function loadEnvFile() {
  const envPath = join(ROOT, ".env");
  if (!existsSync(envPath)) return;
  for (const line of readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
    const i = trimmed.indexOf("=");
    const k = trimmed.slice(0, i).trim();
    let v = trimmed.slice(i + 1).trim();
    if (
      (v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'"))
    ) {
      v = v.slice(1, -1);
    }
    if (!(k in process.env)) process.env[k] = v;
  }
}

loadEnvFile();

const token = (
  process.env.CLOUDFLARE_WAF_TOKEN ||
  process.env.CLOUDFLARE_SETUP_TOKEN ||
  process.env.CLOUDFLARE_API_TOKEN ||
  ""
).trim();

const TOKEN_LABEL = process.env.CLOUDFLARE_WAF_TOKEN
  ? "CLOUDFLARE_WAF_TOKEN"
  : process.env.CLOUDFLARE_SETUP_TOKEN
    ? "CLOUDFLARE_SETUP_TOKEN"
    : "CLOUDFLARE_API_TOKEN";

async function cf(path, init = {}) {
  const res = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  return res.json();
}

function status(ok, detail = "") {
  return ok ? `OK${detail ? ` — ${detail}` : ""}` : `FAIL${detail ? ` — ${detail}` : ""}`;
}

function printTokenSetupGuide() {
  console.log(`
Create a dedicated zone token for GSC / Bot Fight fixes:

1. Cloudflare dashboard → My Profile → API Tokens → Create Token
2. Use template "Edit zone DNS" as a starting point, then customize:

   Permissions (zone-scoped to billmaniac.win):
   • Zone → Zone → Read
   • Zone → Firewall Services → Edit        (legacy IP access rules)
   • Zone → Zone WAF → Edit                  (modern WAF skip rule — required)
   • Zone → Bot Management → Edit            (optional: disable Bot Fight via API)
   • Zone → Cache Purge → Purge              (optional: auto-purge after fix)

   Zone Resources:
   • Include → Specific zone → billmaniac.win

3. Save the token to .env as:
   CLOUDFLARE_WAF_TOKEN=your_token_here

   Keep CLOUDFLARE_API_TOKEN for deploy/scripts that only need Pages/R2.
   The GSC fix script prefers CLOUDFLARE_WAF_TOKEN when set.

4. Verify:
   npm run gsc:token-check
   npm run gsc:cloudflare-fix
`);
}

async function main() {
  if (!token) {
    console.error("No token found. Set CLOUDFLARE_WAF_TOKEN or CLOUDFLARE_API_TOKEN in .env");
    printTokenSetupGuide();
    process.exit(1);
  }

  console.log(`Checking ${TOKEN_LABEL} against zone ${ZONE_NAME}…\n`);

  const verify = await cf("/user/tokens/verify", { method: "GET" });
  console.log(
    `Token verify: ${status(verify.success, verify.result?.status || verify.errors?.[0]?.message)}`,
  );

  const zonesBody = await cf(`/zones?name=${ZONE_NAME}&account.id=${ACCOUNT}`);
  const zone =
    zonesBody.result?.find((z) => z.name === ZONE_NAME) || zonesBody.result?.[0];
  console.log(
    `Zone lookup: ${status(zonesBody.success && zone, zone ? zone.id : zonesBody.errors?.[0]?.message)}`,
  );
  if (!zone) {
    printTokenSetupGuide();
    process.exit(1);
  }

  const accessRules = await cf(
    `/zones/${zone.id}/firewall/access_rules/rules?per_page=5`,
  );
  console.log(
    `Firewall access rules (read): ${status(accessRules.success, accessRules.errors?.[0]?.message)}`,
  );

  const ruleset = await cf(
    `/zones/${zone.id}/rulesets/phases/http_request_firewall_custom/entrypoint`,
  );
  console.log(
    `Zone WAF rulesets (read/write): ${status(ruleset.success, ruleset.errors?.[0]?.message)}`,
  );

  const botMgmt = await cf(`/zones/${zone.id}/bot_management`);
  const botDetail = botMgmt.success
    ? `fight_mode=${botMgmt.result?.fight_mode ?? "?"}`
    : botMgmt.errors?.[0]?.message;
  console.log(`Bot Management (read): ${status(botMgmt.success, botDetail)}`);

  const purgeProbe = await cf(`/zones/${zone.id}/purge_cache`, {
    method: "POST",
    body: JSON.stringify({ purge_everything: false, files: [] }),
  });
  const purgeOk =
    purgeProbe.success ||
    purgeProbe.errors?.[0]?.message?.includes("must purge");
  console.log(
    `Cache purge: ${status(purgeOk, purgeProbe.errors?.[0]?.message || "reachable")}`,
  );

  const canFixGsc = ruleset.success || botMgmt.success;
  console.log("");
  if (canFixGsc) {
    console.log("This token can run: npm run gsc:cloudflare-fix");
  } else {
    console.log("This token cannot create WAF skip rules or change Bot Fight Mode.");
    printTokenSetupGuide();
    process.exit(2);
  }
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
