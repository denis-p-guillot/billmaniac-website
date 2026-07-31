#!/usr/bin/env node
/**
 * Fix Google Search Console "Couldn't fetch" for /sitemap.xml on Cloudflare.
 *
 * Root cause: Bot Fight Mode / WAF often blocks real Googlebot (AS15169) while
 * curl with a fake Googlebot user-agent still returns 200.
 *
 * This script whitelists Google ASNs via IP Access Rules (works with limited tokens).
 * For Bot Fight Mode you still need the dashboard step below OR a token with
 * Zone → Firewall Services → Edit to create modern WAF skip rules.
 *
 *   CLOUDFLARE_API_TOKEN=... node scripts/cloudflare-gsc-sitemap-fix.mjs
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

const token = (process.env.CLOUDFLARE_API_TOKEN || "").trim();

function dashboardSteps() {
  console.log(`
Google Search Console "Couldn't fetch" on Cloudflare — required dashboard steps:

1. Security → Bots → Bot Fight Mode
   • Turn OFF Bot Fight Mode (most common fix for Cloudflare Pages + GSC)
   • Legacy firewall "skip" rules do NOT bypass Bot Fight Mode

2. Security → WAF → Custom rules → Create rule (if Bot Fight stays on)
   • Name: Allow verified bots and sitemap feeds
   • Expression:
       (cf.client.bot) or (http.request.uri.path in {"/sitemap.xml" "/sitemap-images.xml" "/robots.txt" "/site-map"})
   • Action: Skip → Super Bot Fight Mode + all WAF phases

3. Security → Events → filter path /sitemap.xml → confirm no Block/Challenge for Google

4. Caching → Purge Everything

5. Google Search Console (property: https://billmaniac.win/)
   • Delete failed sitemap rows
   • Submit ONLY: https://billmaniac.win/sitemap.xml  (no trailing slash)
   • URL Inspection → Live test on that exact URL

To auto-whitelist Google ASNs, set CLOUDFLARE_API_TOKEN in .env and re-run.
For WAF custom rules, the token also needs Zone → Firewall Services → Edit.
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
  const body = await res.json();
  return body;
}

async function ensureGoogleAsnWhitelist(zoneId) {
  const list = await cf(
    `/zones/${zoneId}/firewall/access_rules/rules?per_page=100`,
  );
  if (!list.success) {
    throw new Error(
      `Cannot list access rules: ${JSON.stringify(list.errors || list)}`,
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

async function listLegacyFirewallRules(zoneId) {
  const body = await cf(`/zones/${zoneId}/firewall/rules?per_page=50`);
  if (!body.success) return null;
  return body.result || [];
}

function reportExistingLegacyRules(rules) {
  const sitemapRules = rules.filter((rule) => {
    const expr = rule.filter?.expression || "";
    return (
      /sitemap|robots\.txt|cf\.client\.bot/i.test(expr) &&
      rule.action === "skip"
    );
  });
  if (sitemapRules.length === 0) return false;
  console.log("Found legacy firewall skip rules (do not bypass Bot Fight Mode):");
  for (const rule of sitemapRules) {
    console.log(`  • ${rule.description}: ${rule.filter?.expression}`);
  }
  return true;
}

async function tryModernWafSkipRule(zoneId) {
  const expression =
    '(cf.client.bot) or (http.request.uri.path in {"/sitemap.xml" "/sitemap-images.xml" "/robots.txt" "/site-map" "/site-map.html"})';
  const skipPhases = [
    "http_request_firewall_managed",
    "http_request_sbfm",
    "http_rate_limit",
    "http_request_firewall_custom",
  ];

  const rulesetBody = await cf(
    `/zones/${zoneId}/rulesets/phases/http_request_firewall_custom/entrypoint`,
  );
  if (!rulesetBody.success) {
    throw new Error(rulesetBody.errors?.[0]?.message || "rulesets API failed");
  }
  const ruleset = rulesetBody.result;
  const existing = (ruleset.rules || []).find(
    (r) => r.description === "Allow verified bots and sitemap feeds",
  );
  if (existing) {
    console.log("Modern WAF skip rule already exists.");
    return;
  }

  const update = await cf(`/zones/${zoneId}/rulesets/${ruleset.id}`, {
    method: "PUT",
    body: JSON.stringify({
      rules: [
        ...(ruleset.rules || []),
        {
          action: "skip",
          action_parameters: {
            ruleset: "current",
            phases: skipPhases,
          },
          description: "Allow verified bots and sitemap feeds",
          expression,
          enabled: true,
        },
      ],
    }),
  });
  if (!update.success) {
    throw new Error(update.errors?.[0]?.message || "ruleset update failed");
  }
  console.log("Created modern WAF skip rule (includes Super Bot Fight Mode).");
}

async function main() {
  if (!token) {
    dashboardSteps();
    return;
  }

  const zonesBody = await cf(`/zones?name=${ZONE_NAME}&account.id=${ACCOUNT}`);
  if (!zonesBody.success) {
    throw new Error(JSON.stringify(zonesBody.errors || zonesBody));
  }
  const zone =
    zonesBody.result.find((z) => z.name === ZONE_NAME) || zonesBody.result[0];
  if (!zone) throw new Error(`Zone not found: ${ZONE_NAME}`);

  await ensureGoogleAsnWhitelist(zone.id);

  try {
    await tryModernWafSkipRule(zone.id);
  } catch (rulesetError) {
    console.warn(`Modern WAF rulesets API unavailable: ${rulesetError.message}`);
    const legacy = await listLegacyFirewallRules(zone.id);
    if (legacy) reportExistingLegacyRules(legacy);
    console.warn(
      "\nTurn OFF Bot Fight Mode manually: Security → Bots → Bot Fight Mode → OFF",
    );
  }

  console.log("\nNext: purge cache in Cloudflare dashboard, then in GSC resubmit:");
  console.log("  https://billmaniac.win/sitemap.xml");
}

main().catch((err) => {
  console.error(err.message || err);
  dashboardSteps();
  process.exit(1);
});
