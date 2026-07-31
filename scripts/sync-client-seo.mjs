#!/usr/bin/env node
/**
 * Sync merged SEO_PAGES from functions/seo-config.js into client @/seo module.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const INDEX = join(ROOT, "dist/index.html");
const GA_ID = process.env.GA_MEASUREMENT_ID || "G-FY5RTLMWZ9";

function jsString(value) {
  return JSON.stringify(value);
}

function buildClientSeoModule(pages) {
  const entries = Object.entries(pages)
    .map(([path, page]) => {
      const fields = [
        `title: ${jsString(page.title)}`,
        `description: ${jsString(page.description)}`,
        `path: ${jsString(page.path)}`,
        `pageKey: ${jsString(page.pageKey)}`,
      ];
      if (page.scrollTo) fields.push(`scrollTo: ${jsString(page.scrollTo)}`);
      return `  ${jsString(path)}: {\n    ${fields.join(",\n    ")},\n  }`;
    })
    .join(",\n");

  return `
const SITE_ORIGIN = 'https://billmaniac.win';
const DEFAULT_OG_IMAGE = \`\${SITE_ORIGIN}/pics/og-cover.jpg\`;

export const SEO_PAGES = {
${entries}
};

export function normalizePath(pathname) {
  if (!pathname || pathname === '/') return '/';
  const trimmed = pathname.replace(/\\/+$/, '');
  return trimmed || '/';
}

export function getSeoForPath(pathname) {
  const path = normalizePath(pathname);
  return SEO_PAGES[path] || SEO_PAGES['/'];
}

function setMetaName(name, content) {
  let el = document.querySelector(\`meta[name="\${name}"]\`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute('name', name);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function setMetaProperty(property, content) {
  let el = document.querySelector(\`meta[property="\${property}"]\`) || document.querySelector(\`meta[name="\${property}"]\`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute('property', property);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function setCanonical(href) {
  let el = document.querySelector('link[rel="canonical"]');
  if (!el) {
    el = document.createElement('link');
    el.setAttribute('rel', 'canonical');
    document.head.appendChild(el);
  }
  el.setAttribute('href', href);
}

export const GA_MEASUREMENT_ID = "${GA_ID}";

/** Track SPA navigations for GA4 (SEO landing-page performance). */
export function trackPageView(seo) {
  if (typeof window === "undefined" || !seo) return;
  const path = seo.path === "/" ? "/" : seo.path;
  const pageLocation = \`\${SITE_ORIGIN}\${path}\`;
  if (typeof window.gtag === "function") {
    window.gtag("config", GA_MEASUREMENT_ID, {
      page_path: path,
      page_title: seo.title,
      page_location: pageLocation,
    });
  }
}

/** Track key conversion events (contact form, etc.). */
export function trackEvent(name, params = {}) {
  if (typeof window === "undefined" || typeof window.gtag !== "function") return;
  window.gtag("event", name, params);
}
/* ANALYTICS_SPA_V1 */

export function applyClientSeo(seo) {
  const url = \`\${SITE_ORIGIN}\${seo.path === '/' ? '/' : seo.path}\`;
  document.title = seo.title;
  setMetaName('description', seo.description);
  setMetaName('robots', 'index, follow, max-image-preview:large');
  setCanonical(url);
  setMetaProperty('og:type', 'website');
  setMetaProperty('og:url', url);
  setMetaProperty('og:title', seo.title);
  setMetaProperty('og:description', seo.description);
  setMetaProperty('og:image', DEFAULT_OG_IMAGE);
  setMetaProperty('og:site_name', 'Bill Maniac');
  setMetaProperty('twitter:card', 'summary_large_image');
  setMetaProperty('twitter:url', url);
  setMetaProperty('twitter:title', seo.title);
  setMetaProperty('twitter:description', seo.description);
  setMetaProperty('twitter:image', DEFAULT_OG_IMAGE);
  trackPageView(seo);
}

export function resolveRouteFromLocation() {
  const path = normalizePath(window.location.pathname);
  const hash = (window.location.hash || '').replace(/^#/, '');

  if (path !== '/' && SEO_PAGES[path]) {
    return SEO_PAGES[path];
  }

  if (hash) {
    const hashPath = \`/\${hash}\`;
    if (SEO_PAGES[hashPath]) return SEO_PAGES[hashPath];
  }

  return SEO_PAGES['/'];
}

export function navigateToPath(path, { replace = false } = {}) {
  const seo = getSeoForPath(path);
  const url = seo.path === '/' ? '/' : seo.path;
  if (replace) {
    window.history.replaceState({ path: url }, '', url);
  } else {
    window.history.pushState({ path: url }, '', url);
  }
  window.dispatchEvent(new Event('billmaniac:navigate'));
}
`.trimStart();
}

function b64(text) {
  return "data:text/javascript;base64," + Buffer.from(text, "utf8").toString("base64");
}

async function main() {
  const mod = await import(pathToFileURL(join(ROOT, "functions/seo-config.js")).href);
  const seoSrc = buildClientSeoModule(mod.SEO_PAGES);

  const html = readFileSync(INDEX, "utf8");
  const m = html.match(/(<script type="importmap">)(.*?)(<\/script>)/s);
  if (!m) throw new Error("importmap not found");

  const imap = JSON.parse(m[2]);
  imap.imports["@/seo"] = b64(seoSrc);
  const out = html.slice(0, m.index) + m[1] + JSON.stringify(imap) + m[3] + html.slice(m.index + m[0].length);
  writeFileSync(INDEX, out);
  console.log(`Synced ${Object.keys(mod.SEO_PAGES).length} pages to @/seo in dist/index.html`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
