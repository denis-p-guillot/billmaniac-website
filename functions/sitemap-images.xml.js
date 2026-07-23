import { buildImagesSitemapXml, sitemapResponseHeaders } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD as META_LASTMOD } from "./_sitemap-meta.js";

/** Marketing images for Google Image Search discovery. */
export async function onRequestGet(context) {
  const lastmod =
    context.env?.SITEMAP_LASTMOD || META_LASTMOD || new Date().toISOString().slice(0, 10);
  const xml = buildImagesSitemapXml(lastmod);

  return new Response(xml, {
    status: 200,
    headers: sitemapResponseHeaders("images"),
  });
}
