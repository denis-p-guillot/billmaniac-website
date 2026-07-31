import {
  SITE_ORIGIN,
  SITEMAP_IMAGES_URL,
  SITEMAP_PAGES_URL,
  listIndexablePages,
} from "./seo-config.js";

const SITEMAP_IMAGE_RE = /\.(jpe?g|png|gif|webp)$/i;

function rasterImages(images) {
  return (images || []).filter((url) => SITEMAP_IMAGE_RE.test(url));
}

/** @param {string} [isoDate] YYYY-MM-DD */
export function todayYmd(isoDate) {
  if (isoDate && /^\d{4}-\d{2}-\d{2}$/.test(isoDate)) return isoDate;
  return new Date().toISOString().slice(0, 10);
}

export function listSitemapEntries(lastmod) {
  const mod = todayYmd(lastmod);
  return listIndexablePages()
    .slice()
    .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0) || a.path.localeCompare(b.path))
    .map((page) => ({
      loc: page.path === "/" ? `${SITE_ORIGIN}/` : `${SITE_ORIGIN}${page.path}`,
      lastmod: mod,
      changefreq: page.changefreq || "monthly",
      priority: typeof page.priority === "number" ? page.priority : 0.5,
      images: page.images || [],
    }));
}

export function buildPagesSitemapXml(lastmod) {
  const entries = listSitemapEntries(lastmod);
  const body = entries
    .map(
      (e) => `  <url>
    <loc>${escapeXml(e.loc)}</loc>
    <lastmod>${e.lastmod}</lastmod>
    <changefreq>${escapeXml(e.changefreq)}</changefreq>
    <priority>${Number(e.priority).toFixed(1)}</priority>
  </url>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`;
}

export function buildImagesSitemapXml(lastmod) {
  const mod = todayYmd(lastmod);
  const pages = listIndexablePages().filter((page) => rasterImages(page.images).length > 0);

  const body = pages
    .map((page) => {
      const pageUrl = page.path === "/" ? `${SITE_ORIGIN}/` : `${SITE_ORIGIN}${page.path}`;
      const imageTags = rasterImages(page.images)
        .map(
          (imageUrl) => `    <image:image>
      <image:loc>${escapeXml(imageUrl)}</image:loc>
    </image:image>`,
        )
        .join("\n");

      return `  <url>
    <loc>${escapeXml(pageUrl)}</loc>
    <lastmod>${mod}</lastmod>
${imageTags}
  </url>`;
    })
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
${body}
</urlset>
`;
}

export function buildSitemapIndexXml(lastmod) {
  const mod = todayYmd(lastmod);
  const sitemaps = [
    { loc: SITEMAP_PAGES_URL, lastmod: mod },
    { loc: SITEMAP_IMAGES_URL, lastmod: mod },
  ];

  const body = sitemaps
    .map(
      (entry) => `  <sitemap>
    <loc>${escapeXml(entry.loc)}</loc>
    <lastmod>${entry.lastmod}</lastmod>
  </sitemap>`,
    )
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${body}
</sitemapindex>
`;
}

/** Back-compat alias used by notify API previews. */
export function buildSitemapXml(lastmod) {
  return buildSitemapIndexXml(lastmod);
}

function escapeXml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function sitemapResponseHeaders(label) {
  return {
    "content-type": "application/xml; charset=UTF-8",
    "cache-control": "no-store, must-revalidate",
    "cdn-cache-control": "no-store",
    "x-billmaniac-sitemap": label,
  };
}

/**
 * Submit URL list to IndexNow (Bing, Yandex, Seznam, Naver, …).
 * @see https://www.indexnow.org/documentation
 */
export async function submitIndexNow({ host, key, keyLocation, urlList, fetchImpl = fetch }) {
  if (!key) throw new Error("INDEXNOW_KEY is required");
  if (!Array.isArray(urlList) || urlList.length === 0) {
    return { ok: true, skipped: true, reason: "empty urlList" };
  }

  const payload = {
    host,
    key,
    keyLocation: keyLocation || `https://${host}/${key}.txt`,
    urlList: urlList.slice(0, 10000),
  };

  const res = await fetchImpl("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "content-type": "application/json; charset=utf-8" },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  const ok = res.status === 200 || res.status === 202 || res.status === 429;
  return {
    ok,
    rateLimited: res.status === 429,
    status: res.status,
    body: text.slice(0, 500),
    submitted: payload.urlList.length,
  };
}

export async function submitBingSitemapFeed({
  apiKey,
  siteUrl = SITE_ORIGIN,
  feedUrl = SITEMAP_PAGES_URL,
  fetchImpl = fetch,
}) {
  if (!apiKey) return { ok: true, skipped: true, reason: "BING_WEBMASTER_API_KEY not set" };

  const endpoint = new URL("https://ssl.bing.com/webmaster/api.svc/json/SubmitFeed");
  endpoint.searchParams.set("apikey", apiKey);
  endpoint.searchParams.set("siteUrl", siteUrl);
  endpoint.searchParams.set("feedUrl", feedUrl);

  const res = await fetchImpl(endpoint.toString(), { method: "GET" });
  const text = await res.text();
  return {
    ok: res.ok,
    status: res.status,
    body: text.slice(0, 500),
  };
}

export async function submitGoogleSitemapPing({
  feedUrl = SITEMAP_PAGES_URL,
  pingUrl,
  fetchImpl = fetch,
}) {
  if (!pingUrl) {
    return {
      ok: true,
      skipped: true,
      reason:
        `Google anonymous sitemap ping is deprecated; submit ${SITEMAP_PAGES_URL} manually in Google Search Console`,
    };
  }
  const url = pingUrl.includes("{sitemap}")
    ? pingUrl.replace("{sitemap}", encodeURIComponent(feedUrl))
    : `${pingUrl}${pingUrl.includes("?") ? "&" : "?"}sitemap=${encodeURIComponent(feedUrl)}`;
  const res = await fetchImpl(url, { method: "GET" });
  const text = await res.text();
  return { ok: res.ok, status: res.status, body: text.slice(0, 500) };
}

export async function notifySearchEngines(env, { lastmod } = {}) {
  const host = new URL(SITE_ORIGIN).host;
  const key = env.INDEXNOW_KEY;
  const entries = listSitemapEntries(lastmod || env.SITEMAP_LASTMOD);
  const urlList = entries.map((e) => e.loc);
  const sitemapUrl = SITEMAP_PAGES_URL;
  const fingerprint = `${urlList.join("|")}|${entries[0]?.lastmod || ""}`;

  const indexNow = key
    ? await submitIndexNow({
        host,
        key,
        keyLocation: `${SITE_ORIGIN}/${key}.txt`,
        urlList,
      })
    : { ok: false, skipped: true, reason: "INDEXNOW_KEY not set" };

  const bing = await submitBingSitemapFeed({
    apiKey: env.BING_WEBMASTER_API_KEY,
    siteUrl: SITE_ORIGIN,
    feedUrl: sitemapUrl,
  });

  const google = await submitGoogleSitemapPing({
    feedUrl: sitemapUrl,
    pingUrl: env.GOOGLE_SITEMAP_PING_URL,
  });

  const indexNowAccepted =
    indexNow.ok || indexNow.skipped || indexNow.status === 429 || indexNow.status === 202;

  return {
    ok: Boolean(indexNowAccepted) && Boolean(bing.ok || bing.skipped),
    fingerprint,
    sitemapUrl,
    sitemapPagesUrl: SITEMAP_PAGES_URL,
    sitemapImagesUrl: SITEMAP_IMAGES_URL,
    urlCount: urlList.length,
    lastmod: entries[0]?.lastmod,
    indexNow,
    bing,
    google,
  };
}
