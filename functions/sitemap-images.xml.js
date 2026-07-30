import { buildImagesSitemapXml } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD } from "./_sitemap-meta.js";

/** Serve /sitemap-images.xml at the edge with explicit XML headers. */
export async function onRequest() {
  const xml = buildImagesSitemapXml(SITEMAP_LASTMOD);
  return new Response(xml, {
    status: 200,
    headers: {
      "Content-Type": "application/xml; charset=UTF-8",
      "Cache-Control": "no-store, must-revalidate",
      "CDN-Cache-Control": "no-store",
    },
  });
}
