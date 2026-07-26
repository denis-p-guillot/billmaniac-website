import { buildPagesSitemapXml, sitemapResponseHeaders } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD as META_LASTMOD } from "./_sitemap-meta.js";

/** Serves /sitemap1.xml with explicit text/xml headers for Google Search Console. */
export async function onRequestGet(context) {
  const lastmod =
    context.env?.SITEMAP_LASTMOD || META_LASTMOD || new Date().toISOString().slice(0, 10);
  const xml = buildPagesSitemapXml(lastmod);

  return new Response(xml, {
    status: 200,
    headers: sitemapResponseHeaders("pages"),
  });
}
