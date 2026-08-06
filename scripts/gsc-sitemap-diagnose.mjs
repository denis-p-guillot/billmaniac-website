#!/usr/bin/env node
/**
 * Diagnose why Google Search Console may report "Sitemap could not be read".
 * Run: npm run gsc:diagnose
 */
const SITEMAP = "https://billmaniac.win/sitemap.xml";
const APEX = "https://billmaniac.win";
const WWW = "https://www.billmaniac.win";

const CHECKS = [
  { label: "Googlebot desktop", ua: "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" },
  { label: "Google InspectionTool", ua: "Google-InspectionTool/1.0" },
  { label: "Google Site Verification", ua: "Mozilla/5.0 (compatible; Google-Site-Verification/1.0)" },
  { label: "Generic browser", ua: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
];

async function probe(url, ua) {
  const res = await fetch(url, {
    headers: ua ? { "User-Agent": ua, Accept: "application/xml,text/xml,*/*" } : {},
    redirect: "follow",
  });
  const ct = res.headers.get("content-type") || "";
  const body = (await res.text()).slice(0, 120);
  const xml = body.startsWith("<?xml") || body.includes("<urlset");
  return { status: res.status, ct, xml, body: body.replace(/\s+/g, " ").trim() };
}

function parseLocs(xmlText) {
  return [...xmlText.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
}

async function main() {
  console.log(`\nGSC sitemap diagnose — ${SITEMAP}\n`);

  for (const { label, ua } of CHECKS) {
    try {
      const r = await probe(SITEMAP, ua);
      const ok = r.status === 200 && r.xml;
      console.log(`${ok ? "✓" : "✗"} ${label}: HTTP ${r.status}, ${r.ct}${ok ? "" : ` — ${r.body}`}`);
    } catch (e) {
      console.log(`✗ ${label}: ${e.message}`);
    }
  }

  const apexHome = await probe(`${APEX}/`, CHECKS[0].ua);
  const wwwHome = await probe(`${WWW}/`, CHECKS[0].ua);
  console.log(`\nwww → apex redirect: ${wwwHome.status === 301 || wwwHome.status === 308 ? "yes" : "NO (www returns " + wwwHome.status + " — fix in Cloudflare)"}`);

  const sm = await fetch(SITEMAP, { headers: { "User-Agent": CHECKS[0].ua } });
  const xml = await sm.text();
  const locs = parseLocs(xml);
  const hosts = [...new Set(locs.map((u) => u.match(/^https?:\/\/[^/]+/)[0]))];
  console.log(`\nSitemap URLs: ${locs.length}`);
  console.log(`Hosts in <loc>: ${hosts.join(", ")}`);

  try {
    const feeds = await fetch("https://feeds.billmaniac.win/sitemap.xml", {
      headers: { "User-Agent": CHECKS[0].ua },
    });
    console.log(`feeds.billmaniac.win: HTTP ${feeds.status}`);
  } catch {
    console.log("feeds.billmaniac.win: DNS missing — do NOT submit this URL in GSC");
  }

  console.log(`
Most common GSC cause when the sitemap returns HTTP 200:
  • Wrong Search Console property (www vs non-www URL prefix)
  • Sitemap submitted under a different property than you are viewing

Use ONE of these in Search Console:
  ✓ Domain property: billmaniac.win
  ✓ URL prefix:      ${APEX}/   (not www unless you redirect www → apex)

Then:
  1. Delete all old sitemap rows in Sitemaps
  2. Submit exactly: ${SITEMAP}  (no trailing slash)
  3. URL Inspection → paste sitemap URL → Live test → expect "Page fetch: Successful"

Cloudflare dashboard (manual):
  Security → Bots → turn OFF "JS Detections" (enable_js)
  Rules → Redirect Rules → www.billmaniac.win → ${APEX}$1 (301)
`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
