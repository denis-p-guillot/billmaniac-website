import { buildPagesSitemapXml } from "./sitemap-lib.js";
import { SITEMAP_LASTMOD } from "./_sitemap-meta.js";

const HEADERS = {
  "Content-Type": "application/xml; charset=UTF-8",
  "Cache-Control": "no-store, must-revalidate",
  "CDN-Cache-Control": "no-store",
  "Accept-Ranges": "bytes",
};

/** Serve /sitemap.xml at the edge with explicit XML headers for crawlers. */
export async function onRequest(context) {
  const xml = buildPagesSitemapXml(SITEMAP_LASTMOD);
  const bytes = new TextEncoder().encode(xml);
  const headers = {
    ...HEADERS,
    "Content-Length": String(bytes.byteLength),
  };

  if (context.request.method === "HEAD") {
    return new Response(null, { status: 200, headers });
  }

  return new Response(xml, { status: 200, headers });
}
