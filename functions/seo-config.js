/** Shared SEO config for Cloudflare Pages middleware + sitemap. */
export const SITE_ORIGIN = "https://billmaniac.win";
export const DEFAULT_OG_IMAGE = `${SITE_ORIGIN}/pics/og-billmaniac.svg`;
/** Raster OG image for image sitemaps (Google does not index SVG in image sitemaps). */
export const SITEMAP_OG_IMAGE = `${SITE_ORIGIN}/pics/og-cover.jpg`;
export const SITEMAP_PAGES_FILE = "sitemap.xml";
export const SITEMAP_PAGES_PATH = `/${SITEMAP_PAGES_FILE}`;
export const SITEMAP_PAGES_URL = `${SITE_ORIGIN}${SITEMAP_PAGES_PATH}`;
export const SITEMAP_IMAGES_FILE = "sitemap-images.xml";
export const SITEMAP_IMAGES_URL = `${SITE_ORIGIN}/${SITEMAP_IMAGES_FILE}`;

/**
 * @typedef {{
 *   title: string,
 *   description: string,
 *   path: string,
 *   priority: number,
 *   changefreq: string,
 *   pageKey: string,
 *   scrollTo?: string,
 *   index?: boolean,
 *   images?: string[],
 *   keywords?: string,
 * }} SeoPage
 */

/** @type {Record<string, SeoPage>} */
export const SEO_PAGES = {
  "/": {
    title: "Bill Maniac: Smart Expense Management & AI Receipt Scanner",
    description:
      "Tame your financial chaos with Bill Maniac. An AI-powered expense tracker with secure cloud storage. Scan receipts, get insights, and export your data anytime.",
    path: "/",
    priority: 1.0,
    changefreq: "weekly",
    pageKey: "home",
    keywords: "expense tracker, receipt scanner, AI finance, bill management",
    images: [SITEMAP_OG_IMAGE],
  },
  "/features": {
    title: "Features — Bill Maniac AI Receipt Scanner & Expense Tracker",
    description:
      "Scan receipts with AI, store them in a private Cloudflare cloud (D1 + R2), track spending by category, and export CSV or Excel anytime.",
    path: "/features",
    priority: 0.9,
    changefreq: "weekly",
    pageKey: "home",
    scrollTo: "features",
    keywords: "receipt OCR, expense categories, cloud storage, CSV export",
    images: [SITEMAP_OG_IMAGE],
  },
  "/pricing": {
    title: "Pricing — Bill Maniac Free, Pro & Maniac Plans",
    description:
      "Simple yearly pricing for Bill Maniac. Start free, upgrade to Pro or Maniac for more scans, private cloud storage, and advanced insights.",
    path: "/pricing",
    priority: 0.9,
    changefreq: "weekly",
    pageKey: "home",
    scrollTo: "pricing",
    keywords: "Bill Maniac pricing, Pro plan, expense app subscription",
    images: [SITEMAP_OG_IMAGE],
  },
  "/faq": {
    title: "FAQ — Bill Maniac Expense Tracker",
    description:
      "Answers about Bill Maniac scanning, private cloud storage, Google sign-in, Android app, exports, and pricing.",
    path: "/faq",
    priority: 0.8,
    changefreq: "monthly",
    pageKey: "home",
    scrollTo: "faq",
    keywords: "Bill Maniac FAQ, receipt scanning help, cloud storage",
    images: [SITEMAP_OG_IMAGE],
  },
  "/android": {
    title: "Android App — Bill Maniac Receipt Scanner",
    description:
      "Bill Maniac on Android: scan receipts on the go, unlock with PIN, sync to your private cloud, and review expenses anywhere.",
    path: "/android",
    priority: 0.9,
    changefreq: "weekly",
    pageKey: "android",
    keywords: "Bill Maniac Android, mobile receipt scanner, expense app",
    images: [SITEMAP_OG_IMAGE],
  },
  "/services": {
    title: "Products & Services — Bill Maniac",
    description:
      "AI receipt scanning, private cloud expense database, analytics, exports, and support plans from PT. DEVINCI GROUP INDONESIA.",
    path: "/services",
    priority: 0.9,
    changefreq: "monthly",
    pageKey: "services",
    keywords: "expense management services, receipt digitization, finance software",
    images: [SITEMAP_OG_IMAGE],
  },
  "/checkout": {
    title: "Checkout — Subscribe to Bill Maniac",
    description:
      "Choose Free, Pro, or Maniac and complete your yearly subscription request with PT. DEVINCI GROUP INDONESIA.",
    path: "/checkout",
    priority: 0.3,
    changefreq: "monthly",
    pageKey: "checkout",
    index: false,
    images: [SITEMAP_OG_IMAGE],
  },
  "/about": {
    title: "About — Bill Maniac",
    description:
      "Learn why Bill Maniac exists: AI receipt scanning with private cloud storage so your expense data stays yours.",
    path: "/about",
    priority: 0.7,
    changefreq: "monthly",
    pageKey: "about",
    images: [SITEMAP_OG_IMAGE, `${SITE_ORIGIN}/pics/avatars/sarah-k.jpg`, `${SITE_ORIGIN}/pics/avatars/david-l.jpg`],
  },
  "/contact": {
    title: "Contact — Bill Maniac",
    description: "Get in touch with the Bill Maniac team for support, partnerships, or product questions.",
    path: "/contact",
    priority: 0.7,
    changefreq: "monthly",
    pageKey: "contact",
    images: [SITEMAP_OG_IMAGE],
  },
  "/blog": {
    title: "Blog — Bill Maniac",
    description: "Tips on expense tracking, receipt scanning, and staying in control of your spending with Bill Maniac.",
    path: "/blog",
    priority: 0.6,
    changefreq: "weekly",
    pageKey: "blog",
    keywords: "expense tracking tips, receipt scanning blog",
    images: [SITEMAP_OG_IMAGE],
  },
  "/technical": {
    title: "Technical Overview — Bill Maniac Architecture",
    description:
      "How Bill Maniac Pro works: Google sign-in, Cloudflare Workers, D1 database, R2 receipt storage, and web + Android clients.",
    path: "/technical",
    priority: 0.6,
    changefreq: "monthly",
    pageKey: "technical",
    keywords: "Bill Maniac architecture, Cloudflare Workers, D1, R2",
    images: [SITEMAP_OG_IMAGE],
  },
  "/privacy": {
    title: "Privacy Policy — Bill Maniac",
    description: "How Bill Maniac collects, stores, and protects your account and receipt data.",
    path: "/privacy",
    priority: 0.5,
    changefreq: "yearly",
    pageKey: "privacy",
    images: [SITEMAP_OG_IMAGE],
  },
  "/data-deletion": {
    title: "Data Deletion Request — Bill Maniac",
    description:
      "Request deletion of your Bill Maniac account and data via the app or by email.",
    path: "/data-deletion",
    priority: 0.5,
    changefreq: "yearly",
    pageKey: "dataDeletion",
    images: [SITEMAP_OG_IMAGE],
  },
  "/terms": {
    title: "Terms of Service — Bill Maniac",
    description: "Terms governing use of the Bill Maniac web app, Android app, and related services.",
    path: "/terms",
    priority: 0.5,
    changefreq: "yearly",
    pageKey: "terms",
    images: [SITEMAP_OG_IMAGE],
  },
};

/** Site-wide images referenced in the image sitemap. */
export const SITE_IMAGES = [
  {
    loc: SITEMAP_OG_IMAGE,
    title: "Bill Maniac — AI expense tracker",
    caption: "Bill Maniac marketing image",
  },
  {
    loc: `${SITE_ORIGIN}/pics/avatars/sarah-k.jpg`,
    title: "Bill Maniac user testimonial",
    caption: "Bill Maniac customer avatar",
  },
  {
    loc: `${SITE_ORIGIN}/pics/avatars/david-l.jpg`,
    title: "Bill Maniac user testimonial",
    caption: "Bill Maniac customer avatar",
  },
];

export function normalizePath(pathname) {
  if (!pathname || pathname === "/") return "/";
  const trimmed = pathname.replace(/\/+$/, "");
  return trimmed || "/";
}

export function getSeoForPath(pathname) {
  const path = normalizePath(pathname);
  return SEO_PAGES[path] || SEO_PAGES["/"];
}

export function isIndexablePath(pathname) {
  const page = getSeoForPath(pathname);
  return page.index !== false;
}

export function listIndexablePages() {
  return Object.values(SEO_PAGES).filter((page) => page.index !== false);
}
