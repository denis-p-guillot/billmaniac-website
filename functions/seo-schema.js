import { DEFAULT_OG_IMAGE, SITE_ORIGIN, SEO_PAGES, normalizePath } from "./seo-config.js";

/** @typedef {import("./seo-config.js").SeoPage} SeoPage */

export const SITE_LANGUAGES = ["en", "fr", "es"];

export const FAQ_ITEMS = [
  {
    question: "What is Bill Maniac?",
    answer:
      "Bill Maniac is an AI-powered expense tracker for web and Android. Scan receipts, categorize spending, and export your data from secure private cloud storage.",
  },
  {
    question: "How does AI receipt scanning work?",
    answer:
      "Upload a photo or PDF of a receipt. Bill Maniac extracts vendor, date, amount, and category using AI, then stores the receipt image in your private cloud.",
  },
  {
    question: "Where is my data stored?",
    answer:
      "Receipts and bill data are stored in a private Cloudflare cloud (D1 database and R2 object storage). Your data is tied to your account and is not published publicly.",
  },
  {
    question: "Is there an Android app?",
    answer:
      "Yes. Bill Maniac Pro on Android supports receipt scanning, PIN lock, biometric unlock, and sync with the same cloud account as the web app.",
  },
  {
    question: "What pricing plans are available?",
    answer:
      "Bill Maniac offers Free, Pro, and Maniac yearly plans. Start free and upgrade for more scans, storage, and advanced insights.",
  },
  {
    question: "Can I export my expenses?",
    answer:
      "Yes. Export bills to CSV or Excel from the web app at any time, including filtered date ranges.",
  },
];

function pageUrl(path) {
  return path === "/" ? `${SITE_ORIGIN}/` : `${SITE_ORIGIN}${path}`;
}

function organizationNode() {
  return {
    "@type": "Organization",
    "@id": `${SITE_ORIGIN}/#organization`,
    name: "Bill Maniac",
    legalName: "PT. DEVINCI GROUP INDONESIA",
    url: `${SITE_ORIGIN}/`,
    logo: {
      "@type": "ImageObject",
      url: DEFAULT_OG_IMAGE,
    },
    sameAs: [`${SITE_ORIGIN}/`],
  };
}

function websiteNode() {
  return {
    "@type": "WebSite",
    "@id": `${SITE_ORIGIN}/#website`,
    url: `${SITE_ORIGIN}/`,
    name: "Bill Maniac",
    description:
      "AI-powered expense tracker with private cloud storage for web and Android.",
    publisher: { "@id": `${SITE_ORIGIN}/#organization` },
    inLanguage: SITE_LANGUAGES,
  };
}

/** @param {string} path @param {SeoPage} seo */
function webPageNode(path, seo) {
  return {
    "@type": "WebPage",
    "@id": `${pageUrl(path)}#webpage`,
    url: pageUrl(path),
    name: seo.title,
    description: seo.description,
    isPartOf: { "@id": `${SITE_ORIGIN}/#website` },
    about: { "@id": `${SITE_ORIGIN}/#app` },
    inLanguage: SITE_LANGUAGES,
  };
}

/** @param {string} path @param {SeoPage} seo */
function breadcrumbNode(path, seo) {
  const crumbs = [{ name: "Home", path: "/" }];
  if (path !== "/") {
    const label =
      seo.path === "/features"
        ? "Features"
        : seo.path === "/pricing"
          ? "Pricing"
          : seo.title.split(" — ")[0] || seo.title;
    crumbs.push({ name: label, path });
  }

  return {
    "@type": "BreadcrumbList",
    "@id": `${pageUrl(path)}#breadcrumb`,
    itemListElement: crumbs.map((crumb, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: crumb.name,
      item: pageUrl(crumb.path),
    })),
  };
}

function softwareApplicationNode() {
  return {
    "@type": "SoftwareApplication",
    "@id": `${SITE_ORIGIN}/#app`,
    name: "Bill Maniac",
    applicationCategory: "FinanceApplication",
    operatingSystem: "Web, Android",
    description:
      "Smart expense manager with AI receipt scanning, private cloud storage, analytics, and exports.",
    offers: {
      "@type": "AggregateOffer",
      offerCount: 3,
      lowPrice: "0",
      highPrice: "60",
      priceCurrency: "USD",
      offers: [
        { "@type": "Offer", name: "FREE", price: "0", priceCurrency: "USD" },
        {
          "@type": "Offer",
          name: "PRO MODE",
          price: "12",
          priceCurrency: "USD",
          priceSpecification: {
            "@type": "PriceSpecification",
            price: "12",
            priceCurrency: "USD",
            unitText: "YEAR",
          },
        },
        {
          "@type": "Offer",
          name: "MANIAC MODE",
          price: "60",
          priceCurrency: "USD",
          priceSpecification: {
            "@type": "PriceSpecification",
            price: "60",
            priceCurrency: "USD",
            unitText: "YEAR",
          },
        },
      ],
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "4.8",
      ratingCount: "128",
    },
  };
}

function faqPageNode() {
  return {
    "@type": "FAQPage",
    "@id": `${SITE_ORIGIN}/faq#faq`,
    mainEntity: FAQ_ITEMS.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}

function androidAppNode() {
  return {
    "@type": "MobileApplication",
    "@id": `${SITE_ORIGIN}/android#app`,
    name: "Bill Maniac for Android",
    operatingSystem: "Android",
    applicationCategory: "FinanceApplication",
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    url: `${SITE_ORIGIN}/android`,
  };
}

/** @param {string} pathname */
export function buildStructuredData(pathname) {
  const path = normalizePath(pathname);
  const seo = SEO_PAGES[path] || SEO_PAGES["/"];
  const graph = [
    organizationNode(),
    websiteNode(),
    webPageNode(path, seo),
    breadcrumbNode(path, seo),
  ];

  if (path === "/" || path === "/pricing" || path === "/features") {
    graph.push(softwareApplicationNode());
  }
  if (path === "/faq") {
    graph.push(faqPageNode());
  }
  if (path === "/android") {
    graph.push(androidAppNode());
    graph.push(softwareApplicationNode());
  }

  return {
    "@context": "https://schema.org",
    "@graph": graph,
  };
}
