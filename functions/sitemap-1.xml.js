import { buildPagesSitemapXml, sitemapResponseHeaders } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD as META_LASTMOD } from "./_sitemap-meta.js";

/** Fallback dynamic sitemap (static dist/sitemap-1.xml is preferred for Googlebot). */
export async function onRequestGet(context) {
  const lastmod =
    context.env?.SITEMAP_LASTMOD || META_LASTMOD || new Date().toISOString().slice(0, 10);
  const xml = buildPagesSitemapXml(lastmod);

  return new Response(xml, {
    status: 200,
    headers: sitemapResponseHeaders("pages"),
  });
}
