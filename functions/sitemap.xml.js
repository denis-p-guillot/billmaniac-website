import { buildPagesSitemapXml } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD } from "./_sitemap-meta.js";

/** Serve /sitemap.xml at the edge with explicit XML headers for crawlers. */
export async function onRequest() {
  const xml = buildPagesSitemapXml(SITEMAP_LASTMOD);
  return new Response(xml, {
    status: 200,
    headers: {
      "Content-Type": "application/xml; charset=UTF-8",
      "Cache-Control": "no-store, must-revalidate",
      "CDN-Cache-Control": "no-store",
      "X-Robots-Tag": "noindex",
    },
  });
}
