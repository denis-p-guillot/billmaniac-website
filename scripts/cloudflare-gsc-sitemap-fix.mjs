#!/usr/bin/env node
/**
 * Fix Google Search Console "Couldn't fetch" for /sitemap.xml on Cloudflare.
 *
 * Root cause: Bot Fight Mode / WAF often blocks real Googlebot (AS15169) while
 * curl with a fake Googlebot user-agent still returns 200.
 *
 * Usage:
 *   npm run gsc:token-check          # verify token permissions first
 *   npm run gsc:cloudflare-fix       # apply ASN whitelist + WAF skip (+ optional bot off)
 *
 * Token: set CLOUDFLARE_WAF_TOKEN in .env (recommended) with:
 *   Zone → Zone WAF → Edit, Zone → Bot Management → Edit (optional),
 *   Zone → Firewall Services → Edit, Zone → Cache Purge → Purge (optional)
 * Scoped to billmaniac.win. See scripts/cloudflare-token-check.mjs for full guide.
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const ZONE_NAME = "billmaniac.win";
const ACCOUNT =
  process.env.CLOUDFLARE_ACCOUNT_ID || "9345927ca3f495f89fdaddea61a5e3f9";

/** Google primary + common cloud crawler ASNs. */
const GOOGLE_ASNS = [
  { asn: "15169", note: "Google LLC (Googlebot / Search Console fetch)" },
  { asn: "396982", note: "Google Cloud (InspectionTool / some crawlers)" },
];

const WAF_SKIP_DESCRIPTION = "Allow verified bots and sitemap feeds";
const WAF_SKIP_EXPRESSION =
  '(cf.client.bot) or (http.request.uri.path in {"/sitemap.xml" "/sitemap-images.xml" "/robots.txt" "/site-map" "/site-map.html"})';
const WAF_SKIP_PHASES = [
  "http_request_firewall_managed",
  "http_request_sbfm",
  "http_ratelimit",
];

const LEGACY_SITEMAP_RULE_NAMES = new Set([
  WAF_SKIP_DESCRIPTION,
  "Google Sitemap",
  "Google Crawler Bot",
]);

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

function tokenSetupGuide() {
  console.log(`
Google Search Console "Couldn't fetch" — token setup

Your current token (${TOKEN_LABEL}) can whitelist Google ASNs but cannot change
Bot Fight Mode or create modern WAF skip rules.

Create a dedicated zone token:
  Dashboard → My Profile → API Tokens → Create Token

Permissions (zone: billmaniac.win):
  • Zone → Zone → Read
  • Zone → Zone WAF → Edit              ← required for sitemap bot bypass
  • Zone → Bot Management → Edit        ← optional (disable Bot Fight via API)
  • Zone → Firewall Services → Edit
  • Zone → Cache Purge → Purge          ← optional

Save as CLOUDFLARE_WAF_TOKEN in .env, then run:
  npm run gsc:token-check
  npm run gsc:cloudflare-fix

Manual dashboard fallback:
1. Security → Bots → Bot Fight Mode → OFF
2. Security → WAF → Custom rules → Skip verified bots + /sitemap.xml paths
3. Caching → Purge Everything
4. GSC → delete failed sitemap → submit https://billmaniac.win/sitemap.xml
`);
}

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

async function ensureGoogleAsnWhitelist(zoneId) {
  const list = await cf(
    `/zones/${zoneId}/firewall/access_rules/rules?per_page=100`,
  );
  if (!list.success) {
    throw new Error(
      `Cannot list access rules: ${list.errors?.[0]?.message || "unknown"}`,
    );
  }

  const existingAsns = new Set(
    (list.result || [])
      .filter((r) => r.configuration?.target === "asn")
      .map((r) => String(r.configuration.value).replace(/^AS/i, "")),
  );

  for (const { asn, note } of GOOGLE_ASNS) {
    if (existingAsns.has(asn)) {
      console.log(`ASN ${asn} already whitelisted.`);
      continue;
    }
    const created = await cf(`/zones/${zoneId}/firewall/access_rules/rules`, {
      method: "POST",
      body: JSON.stringify({
        mode: "whitelist",
        notes: note,
        configuration: { target: "asn", value: asn },
      }),
    });
    if (!created.success) {
      console.warn(
        `Could not whitelist ASN ${asn}: ${created.errors?.[0]?.message || "unknown error"}`,
      );
    } else {
      console.log(`Whitelisted ASN ${asn} (${note}).`);
    }
  }
}

async function consolidateWafSkipRules(zoneId) {
  const rulesetBody = await cf(
    `/zones/${zoneId}/rulesets/phases/http_request_firewall_custom/entrypoint`,
  );
  if (!rulesetBody.success) {
    throw new Error(rulesetBody.errors?.[0]?.message || "rulesets API failed");
  }
  const ruleset = rulesetBody.result;
  const otherRules = (ruleset.rules || []).filter(
    (rule) => !LEGACY_SITEMAP_RULE_NAMES.has(rule.description || ""),
  );

  const skipRule = {
    action: "skip",
    action_parameters: {
      ruleset: "current",
      phases: WAF_SKIP_PHASES,
    },
    description: WAF_SKIP_DESCRIPTION,
    expression: WAF_SKIP_EXPRESSION,
    enabled: true,
  };

  const update = await cf(`/zones/${zoneId}/rulesets/${ruleset.id}`, {
    method: "PUT",
    body: JSON.stringify({
      rules: [skipRule, ...otherRules],
    }),
  });
  if (!update.success) {
    throw new Error(update.errors?.[0]?.message || "ruleset update failed");
  }
  console.log(
    "Consolidated WAF skip rule (first in chain; covers sitemap + verified bots).",
  );
  return true;
}

async function tryDisableBotFightMode(zoneId) {
  const current = await cf(`/zones/${zoneId}/bot_management`);
  if (!current.success) {
    console.warn(
      `Bot Management API unavailable: ${current.errors?.[0]?.message || "no access"}`,
    );
    return false;
  }

  const fightMode = current.result?.fight_mode;
  const sbfm = current.result?.sbfm;
  const enableJs = current.result?.enable_js;
  if (fightMode === false && sbfm?.enabled !== true && enableJs === false) {
    console.log("Bot Fight Mode already off (JS challenge disabled).");
    return true;
  }

  const put = await cf(`/zones/${zoneId}/bot_management`, {
    method: "PUT",
    body: JSON.stringify({
      fight_mode: false,
      enable_js: false,
      ai_bots_protection: current.result?.ai_bots_protection ?? "disabled",
      content_bots_protection: current.result?.content_bots_protection ?? "disabled",
      crawler_protection: current.result?.crawler_protection ?? "disabled",
      cf_robots_variant: current.result?.cf_robots_variant ?? "policy_only",
      ...(sbfm ? { sbfm: { ...sbfm, enabled: false } } : {}),
    }),
  });
  if (!put.success) {
    console.warn(
      `Could not disable JS Detections via API: ${put.errors?.[0]?.message || "unknown"}`,
    );
    console.warn(
      "On Free plan there is often no dashboard toggle — create a zone token with Bot Management Edit and re-run npm run gsc:cloudflare-fix.",
    );
    return false;
  }
  console.log("Disabled JS Detections (enable_js) via API.");
  return true;
}

async function tryPurgeCache(zoneId) {
  const purge = await cf(`/zones/${zoneId}/purge_cache`, {
    method: "POST",
    body: JSON.stringify({ purge_everything: true }),
  });
  if (!purge.success) {
    console.warn(
      `Cache purge skipped: ${purge.errors?.[0]?.message || "no permission"}`,
    );
    return false;
  }
  console.log("Purged Cloudflare cache for billmaniac.win.");
  return true;
}

async function main() {
  if (!token) {
    tokenSetupGuide();
    process.exit(1);
  }

  console.log(`Using ${TOKEN_LABEL} for ${ZONE_NAME}…\n`);

  const zonesBody = await cf(`/zones?name=${ZONE_NAME}&account.id=${ACCOUNT}`);
  if (!zonesBody.success) {
    throw new Error(zonesBody.errors?.[0]?.message || "zone lookup failed");
  }
  const zone =
    zonesBody.result.find((z) => z.name === ZONE_NAME) || zonesBody.result[0];
  if (!zone) throw new Error(`Zone not found: ${ZONE_NAME}`);

  await ensureGoogleAsnWhitelist(zone.id);

  let wafOk = false;
  let botOk = false;
  try {
    wafOk = await consolidateWafSkipRules(zone.id);
  } catch (rulesetError) {
    console.warn(`WAF skip rule failed: ${rulesetError.message}`);
    if (/auth/i.test(rulesetError.message)) {
      console.warn(
        "Missing permission: Zone → Zone WAF → Edit (create CLOUDFLARE_WAF_TOKEN).",
      );
    }
  }

  botOk = await tryDisableBotFightMode(zone.id);
  await tryPurgeCache(zone.id);

  if (!wafOk && !botOk) {
    console.warn("\nBot Fight bypass was not applied via API.");
    tokenSetupGuide();
    process.exit(2);
  }

  console.log("\nDone. In Google Search Console:");
  console.log("  1. Delete failed sitemap rows");
  console.log("  2. Submit: https://billmaniac.win/sitemap.xml");
  console.log("  3. URL Inspection → Live test that URL");
}

main().catch((err) => {
  console.error(err.message || err);
  tokenSetupGuide();
  process.exit(1);
});
