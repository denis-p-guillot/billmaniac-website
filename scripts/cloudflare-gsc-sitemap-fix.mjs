#!/usr/bin/env node
/**
 * Create Cloudflare WAF skip rules so Googlebot can fetch /sitemap.xml.
 *
 * Requires an API token with Zone:Firewall Services:Edit on billmaniac.win:
 *   CLOUDFLARE_API_TOKEN=... node scripts/cloudflare-gsc-sitemap-fix.mjs
 *
 * Without a token, prints dashboard steps (Bot Fight Mode is the usual cause of
 * GSC "Sitemap could not be read" while curl with a fake Googlebot UA still works).
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
Google Search Console still shows "Sitemap could not be read" even when the XML
is valid in a browser. On Cloudflare sites this is almost always Bot Fight Mode
blocking real Googlebot (curl with a fake Googlebot user-agent still returns 200).

Do this in the Cloudflare dashboard for ${ZONE_NAME}:

1. Security → Bots → Bot Fight Mode / Super Bot Fight Mode
   • Turn OFF Bot Fight Mode, OR
   • Set "Verified bots" to Allow

2. Security → Events → filter last 24h for path /sitemap.xml
   • If you see Block/Challenge for Googlebot, add a skip rule (step 3)

3. Security → WAF → Custom rules → Create rule
   • Name: Allow verified bots and sitemap feeds
   • Expression:
       (cf.client.bot) or (http.request.uri.path in {"/sitemap.xml" "/sitemap-images.xml" "/robots.txt"})
   • Action: Skip → All remaining custom rules (and Bot Fight Mode if listed)

4. Caching → Configuration → Purge Everything

5. Google Search Console
   • Use property that matches your URLs: https://billmaniac.win/ (or Domain: billmaniac.win)
   • Delete ALL old sitemap rows (sitemap1.xml, sitemap-1.xml, failed attempts)
   • Submit ONLY: https://billmaniac.win/sitemap.xml
   • If URL Inspection Live Test on that URL succeeds, the Sitemaps report may still say
     "could not be read" for days — that queue is separate; status is often stale/pending
   • Also URL-inspect https://billmaniac.win/site-map and Request Indexing (HTML page)

To create the WAF rule automatically, create an API token with
Zone → Firewall Services → Edit for ${ZONE_NAME}, add to .env as:
  CLOUDFLARE_API_TOKEN=...
Then re-run: node scripts/cloudflare-gsc-sitemap-fix.mjs
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
  if (!body.success) {
    throw new Error(JSON.stringify(body.errors || body, null, 2));
  }
  return body.result;
}

async function main() {
  if (!token) {
    dashboardSteps();
    return;
  }

  const zones = await cf(`/zones?name=${ZONE_NAME}&account.id=${ACCOUNT}`);
  const zone = zones.find((z) => z.name === ZONE_NAME) || zones[0];
  if (!zone) throw new Error(`Zone not found: ${ZONE_NAME}`);

  const expression =
    '(cf.client.bot) or (http.request.uri.path in {"/sitemap.xml" "/sitemap-images.xml" "/robots.txt"})';

  const ruleset = await cf(
    `/zones/${zone.id}/rulesets/phases/http_request_firewall_custom/entrypoint`,
  );

  const existing = (ruleset.rules || []).find(
    (r) => r.description === "Allow verified bots and sitemap feeds",
  );
  if (existing) {
    console.log("WAF skip rule already exists.");
  } else {
    await cf(`/zones/${zone.id}/rulesets/${ruleset.id}`, {
      method: "PUT",
      body: JSON.stringify({
        rules: [
          ...(ruleset.rules || []),
          {
            action: "skip",
            action_parameters: {
              ruleset: "current",
            },
            description: "Allow verified bots and sitemap feeds",
            expression,
            enabled: true,
          },
        ],
      }),
    });
    console.log("Created WAF skip rule for verified bots + sitemap paths.");
  }

  console.log("Purge cache in dashboard (Caching → Purge Everything), then resubmit:");
  console.log("  https://billmaniac.win/sitemap.xml");
}

main().catch((err) => {
  console.error(err.message || err);
  dashboardSteps();
  process.exit(1);
});
