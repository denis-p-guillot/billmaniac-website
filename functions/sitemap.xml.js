import { buildSitemapXml } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD as META_LASTMOD } from "./_sitemap-meta.js";

/** Dynamic sitemap — always mirrors functions/seo-config.js */
export async function onRequestGet(context) {
  const lastmod =
    context.env?.SITEMAP_LASTMOD || META_LASTMOD || new Date().toISOString().slice(0, 10);
  const xml = buildSitemapXml(lastmod);

  return new Response(xml, {
    status: 200,
    headers: {
      "content-type": "application/xml; charset=utf-8",
      "cache-control": "public, max-age=3600, must-revalidate",
      "x-billmaniac-sitemap": "dynamic",
    },
  });
}
