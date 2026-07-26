import {
  DEFAULT_OG_IMAGE,
  SITE_ORIGIN,
  SEO_PAGES,
  getSeoForPath,
  isIndexablePath,
  normalizePath,
} from "./seo-config.js";
import { SITE_LANGUAGES, buildStructuredData } from "./seo-schema.js";

const ASSET_EXT =
  /\.(xml|txt|json|js|mjs|cjs|ts|tsx|jsx|css|png|jpe?g|gif|webp|svg|ico|woff2?|map|webmanifest|apk|aab)$/i;

const SITEMAP_PATHS = new Set([
  "/sitemap-1.xml",
  "/sitemap-images.xml",
]);

function upsertMetaByName(html, name, content) {
  const re = new RegExp(
    `<meta\\s+name=["']${name}["']\\s+content=["'][^"']*["']\\s*/?>`,
    "i",
  );
  const tag = `<meta name="${name}" content="${escapeAttr(content)}">`;
  if (re.test(html)) return html.replace(re, tag);
  return html.replace(/<\/head>/i, `    ${tag}\n</head>`);
}

function upsertMetaByProperty(html, property, content) {
  const re = new RegExp(
    `<meta\\s+(?:property|name)=["']${property}["']\\s+content=["'][^"']*["']\\s*/?>`,
    "i",
  );
  const tag = `<meta property="${property}" content="${escapeAttr(content)}">`;
  if (re.test(html)) return html.replace(re, tag);
  return html.replace(/<\/head>/i, `    ${tag}\n</head>`);
}

function injectOgLocales(html) {
  let out = html.replace(
    /<meta\s+(?:property|name)=["']og:locale(?::alternate)?["'][^>]*>\s*/gi,
    "",
  );
  const tags = [
    `<meta property="og:locale" content="en_US">`,
    `<meta property="og:locale:alternate" content="fr_FR">`,
    `<meta property="og:locale:alternate" content="es_ES">`,
  ];
  return out.replace(/<\/head>/i, `    ${tags.join("\n    ")}\n</head>`);
}

function upsertCanonical(html, href) {
  const re = /<link\s+rel=["']canonical["']\s+href=["'][^"']*["']\s*\/?>/i;
  const tag = `<link rel="canonical" href="${escapeAttr(href)}" />`;
  if (re.test(html)) return html.replace(re, tag);
  return html.replace(/<\/head>/i, `    ${tag}\n</head>`);
}

function upsertTitle(html, title) {
  if (/<title>[^<]*<\/title>/i.test(html)) {
    return html.replace(/<title>[^<]*<\/title>/i, `<title>${escapeHtml(title)}</title>`);
  }
  return html.replace(/<\/head>/i, `    <title>${escapeHtml(title)}</title>\n</head>`);
}

function removeStructuredData(html) {
  return html.replace(
    /<script\s+type=["']application\/ld\+json["'][^>]*>[\s\S]*?<\/script>\s*/gi,
    "",
  );
}

function injectStructuredData(html, pathname) {
  const payload = JSON.stringify(buildStructuredData(pathname), null, 2);
  const tag = `<script type="application/ld+json" data-billmaniac-seo="1">\n${payload}\n    </script>`;
  return html.replace(/<\/head>/i, `    ${tag}\n</head>`);
}

function injectHreflang(html, url) {
  let out = html;
  for (const lang of SITE_LANGUAGES) {
    const re = new RegExp(
      `<link\\s+rel=["']alternate["']\\s+hreflang=["']${lang}["'][^>]*>`,
      "i",
    );
    const tag = `<link rel="alternate" hreflang="${lang}" href="${escapeAttr(url)}" />`;
    out = re.test(out)
      ? out.replace(re, tag)
      : out.replace(/<\/head>/i, `    ${tag}\n</head>`);
  }

  const xDefaultRe =
    /<link\s+rel=["']alternate["']\s+hreflang=["']x-default["'][^>]*>/i;
  const xDefaultTag = `<link rel="alternate" hreflang="x-default" href="${escapeAttr(url)}" />`;
  out = xDefaultRe.test(out)
    ? out.replace(xDefaultRe, xDefaultTag)
    : out.replace(/<\/head>/i, `    ${xDefaultTag}\n</head>`);

  return out;
}

function escapeAttr(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function applySeo(html, seo, pathname) {
  const url = `${SITE_ORIGIN}${seo.path === "/" ? "/" : seo.path}`;
  const image = DEFAULT_OG_IMAGE;
  const indexable = isIndexablePath(pathname);
  const robots = indexable
    ? "index, follow, max-image-preview:large"
    : "noindex, follow";

  let out = html;
  out = upsertTitle(out, seo.title);
  out = upsertMetaByName(out, "description", seo.description);
  if (seo.keywords) {
    out = upsertMetaByName(out, "keywords", seo.keywords);
  }
  out = upsertMetaByName(out, "robots", robots);
  out = upsertCanonical(out, url);
  out = injectHreflang(out, url);
  out = upsertMetaByProperty(out, "og:type", "website");
  out = upsertMetaByProperty(out, "og:url", url);
  out = upsertMetaByProperty(out, "og:title", seo.title);
  out = upsertMetaByProperty(out, "og:description", seo.description);
  out = upsertMetaByProperty(out, "og:image", image);
  out = upsertMetaByProperty(out, "og:site_name", "Bill Maniac");
  out = injectOgLocales(out);
  out = upsertMetaByProperty(out, "twitter:card", "summary_large_image");
  out = upsertMetaByProperty(out, "twitter:url", url);
  out = upsertMetaByProperty(out, "twitter:title", seo.title);
  out = upsertMetaByProperty(out, "twitter:description", seo.description);
  out = upsertMetaByProperty(out, "twitter:image", image);
  out = removeStructuredData(out);
  out = injectStructuredData(out, pathname);
  return out;
}

function isHtmlResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("text/html");
}

async function loadIndexHtml(context) {
  const { request, env, next } = context;
  const indexUrl = new URL("/index.html", request.url);

  if (env && env.ASSETS) {
    const assetResponse = await env.ASSETS.fetch(indexUrl);
    if (assetResponse.ok) return assetResponse;
  }

  const viaNext = await next(new Request(indexUrl.toString(), request));
  if (viaNext.ok && isHtmlResponse(viaNext)) return viaNext;

  return fetch(new URL("/", request.url).toString(), {
    headers: { accept: "text/html" },
  });
}

export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);
  const path = normalizePath(url.pathname);

  if (path === "/index.tsx" || path === "/index.ts" || path === "/main.tsx") {
    return new Response("/* legacy entry disabled; use importmap @/index */\n", {
      status: 200,
      headers: { "content-type": "text/javascript; charset=utf-8", "cache-control": "no-store" },
    });
  }

  if (
    ASSET_EXT.test(path) ||
    path.startsWith("/pics/") ||
    path.startsWith("/cdn-cgi/") ||
    path.startsWith("/api/") ||
    url.pathname.startsWith("/api/") ||
    SITEMAP_PATHS.has(path)
  ) {
    return next();
  }

  if (url.pathname !== "/" && url.pathname.endsWith("/")) {
    const bare = normalizePath(url.pathname);
    if (SEO_PAGES[bare]) {
      const dest = new URL(bare, url.origin);
      dest.search = url.search;
      return Response.redirect(dest.toString(), 301);
    }
  }

  const isKnownSeoPath = Boolean(SEO_PAGES[path]);

  let response;
  if (isKnownSeoPath && path !== "/") {
    response = await loadIndexHtml(context);
  } else {
    response = await next();
    if (
      isKnownSeoPath &&
      (!response.ok || response.status >= 300) &&
      path === "/"
    ) {
      response = await loadIndexHtml(context);
    }
  }

  if (!isHtmlResponse(response)) {
    return response;
  }

  const seo = getSeoForPath(path);
  const html = await response.text();
  const patched = applySeo(html, seo, path);

  const headers = new Headers(response.headers);
  headers.set("content-type", "text/html; charset=utf-8");
  headers.delete("location");
  headers.set("vary", "Accept");
  headers.set("x-billmaniac-seo-path", seo.path);
  headers.set("cache-control", "public, max-age=0, must-revalidate");

  return new Response(patched, {
    status: 200,
    headers,
  });
}
