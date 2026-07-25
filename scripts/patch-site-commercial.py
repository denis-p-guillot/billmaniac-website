#!/usr/bin/env python3
"""Patch billmaniac-website dist/index.html with commercial page completeness."""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terms_of_service import patch_terms_in_translations  # noqa: E402
from data_deletion_request import patch_data_deletion_in_translations  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"

PHONE_DISPLAY = "+62 (0) 81283803745"
PHONE_TEL = "+6281283803745"
WA = "6281283803745"
ADDRESS_LINE1 = "Menara Ravindo, Lantai 12"
ADDRESS_LINE2 = "Jl. Kebon Sirih Kav. 75"
ADDRESS_LINE3 = "RT 001 / RW 001"
ADDRESS_LINE4 = "Kelurahan Kebon Sirih, Kecamatan Menteng"
ADDRESS_LINE5 = "Jakarta Pusat 10340"
ADDRESS_LINE6 = "DKI Jakarta, Indonesia"
ADDRESS_FULL = (
    "Menara Ravindo, Lantai 12, Jl. Kebon Sirih Kav. 75, "
    "RT 001/RW 001, Kelurahan Kebon Sirih, Kecamatan Menteng, "
    "Jakarta Pusat 10340, DKI Jakarta, Indonesia"
)
EMAIL_BIZ = "denis@digitek-computer.com"
EMAIL_GEN = "denis.digitek@gmail.com"
COMPANY = "PT. DEVINCI GROUP INDONESIA"


def b64(src: str) -> str:
    return "data:application/javascript;base64," + base64.b64encode(
        src.encode("utf-8")
    ).decode("ascii")


CONTACT_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const PHONE_DISPLAY = "+62 (0) 81283803745";
const PHONE_TEL = "+6281283803745";
const WA = "6281283803745";
const EMAIL_BIZ = "denis@digitek-computer.com";
const EMAIL_GEN = "denis.digitek@gmail.com";
const ADDRESS_LINES = [
  "Menara Ravindo, Lantai 12",
  "Jl. Kebon Sirih Kav. 75",
  "Jakarta, Indonesia",
];

const Contact = () => {
  const { t } = useLanguage();
  const onBack = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath("/");
  };
  return _jsx("section", {
    id: "contact",
    className: "bg-slate-950 py-20 sm:py-28",
    children: _jsxs("div", {
      className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "text-center",
          children: [
            _jsx("h1", { className: "text-4xl font-extrabold text-white sm:text-5xl", children: t.contact.title }),
            _jsx("p", { className: "mt-4 text-lg text-slate-400", children: t.contact.intro }),
          ],
        }),
        _jsx("div", {
          className: "mt-12 grid gap-6 md:grid-cols-2",
          children: [
            _jsxs("div", {
              className: "bg-slate-900 p-8 rounded-lg border border-slate-800",
              children: [
                _jsx("h2", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: t.contact.officeLabel }),
                _jsx("p", { className: "mt-3 text-lg font-semibold text-white", children: "PT. DEVINCI GROUP INDONESIA" }),
                _jsx("p", { className: "mt-3 text-slate-300 whitespace-pre-line", children: ADDRESS_LINES.join("\n") }),
                _jsxs("p", {
                  className: "mt-6 text-slate-300",
                  children: [
                    _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.phoneLabel }),
                    _jsx("a", {
                      href: `tel:${PHONE_TEL}`,
                      className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                      children: PHONE_DISPLAY,
                    }),
                  ],
                }),
                _jsxs("div", {
                  className: "mt-4 flex flex-wrap gap-3",
                  children: [
                    _jsx("a", {
                      href: `https://wa.me/${WA}`,
                      target: "_blank",
                      rel: "noopener noreferrer",
                      className: "inline-flex items-center justify-center px-4 py-2 rounded-md bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-500",
                      children: t.contact.whatsappCta,
                    }),
                    _jsx("a", {
                      href: "/checkout",
                      className: "inline-flex items-center justify-center px-4 py-2 rounded-md bg-brand-primary text-white text-sm font-semibold hover:bg-brand-dark",
                      children: t.contact.checkoutCta,
                    }),
                  ],
                }),
              ],
            }),
            _jsxs("div", {
              className: "bg-slate-900 p-8 rounded-lg border border-slate-800 space-y-5",
              children: [
                _jsx("h2", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: t.contact.emailLabel }),
                _jsxs("p", {
                  className: "text-slate-300",
                  children: [
                    _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.businessLabel }),
                    _jsx("a", {
                      href: `mailto:${EMAIL_BIZ}`,
                      className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                      children: EMAIL_BIZ,
                    }),
                  ],
                }),
                _jsxs("p", {
                  className: "text-slate-300",
                  children: [
                    _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.generalLabel }),
                    _jsx("a", {
                      href: `mailto:${EMAIL_GEN}`,
                      className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                      children: EMAIL_GEN,
                    }),
                  ],
                }),
                _jsx("p", { className: "text-sm text-slate-500", children: t.contact.hours }),
              ],
            }),
          ],
        }),
        _jsx("div", {
          className: "mt-12 text-center",
          children: _jsxs("a", {
            href: "/",
            onClick: onBack,
            className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors",
            children: [
              _jsx(ArrowLeftIcon, { "aria-hidden": "true", className: "h-4 w-4" }),
              t.contact.backToHome,
            ],
          }),
        }),
      ],
    }),
  });
};
export default Contact;
'''

CHECKOUT_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from 'react';
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon, CheckIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const PHONE_DISPLAY = "+62 (0) 81283803745";
const PHONE_TEL = "+6281283803745";
const WA = "6281283803745";
const EMAIL_BIZ = "denis@digitek-computer.com";
const ADDRESS = "Menara Ravindo, Lantai 12, Jl. Kebon Sirih Kav. 75, Jakarta, Indonesia";

const PLAN_META = {
  free: { id: "free", priceEn: "$0 / forever", priceFr: "0€ / pour toujours", priceEs: "0€ / para siempre" },
  pro: { id: "pro", priceEn: "$18 / year", priceFr: "18€ / an", priceEs: "18€ / año" },
  maniac: { id: "maniac", priceEn: "$60 / year", priceFr: "60€ / an", priceEs: "60€ / año" },
};

function initialPlan() {
  try {
    const q = new URLSearchParams(window.location.search).get("plan");
    if (q && PLAN_META[q.toLowerCase()]) return q.toLowerCase();
  } catch (_) {}
  return "pro";
}

const Checkout = () => {
  const { t, language } = useLanguage();
  const c = t.checkout;
  const [plan, setPlan] = useState(initialPlan);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [notes, setNotes] = useState("");

  const planLabel = useMemo(() => {
    const map = { free: c.planFree, pro: c.planPro, maniac: c.planManiac };
    return map[plan] || c.planPro;
  }, [plan, c]);

  const planPrice = useMemo(() => {
    const meta = PLAN_META[plan] || PLAN_META.pro;
    if (language === "fr") return meta.priceFr;
    if (language === "es") return meta.priceEs;
    return meta.priceEn;
  }, [plan, language]);

  const messageBody = useMemo(() => {
    return [
      c.messageIntro,
      "",
      `${c.fieldPlan}: ${planLabel} (${planPrice})`,
      `${c.fieldName}: ${name || "-"}`,
      `${c.fieldEmail}: ${email || "-"}`,
      `${c.fieldCompany}: ${company || "-"}`,
      `${c.fieldNotes}: ${notes || "-"}`,
      "",
      c.messageOutro,
    ].join("\n");
  }, [c, planLabel, planPrice, name, email, company, notes]);

  const mailtoHref = `mailto:${EMAIL_BIZ}?subject=${encodeURIComponent(c.emailSubject.replace("{plan}", planLabel))}&body=${encodeURIComponent(messageBody)}`;
  const waHref = `https://wa.me/${WA}?text=${encodeURIComponent(messageBody)}`;

  const onBack = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath("/pricing");
  };

  const plans = [
    { id: "free", label: c.planFree },
    { id: "pro", label: c.planPro },
    { id: "maniac", label: c.planManiac },
  ];

  return _jsx("section", {
    id: "checkout",
    className: "bg-slate-950 py-20 sm:py-28",
    children: _jsxs("div", {
      className: "max-w-5xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "text-center max-w-3xl mx-auto",
          children: [
            _jsx("p", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: c.eyebrow }),
            _jsx("h1", { className: "mt-3 text-4xl font-extrabold text-white sm:text-5xl", children: c.title }),
            _jsx("p", { className: "mt-4 text-lg text-slate-400", children: c.intro }),
          ],
        }),
        _jsx("div", {
          className: "mt-12 grid gap-8 lg:grid-cols-5",
          children: [
            _jsxs("div", {
              className: "lg:col-span-3 bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-5",
              children: [
                _jsx("h2", { className: "text-lg font-semibold text-white", children: c.selectPlan }),
                _jsx("div", {
                  className: "grid gap-3 sm:grid-cols-3",
                  children: plans.map((p) =>
                    _jsx("button", {
                      type: "button",
                      onClick: () => setPlan(p.id),
                      className: `rounded-xl border px-3 py-3 text-sm font-semibold transition-colors ${plan === p.id ? "border-brand-primary bg-brand-primary/20 text-white" : "border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500"}`,
                      children: p.label,
                    }, p.id)
                  ),
                }),
                _jsxs("label", {
                  className: "block",
                  children: [
                    _jsx("span", { className: "text-sm text-slate-400", children: c.fieldName }),
                    _jsx("input", {
                      value: name,
                      onChange: (e) => setName(e.target.value),
                      className: "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100",
                      placeholder: c.placeholderName,
                      required: true,
                    }),
                  ],
                }),
                _jsxs("label", {
                  className: "block",
                  children: [
                    _jsx("span", { className: "text-sm text-slate-400", children: c.fieldEmail }),
                    _jsx("input", {
                      type: "email",
                      value: email,
                      onChange: (e) => setEmail(e.target.value),
                      className: "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100",
                      placeholder: c.placeholderEmail,
                      required: true,
                    }),
                  ],
                }),
                _jsxs("label", {
                  className: "block",
                  children: [
                    _jsx("span", { className: "text-sm text-slate-400", children: c.fieldCompany }),
                    _jsx("input", {
                      value: company,
                      onChange: (e) => setCompany(e.target.value),
                      className: "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100",
                      placeholder: c.placeholderCompany,
                    }),
                  ],
                }),
                _jsxs("label", {
                  className: "block",
                  children: [
                    _jsx("span", { className: "text-sm text-slate-400", children: c.fieldNotes }),
                    _jsx("textarea", {
                      value: notes,
                      onChange: (e) => setNotes(e.target.value),
                      rows: 4,
                      className: "mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-100",
                      placeholder: c.placeholderNotes,
                    }),
                  ],
                }),
                _jsxs("div", {
                  className: "flex flex-col sm:flex-row gap-3 pt-2",
                  children: [
                    _jsx("a", {
                      href: waHref,
                      target: "_blank",
                      rel: "noopener noreferrer",
                      className: "flex-1 inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-3 text-sm font-bold text-white hover:bg-emerald-500",
                      children: c.whatsappCta,
                    }),
                    _jsx("a", {
                      href: mailtoHref,
                      className: "flex-1 inline-flex items-center justify-center rounded-lg bg-brand-primary px-4 py-3 text-sm font-bold text-white hover:bg-brand-dark",
                      children: c.emailCta,
                    }),
                  ],
                }),
                _jsx("p", { className: "text-xs text-slate-500", children: c.help }),
              ],
            }),
            _jsxs("aside", {
              className: "lg:col-span-2 space-y-6",
              children: [
                _jsxs("div", {
                  className: "bg-slate-900 border border-slate-800 rounded-2xl p-6",
                  children: [
                    _jsx("h3", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: c.summaryTitle }),
                    _jsx("p", { className: "mt-3 text-2xl font-bold text-white", children: planLabel }),
                    _jsx("p", { className: "mt-1 text-slate-300", children: planPrice }),
                    _jsx("ul", {
                      className: "mt-5 space-y-2 text-sm text-slate-400",
                      children: (c.summaryBullets || []).map((item, idx) =>
                        _jsxs("li", {
                          className: "flex items-start gap-2",
                          children: [
                            _jsx(CheckIcon, { className: "h-5 w-5 text-brand-primary flex-shrink-0", "aria-hidden": "true" }),
                            _jsx("span", { children: item }),
                          ],
                        }, idx)
                      ),
                    }),
                  ],
                }),
                _jsxs("div", {
                  className: "bg-slate-900 border border-slate-800 rounded-2xl p-6 text-sm text-slate-300 space-y-2",
                  children: [
                    _jsx("h3", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: c.sellerTitle }),
                    _jsx("p", { className: "font-semibold text-white", children: "PT. DEVINCI GROUP INDONESIA" }),
                    _jsx("p", { children: ADDRESS }),
                    _jsxs("p", {
                      children: [
                        c.phoneLabel,
                        ": ",
                        _jsx("a", { href: `tel:${PHONE_TEL}`, className: "text-brand-primary underline", children: PHONE_DISPLAY }),
                      ],
                    }),
                    _jsxs("p", {
                      children: [
                        c.emailLabel,
                        ": ",
                        _jsx("a", { href: `mailto:${EMAIL_BIZ}`, className: "text-brand-primary underline", children: EMAIL_BIZ }),
                      ],
                    }),
                  ],
                }),
              ],
            }),
          ],
        }),
        _jsx("div", {
          className: "mt-12 text-center",
          children: _jsxs("a", {
            href: "/pricing",
            onClick: onBack,
            className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white",
            children: [_jsx(ArrowLeftIcon, { className: "h-4 w-4", "aria-hidden": "true" }), c.backToPricing],
          }),
        }),
      ],
    }),
  });
};
export default Checkout;
'''

SERVICES_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon, CheckIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const Services = () => {
  const { t } = useLanguage();
  const s = t.services;
  const onBack = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath("/");
  };
  return _jsx("section", {
    id: "services",
    className: "bg-slate-950 py-20 sm:py-28",
    children: _jsxs("div", {
      className: "max-w-6xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "text-center max-w-3xl mx-auto",
          children: [
            _jsx("p", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: s.eyebrow }),
            _jsx("h1", { className: "mt-3 text-4xl font-extrabold text-white sm:text-5xl", children: s.title }),
            _jsx("p", { className: "mt-4 text-lg text-slate-400", children: s.intro }),
          ],
        }),
        _jsx("div", {
          className: "mt-14 grid gap-6 md:grid-cols-2",
          children: (s.items || []).map((item) =>
            _jsxs("article", {
              className: "rounded-2xl border border-slate-800 bg-slate-900 p-7",
              children: [
                _jsx("h2", { className: "text-xl font-bold text-white", children: item.title }),
                _jsx("p", { className: "mt-3 text-slate-400", children: item.text }),
                _jsx("ul", {
                  className: "mt-5 space-y-2",
                  children: (item.bullets || []).map((b, i) =>
                    _jsxs("li", {
                      className: "flex items-start gap-2 text-sm text-slate-300",
                      children: [
                        _jsx(CheckIcon, { className: "h-5 w-5 text-brand-primary flex-shrink-0", "aria-hidden": "true" }),
                        _jsx("span", { children: b }),
                      ],
                    }, i)
                  ),
                }),
              ],
            }, item.title)
          ),
        }),
        _jsxs("div", {
          className: "mt-12 flex flex-col sm:flex-row gap-3 justify-center",
          children: [
            _jsx("a", {
              href: "/pricing",
              className: "inline-flex justify-center rounded-lg bg-brand-primary px-6 py-3 text-sm font-bold text-white hover:bg-brand-dark",
              children: s.ctaPricing,
            }),
            _jsx("a", {
              href: "/checkout?plan=pro",
              className: "inline-flex justify-center rounded-lg bg-slate-700 px-6 py-3 text-sm font-bold text-white hover:bg-slate-600",
              children: s.ctaCheckout,
            }),
          ],
        }),
        _jsx("div", {
          className: "mt-10 text-center",
          children: _jsxs("a", {
            href: "/",
            onClick: onBack,
            className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white",
            children: [_jsx(ArrowLeftIcon, { className: "h-4 w-4", "aria-hidden": "true" }), s.backToHome],
          }),
        }),
      ],
    }),
  });
};
export default Services;
'''

PRICING_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { CheckIcon } from '@/constants';

function ctaHrefForTier(name) {
  const n = String(name || "").toUpperCase();
  if (n.includes("MANIAC")) return "/checkout?plan=maniac";
  if (n.includes("PRO")) return "/checkout?plan=pro";
  return "https://my.billmaniac.win";
}

const Pricing = () => {
  const { t } = useLanguage();
  return _jsx("section", {
    id: "pricing",
    className: "py-20 sm:py-28 bg-slate-900",
    children: _jsxs("div", {
      className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "text-center",
          children: [
            _jsx("h2", { className: "text-3xl font-extrabold text-white sm:text-4xl", children: t.pricing.title }),
            _jsx("p", { className: "mt-4 text-lg text-slate-400", children: t.pricing.subTitle }),
          ],
        }),
        _jsx("div", {
          className: "mt-16 grid max-w-lg mx-auto gap-8 lg:max-w-7xl lg:grid-cols-3",
          children: t.pricing.tiers.map((tier) => {
            const href = ctaHrefForTier(tier.name);
            const external = href.startsWith("http");
            return _jsxs("div", {
              className: `relative flex flex-col rounded-2xl p-8 shadow-2xl ${tier.isPopular ? "bg-slate-800 border-2 border-brand-primary" : "bg-slate-800/50 border border-slate-700"}`,
              children: [
                tier.isPopular && _jsx("div", {
                  className: "absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2",
                  children: _jsx("span", {
                    className: "inline-flex items-center px-4 py-1 rounded-full text-sm font-semibold tracking-wider text-white bg-brand-primary",
                    children: t.pricing.mostPopular || "Most Popular",
                  }),
                }),
                _jsx("h3", { className: "text-2xl font-bold text-white", children: tier.name }),
                _jsx("p", { className: "mt-2 text-slate-400 h-12", children: tier.audience }),
                _jsxs("div", {
                  className: "mt-4",
                  children: [
                    _jsx("span", { className: "text-5xl font-extrabold text-white", children: tier.price }),
                    _jsx("span", { className: "text-lg font-medium text-slate-500", children: tier.priceDetails }),
                  ],
                }),
                _jsx("ul", {
                  className: "mt-8 space-y-4 text-slate-400 flex-grow",
                  children: tier.features.map((feature, index) =>
                    _jsxs("li", {
                      className: "flex items-start",
                      children: [
                        !feature.isSpecial
                          ? _jsx(CheckIcon, { "aria-hidden": "true", className: "h-6 w-6 flex-shrink-0 mr-2 text-brand-primary" })
                          : _jsx("span", { className: "w-6 mr-2 flex-shrink-0" }),
                        _jsx("span", { className: feature.isSpecial ? "font-bold text-white" : "", children: feature.text }),
                      ],
                    }, index)
                  ),
                }),
                _jsx("div", {
                  className: "mt-10",
                  children: _jsx("a", {
                    href: href,
                    ...(external ? {} : {}),
                    className: `w-full inline-flex items-center justify-center px-6 py-3 text-lg font-bold rounded-lg transition-colors ${tier.isPopular ? "text-white bg-brand-primary hover:bg-brand-dark shadow-lg" : "text-white bg-slate-700 hover:bg-slate-600"}`,
                    children: tier.cta,
                  }),
                }),
              ],
            }, tier.name);
          }),
        }),
        _jsx("p", {
          className: "mt-10 text-center text-sm text-slate-500",
          children: t.pricing.checkoutNote || "",
        }),
      ],
    }),
  });
};
export default Pricing;
'''

ABOUT_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const PHONE_DISPLAY = "+62 (0) 81283803745";
const PHONE_TEL = "+6281283803745";
const ADDRESS = "Menara Ravindo, Lantai 12, Jl. Kebon Sirih Kav. 75, Jakarta, Indonesia";

const About = () => {
  const { t } = useLanguage();
  const onBack = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath("/");
  };
  return _jsx("section", {
    id: "about",
    className: "bg-slate-950 py-20 sm:py-28",
    children: _jsxs("div", {
      className: "max-w-3xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsx("div", {
          className: "text-center",
          children: _jsx("h1", { className: "text-4xl font-extrabold text-white sm:text-5xl", children: t.about.title }),
        }),
        _jsxs("div", {
          className: "mt-12 text-lg text-slate-400 space-y-6 bg-slate-900 p-8 rounded-lg border border-slate-800",
          children: [
            _jsxs("p", {
              children: [
                t.about.p1,
                " ",
                _jsx("a", {
                  href: "http://www.digitek-computer.com",
                  target: "_blank",
                  rel: "noopener noreferrer",
                  className: "font-semibold text-brand-primary hover:text-brand-secondary transition-colors underline",
                  children: t.about.companyName,
                }),
                ".",
              ],
            }),
            _jsx("p", { children: t.about.p2 }),
            _jsxs("p", {
              children: [
                t.about.p3,
                " ",
                _jsx("a", {
                  href: "https://www.linkedin.com/in/denis-guillot-portcities/",
                  target: "_blank",
                  rel: "noopener noreferrer",
                  className: "font-semibold text-brand-primary hover:text-brand-secondary transition-colors underline",
                  children: t.about.developerName,
                }),
                ".",
              ],
            }),
            _jsxs("div", {
              className: "pt-4 border-t border-slate-800 space-y-2 text-base",
              children: [
                _jsx("p", { className: "text-sm uppercase tracking-wider text-brand-primary font-semibold", children: t.about.officeLabel }),
                _jsx("p", { className: "text-slate-300", children: ADDRESS }),
                _jsxs("p", {
                  className: "text-slate-300",
                  children: [
                    t.about.phoneLabel,
                    ": ",
                    _jsx("a", { href: `tel:${PHONE_TEL}`, className: "text-brand-primary underline", children: PHONE_DISPLAY }),
                  ],
                }),
              ],
            }),
          ],
        }),
        _jsx("div", {
          className: "mt-12 text-center",
          children: _jsxs("a", {
            href: "/",
            onClick: onBack,
            className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors",
            children: [_jsx(ArrowLeftIcon, { "aria-hidden": "true", className: "h-4 w-4" }), t.about.backToHome],
          }),
        }),
      ],
    }),
  });
};
export default About;
'''

FOOTER_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BillManiacLogo } from '@/constants';
import { useLanguage } from '@/LanguageContext';
import { navigateToPath } from '@/seo';

const PHONE_DISPLAY = "+62 (0) 81283803745";
const PHONE_TEL = "+6281283803745";
const ADDRESS_LINES = [
  "Menara Ravindo, Lantai 12",
  "Jl. Kebon Sirih Kav. 75",
  "Jakarta, Indonesia",
];

const Footer = () => {
  const { t } = useLanguage();
  return _jsx("footer", {
    className: "bg-slate-900 text-slate-400",
    children: _jsxs("div", {
      className: "max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "grid grid-cols-2 md:grid-cols-5 gap-8",
          children: [
            _jsxs("div", {
              className: "col-span-2 md:col-span-2",
              children: [
                _jsxs("a", {
                  href: "/",
                  className: "flex items-center gap-2",
                  children: [
                    _jsx(BillManiacLogo, { className: "h-8 w-auto text-white" }),
                    _jsx("span", { className: "text-xl font-bold text-white", children: "Bill Maniac" }),
                  ],
                }),
                _jsx("p", { className: "mt-4 text-sm", children: t.footer.copyright }),
                _jsx("p", { className: "mt-4 text-sm font-semibold text-slate-300", children: "PT. DEVINCI GROUP INDONESIA" }),
                _jsx("p", { className: "mt-2 text-sm whitespace-pre-line", children: ADDRESS_LINES.join("\n") }),
                _jsxs("p", {
                  className: "mt-2 text-sm",
                  children: [
                    _jsx("a", { href: `tel:${PHONE_TEL}`, className: "hover:text-white", children: PHONE_DISPLAY }),
                  ],
                }),
              ],
            }),
            _jsxs("div", {
              children: [
                _jsx("h3", { className: "text-sm font-semibold text-slate-300 tracking-wider uppercase", children: t.footer.product }),
                _jsxs("ul", {
                  className: "mt-4 space-y-2",
                  children: [
                    _jsx("li", { children: _jsx("a", { href: "/services", className: "text-base hover:text-white transition-colors", children: t.footer.nav.services }) }),
                    _jsx("li", { children: _jsx("a", { href: "/features", className: "text-base hover:text-white transition-colors", children: t.footer.nav.features }) }),
                    _jsx("li", { children: _jsx("a", { href: "/android", className: "text-base hover:text-white transition-colors", children: t.footer.nav.android }) }),
                    _jsx("li", { children: _jsx("a", { href: "/pricing", className: "text-base hover:text-white transition-colors", children: t.footer.nav.pricing }) }),
                    _jsx("li", { children: _jsx("a", { href: "/checkout", className: "text-base hover:text-white transition-colors", children: t.footer.nav.checkout }) }),
                    _jsx("li", { children: _jsx("a", { href: "https://my.billmaniac.win", className: "text-base hover:text-white transition-colors", children: t.footer.nav.login }) }),
                  ],
                }),
              ],
            }),
            _jsxs("div", {
              children: [
                _jsx("h3", { className: "text-sm font-semibold text-slate-300 tracking-wider uppercase", children: t.footer.company }),
                _jsxs("ul", {
                  className: "mt-4 space-y-2",
                  children: [
                    _jsx("li", { children: _jsx("a", { href: "/about", className: "text-base hover:text-white transition-colors", children: t.footer.nav.about }) }),
                    _jsx("li", { children: _jsx("a", { href: "/contact", className: "text-base hover:text-white transition-colors", children: t.footer.nav.contact }) }),
                    _jsx("li", { children: _jsx("a", { href: "/blog", className: "text-base hover:text-white transition-colors", children: t.footer.nav.blog }) }),
                    _jsx("li", { children: _jsx("a", { href: "/technical", className: "text-base hover:text-white transition-colors", children: t.footer.nav.technical }) }),
                  ],
                }),
              ],
            }),
            _jsxs("div", {
              children: [
                _jsx("h3", { className: "text-sm font-semibold text-slate-300 tracking-wider uppercase", children: t.footer.legal }),
                _jsxs("ul", {
                  className: "mt-4 space-y-2",
                  children: [
                    _jsx("li", { children: _jsx("a", { href: "/privacy", className: "text-base hover:text-white transition-colors", children: t.footer.nav.privacy }) }),
                    _jsx("li", { children: _jsx("a", { href: "/terms", className: "text-base hover:text-white transition-colors", children: t.footer.nav.terms }) }),
                    _jsx("li", { children: _jsx("a", { href: "/data-deletion", className: "text-base hover:text-white transition-colors", children: t.footer.nav.dataDeletion }) }),
                  ],
                }),
              ],
            }),
          ],
        }),
        _jsx("div", {
          className: "mt-8 border-t border-slate-800 pt-8 flex items-center justify-between",
          children: _jsx("p", { className: "text-sm", children: t.footer.tagline }),
        }),
      ],
    }),
  });
};
export default Footer;

if (typeof window !== "undefined" && !window.__billmaniacFooterNav) {
  window.__billmaniacFooterNav = true;
  document.addEventListener("click", (event) => {
    const a = event.target && event.target.closest ? event.target.closest('a[href^="/"]') : null;
    if (!a) return;
    const href = a.getAttribute("href");
    if (!href || href.startsWith("//") || href.includes("://")) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath(href.split("?")[0]);
    if (href.includes("?")) {
      window.history.replaceState({}, "", href);
      window.dispatchEvent(new Event("billmaniac:navigate"));
    }
  });
}
'''

HEADER_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BillManiacLogo } from '@/constants';
import { useLanguage } from '@/LanguageContext';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import { navigateToPath } from '@/seo';

const Header = () => {
  const { t } = useLanguage();
  const navLinks = [
    { name: t.header.services, href: "/services" },
    { name: t.header.features, href: "/features" },
    { name: t.header.pricing, href: "/pricing" },
    { name: t.header.checkout, href: "/checkout" },
    { name: t.header.faq, href: "/faq" },
    { name: t.header.android, href: "/android" },
  ];

  const onNav = (event, href) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath(href);
  };

  return _jsx("header", {
    className: "sticky top-0 z-50 bg-slate-900/80 backdrop-blur-sm border-b border-slate-800",
    children: _jsx("div", {
      className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
      children: _jsxs("div", {
        className: "flex items-center justify-between h-16",
        children: [
          _jsx("div", {
            className: "flex items-center",
            children: _jsxs("a", {
              href: "/",
              onClick: (e) => onNav(e, "/"),
              className: "flex items-center gap-2",
              children: [
                _jsx(BillManiacLogo, { className: "h-8 w-auto text-brand-primary" }),
                _jsx("span", { className: "text-xl font-bold text-white", children: "Bill Maniac" }),
              ],
            }),
          }),
          _jsxs("div", {
            className: "flex items-center space-x-4 md:space-x-6",
            children: [
              _jsx("nav", {
                className: "hidden lg:flex lg:items-center lg:space-x-6",
                children: navLinks.map((link) =>
                  _jsx("a", {
                    href: link.href,
                    onClick: (e) => onNav(e, link.href),
                    className: "font-medium text-slate-300 hover:text-white transition-colors text-sm",
                    children: link.name,
                  }, link.name)
                ),
              }),
              _jsxs("div", {
                className: "flex items-center space-x-3",
                children: [
                  _jsx("a", {
                    href: "/contact",
                    onClick: (e) => onNav(e, "/contact"),
                    className: "hidden md:inline-block text-sm font-semibold text-slate-300 hover:text-white",
                    children: t.header.contact,
                  }),
                  _jsx("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-block text-sm font-semibold bg-slate-700 text-white px-3 py-2 rounded-md hover:bg-slate-600 transition-colors",
                    children: t.header.login,
                  }),
                  _jsx("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-block text-sm font-semibold bg-brand-primary text-white px-3 py-2 rounded-md hover:bg-brand-dark transition-colors shadow-lg",
                    children: t.header.signUp,
                  }),
                  _jsx(LanguageSwitcher, {}),
                ],
              }),
            ],
          }),
        ],
      }),
    }),
  });
};
export default Header;
'''

TERMS_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
const Terms = () => {
    const { t } = useLanguage();
    return (_jsx("section", { id: "terms", className: "bg-slate-950 py-20 sm:py-28", children: _jsxs("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8", children: [_jsxs("div", { className: "text-center", children: [_jsx("h1", { className: "text-4xl font-extrabold text-white sm:text-5xl", children: t.terms.title }), _jsxs("p", { className: "mt-4 text-lg text-slate-400", children: [t.terms.lastUpdated, ": ", new Date().toLocaleDateString()] })] }), _jsx("div", { className: "mt-12 text-base text-slate-400 space-y-8 bg-slate-900 p-8 sm:p-12 rounded-lg border border-slate-800", children: t.terms.sections.map((section, index) => (_jsxs("div", { className: "space-y-4", children: [_jsx("h2", { className: "text-2xl font-bold text-white", children: section.title }), _jsx("p", { children: section.content }), section.list && (_jsx("ul", { className: "list-disc list-inside space-y-2", children: section.list.map((item, itemIndex) => (_jsx("li", { children: item }, itemIndex))) }))] }, index))) }), _jsx("div", { className: "mt-12 text-center", children: _jsxs("a", { href: "#home", className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors", children: [_jsx(ArrowLeftIcon, { "aria-hidden": "true", className: "h-4 w-4" }), t.terms.backToHome] }) })] }) }));
};
export default Terms;
'''

DATA_DELETION_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
const DataDeletion = () => {
    const { t } = useLanguage();
    return (_jsx("section", { id: "data-deletion", className: "bg-slate-950 py-20 sm:py-28", children: _jsxs("div", { className: "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8", children: [_jsxs("div", { className: "text-center", children: [_jsx("h1", { className: "text-4xl font-extrabold text-white sm:text-5xl", children: t.dataDeletion.title }), _jsxs("p", { className: "mt-4 text-lg text-slate-400", children: [t.dataDeletion.lastUpdated, ": ", new Date().toLocaleDateString()] })] }), _jsx("div", { className: "mt-12 text-base text-slate-400 space-y-8 bg-slate-900 p-8 sm:p-12 rounded-lg border border-slate-800", children: t.dataDeletion.sections.map((section, index) => (_jsxs("div", { className: "space-y-4", children: [_jsx("h2", { className: "text-2xl font-bold text-white", children: section.title }), _jsx("p", { children: section.content }), section.list && (_jsx("ul", { className: "list-disc list-inside space-y-2", children: section.list.map((item, itemIndex) => (_jsx("li", { children: item }, itemIndex))) }))] }, index))) }), _jsx("div", { className: "mt-12 text-center", children: _jsxs("a", { href: "#home", className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors", children: [_jsx(ArrowLeftIcon, { "aria-hidden": "true", className: "h-4 w-4" }), t.dataDeletion.backToHome] }) })] }) }));
};
export default DataDeletion;
'''


def patch_app(src: str) -> str:
    if "Checkout" not in src:
        src = src.replace(
            "import Android from '@/components/Android';",
            "import Android from '@/components/Android';\nimport Checkout from '@/components/Checkout';\nimport Services from '@/components/Services';",
        )
    src = src.replace(
        """const pages = {
    home: _jsx(HomePage, {}),
    about: _jsx(About, {}),
    contact: _jsx(Contact, {}),
    privacy: _jsx(Privacy, {}),
    terms: _jsx(Terms, {}),
    blog: _jsx(Blog, {}),
    technical: _jsx(Technical, {}),
    android: _jsx(Android, {}),
};""",
        """const pages = {
    home: _jsx(HomePage, {}),
    about: _jsx(About, {}),
    contact: _jsx(Contact, {}),
    privacy: _jsx(Privacy, {}),
    terms: _jsx(Terms, {}),
    blog: _jsx(Blog, {}),
    technical: _jsx(Technical, {}),
    android: _jsx(Android, {}),
    checkout: _jsx(Checkout, {}),
    services: _jsx(Services, {}),
};""",
    )
    return src


def patch_app_data_deletion(src: str) -> str:
    if "DataDeletion" not in src:
        src = src.replace(
            "import Terms from '@/components/Terms';",
            "import Terms from '@/components/Terms';\nimport DataDeletion from '@/components/DataDeletion';",
        )
    if "dataDeletion:" not in src:
        src = src.replace(
            "    terms: _jsx(Terms, {}),\n    blog:",
            "    terms: _jsx(Terms, {}),\n    dataDeletion: _jsx(DataDeletion, {}),\n    blog:",
        )
    return src


def patch_seo(src: str) -> str:
    if "'/checkout'" in src or '"/checkout"' in src:
        return src
    insert = """  '/services': {
    title: 'Products & Services — Bill Maniac',
    description: 'AI receipt scanning, private cloud expense database, analytics, exports, and support plans from PT. DEVINCI GROUP INDONESIA.',
    path: '/services',
    pageKey: 'services',
  },
  '/checkout': {
    title: 'Checkout — Subscribe to Bill Maniac',
    description: 'Choose Free, Pro, or Maniac and complete your yearly subscription request with PT. DEVINCI GROUP INDONESIA.',
    path: '/checkout',
    pageKey: 'checkout',
  },
"""
    # insert before '/about'
    return src.replace("  '/about': {", insert + "  '/about': {")


def patch_seo_data_deletion(src: str) -> str:
    if "'/data-deletion'" in src or '"/data-deletion"' in src:
        return src
    insert = """  '/data-deletion': {
    title: 'Data Deletion Request — Bill Maniac',
    description: 'How to delete your Bill Maniac account and data in the app or by email request.',
    path: '/data-deletion',
    pageKey: 'dataDeletion',
  },
"""
    return src.replace("  '/privacy': {", insert + "  '/privacy': {")


def replace_contact_block(raw: str, old: str, new: str) -> str:
    if old not in raw:
        raise SystemExit(f"contact block not found:\n{old[:80]}")
    return raw.replace(old, new, 1)


def patch_pricing_plan_limits(raw: str) -> str:
    """Align FREE/PRO scan limits and FREE feature lists across locales."""
    replacements = [
        # English — pricing page tiers
        (
            """                    "features": [
                        {
                            "text": "Unlimited Manual Expenses"
                        },
                        {
                            "text": "Secure cloud sync"
                        },
                        {
                            "text": "30 AI Receipt Scans / month"
                        },
                        {
                            "text": "Basic Categorization"
                        },
                        {
                            "text": "Private receipt cloud storage"
                        },
                        {
                            "text": "Private expense database"
                        }
                    ],""",
            """                    "features": [
                        {
                            "text": "Secure cloud sync"
                        },
                        {
                            "text": "20 AI Receipt Scans / month"
                        },
                        {
                            "text": "Basic Categorization"
                        },
                        {
                            "text": "Private receipt cloud storage"
                        }
                    ],""",
        ),
        ('"text": "120 AI Receipt Scans / month"', '"text": "80 AI Receipt Scans / month"'),
        # English — homepage product cards
        (
            """                    "features": [
                        "Unlimited manual expenses",
                        "Secure cloud sync",
                        "30 AI receipt scans / month",
                        "Private receipt storage"
                    ]""",
            """                    "features": [
                        "Secure cloud sync",
                        "20 AI receipt scans / month",
                        "Basic categorization",
                        "Private receipt cloud storage"
                    ]""",
        ),
        ('"120 AI receipt scans / month"', '"80 AI receipt scans / month"'),
        # French — pricing page tiers
        (
            """                    "features": [
                        {
                            "text": "Dépenses manuelles illimitées"
                        },
                        {
                            "text": "Synchronisation cloud sécurisée"
                        },
                        {
                            "text": "30 numérisations de reçus IA / mois"
                        },
                        {
                            "text": "Catégorisation de base"
                        },
                        {
                            "text": "Stockage cloud privé des reçus"
                        },
                        {
                            "text": "Base de données privée des dépenses"
                        }
                    ],""",
            """                    "features": [
                        {
                            "text": "Synchronisation cloud sécurisée"
                        },
                        {
                            "text": "20 numérisations de reçus IA / mois"
                        },
                        {
                            "text": "Catégorisation de base"
                        },
                        {
                            "text": "Stockage cloud privé des reçus"
                        }
                    ],""",
        ),
        (
            '"text": "120 numérisations de reçus IA / mois"',
            '"text": "80 numérisations de reçus IA / mois"',
        ),
        # French — homepage product cards
        (
            """                    "features": [
                        "Dépenses manuelles illimitées",
                        "Sync cloud sécurisée",
                        "30 scans IA / mois",
                        "Stockage privé des reçus"
                    ]""",
            """                    "features": [
                        "Sync cloud sécurisée",
                        "20 scans IA / mois",
                        "Catégorisation de base",
                        "Stockage cloud privé des reçus"
                    ]""",
        ),
        ('"120 scans IA / mois"', '"80 scans IA / mois"'),
        # Spanish — pricing page tiers
        (
            """                    "features": [
                        {
                            "text": "Gastos manuales ilimitados"
                        },
                        {
                            "text": "Sincronización segura en la nube"
                        },
                        {
                            "text": "30 escaneos de recibos con IA / mes"
                        },
                        {
                            "text": "Categorización básica"
                        },
                        {
                            "text": "Uso de almacenamiento privado de recibos"
                        },
                        {
                            "text": "Base de datos privada de gastos"
                        }
                    ],""",
            """                    "features": [
                        {
                            "text": "Sincronización segura en la nube"
                        },
                        {
                            "text": "20 escaneos de recibos con IA / mes"
                        },
                        {
                            "text": "Categorización básica"
                        },
                        {
                            "text": "Uso de almacenamiento privado de recibos"
                        }
                    ],""",
        ),
        (
            '"text": "120 escaneos de recibos con IA / mes"',
            '"text": "80 escaneos de recibos con IA / mes"',
        ),
        # Spanish — homepage product cards
        (
            """                    "features": [
                        "Gastos manuales ilimitados",
                        "Sincronización cloud segura",
                        "30 escaneos IA / mes",
                        "Almacenamiento privado de recibos"
                    ]""",
            """                    "features": [
                        "Sincronización cloud segura",
                        "20 escaneos IA / mes",
                        "Categorización básica",
                        "Almacenamiento privado de recibos"
                    ]""",
        ),
        ('"120 escaneos IA / mes"', '"80 escaneos IA / mes"'),
        # Indonesian — homepage product cards
        (
            """                    "features": [
                        "Pengeluaran manual tidak terbatas",
                        "Sinkronisasi cloud yang aman",
                        "30 pemindaian struk AI / bulan",
                        "Penyimpanan struk pribadi"
                    ]""",
            """                    "features": [
                        "Sinkronisasi cloud yang aman",
                        "20 pemindaian struk AI / bulan",
                        "Kategorisasi dasar",
                        "Penyimpanan struk cloud pribadi"
                    ]""",
        ),
        ('"120 pemindaian struk AI / bulan"', '"80 pemindaian struk AI / bulan"'),
        # Services page bullets (all locales in this patch file)
        ('"120 scans/month on Pro"', '"80 scans/month on Pro"'),
        ('"120 scans/mois en Pro"', '"80 scans/mois en Pro"'),
        ('"120 escaneos/mes en Pro"', '"80 escaneos/mes en Pro"'),
    ]
    for old, new in replacements:
        if old not in raw:
            raise SystemExit(f"pricing plan patch target not found:\n{old[:120]}...")
        raw = raw.replace(old, new, 1)
    return raw


def patch_pro_annual_price(raw: str) -> str:
    """Set Pro plan display price to $18/year (and 18€ in FR/ES)."""
    replacements = [
        ('"name": "PRO MODE",\n                    "price": "$12"', '"name": "PRO MODE",\n                    "price": "$18"'),
        ('"name": "MODE PRO",\n                    "price": "12€"', '"name": "MODE PRO",\n                    "price": "18€"'),
        ('"name": "MODE PRO",\n                    "price": "$12"', '"name": "MODE PRO",\n                    "price": "$18"'),
        ('"name": "MODO PRO",\n                    "price": "12€"', '"name": "MODO PRO",\n                    "price": "18€"'),
        ('planPro: "PRO MODE — $12/year"', 'planPro: "PRO MODE — $18/year"'),
        ('planPro: "MODE PRO — 12€/an"', 'planPro: "MODE PRO — 18€/an"'),
        ('planPro: "MODO PRO — 12€/año"', 'planPro: "MODO PRO — 18€/año"'),
    ]
    for old, new in replacements:
        if old in raw:
            raw = raw.replace(old, new, 1)
    if '"price": "$12"' in raw and '"name": "PRO MODE"' in raw:
        raise SystemExit("Pro price patch incomplete: $12 still present for PRO MODE")
    return raw


def patch_translations(raw: str) -> str:
    # header keys
    raw = raw.replace(
        """header: {
            features: "Features",
            android: "Android",
            pricing: "Pricing",
            faq: "FAQ",
            login: "Login",
            signUp: "Get Started",
            technical: "Technical",
        },""",
        """header: {
            services: "Services",
            features: "Features",
            android: "Android",
            pricing: "Pricing",
            checkout: "Checkout",
            faq: "FAQ",
            contact: "Contact",
            login: "Login",
            signUp: "Get Started",
            technical: "Technical",
        },""",
        1,
    )
    # FR header - find French version
    raw = raw.replace(
        """header: {
            features: "Fonctionnalités",
            android: "Android",
            pricing: "Tarifs",
            faq: "FAQ",
            login: "Connexion",
            signUp: "Commencer",
            technical: "Technique",
        },""",
        """header: {
            services: "Services",
            features: "Fonctionnalités",
            android: "Android",
            pricing: "Tarifs",
            checkout: "Paiement",
            faq: "FAQ",
            contact: "Contact",
            login: "Connexion",
            signUp: "Commencer",
            technical: "Technique",
        },""",
        1,
    )
    raw = raw.replace(
        """header: {
            features: "Funcionalidades",
            android: "Android",
            pricing: "Precios",
            faq: "FAQ",
            login: "Iniciar Sesión",
            signUp: "Empezar",
            technical: "Técnico",
        },""",
        """header: {
            services: "Servicios",
            features: "Funcionalidades",
            android: "Android",
            pricing: "Precios",
            checkout: "Checkout",
            faq: "FAQ",
            contact: "Contacto",
            login: "Iniciar Sesión",
            signUp: "Empezar",
            technical: "Técnico",
        },""",
        1,
    )

    # footer nav additions + copyright year
    raw = raw.replace(
        'copyright: "Copyright PT. DEVINCI GROUP INDONESIA 2025"',
        'copyright: "Copyright PT. DEVINCI GROUP INDONESIA 2026"',
    )
    for old, new in [
        (
            """nav: {
                features: "Features",
                android: "Android App",
                pricing: "Pricing",
                login: "Login",
                about: "About Us",
                contact: "Contact",
                blog: "Blog",
                privacy: "Privacy Policy",
                terms: "Terms of Service",
                technical: "Technical Overview",
            }""",
            """nav: {
                services: "Services",
                features: "Features",
                android: "Android App",
                pricing: "Pricing",
                checkout: "Checkout",
                login: "Login",
                about: "About Us",
                contact: "Contact",
                blog: "Blog",
                privacy: "Privacy Policy",
                terms: "Terms of Service",
                technical: "Technical Overview",
            }""",
        ),
        (
            """nav: {
                features: "Fonctionnalités",
                android: "App Android",
                pricing: "Tarifs",
                login: "Connexion",
                about: "À propos",
                contact: "Contact",
                blog: "Blog",
                privacy: "Politique de confidentialité",
                terms: "Conditions d'utilisation",
                technical: "Aperçu Technique",
            }""",
            """nav: {
                services: "Services",
                features: "Fonctionnalités",
                android: "App Android",
                pricing: "Tarifs",
                checkout: "Paiement",
                login: "Connexion",
                about: "À propos",
                contact: "Contact",
                blog: "Blog",
                privacy: "Politique de confidentialité",
                terms: "Conditions d'utilisation",
                technical: "Aperçu Technique",
            }""",
        ),
        (
            """nav: {
                features: "Funcionalidades",
                android: "App Android",
                pricing: "Precios",
                login: "Iniciar Sesión",
                about: "Sobre Nosotros",
                contact: "Contacto",
                blog: "Blog",
                privacy: "Política de Privacidad",
                terms: "Términos de Servicio",
                technical: "Resumen Técnico",
            }""",
            """nav: {
                services: "Servicios",
                features: "Funcionalidades",
                android: "App Android",
                pricing: "Precios",
                checkout: "Checkout",
                login: "Iniciar Sesión",
                about: "Sobre Nosotros",
                contact: "Contacto",
                blog: "Blog",
                privacy: "Política de Privacidad",
                terms: "Términos de Servicio",
                technical: "Resumen Técnico",
            }""",
        ),
    ]:
        if old in raw:
            raw = raw.replace(old, new, 1)
        else:
            print("WARN footer nav variant missing")
            print(old[:120])

    # about: add office/phone labels before backToHome in each lang
    about_patches = [
        (
            """developerName: "Denis Guillot on LinkedIn",
            backToHome: "Back to Home",
        },
        contact: {
            title: "Contact Us",""",
            """developerName: "Denis Guillot on LinkedIn",
            officeLabel: "Office",
            phoneLabel: "Phone",
            backToHome: "Back to Home",
        },
        contact: {
            title: "Contact Us",""",
        ),
        (
            """developerName: "Denis Guillot sur LinkedIn",
            backToHome: "Retour à l'accueil",
        },
        contact: {
            title: "Nous contacter",""",
            """developerName: "Denis Guillot sur LinkedIn",
            officeLabel: "Bureau",
            phoneLabel: "Téléphone",
            backToHome: "Retour à l'accueil",
        },
        contact: {
            title: "Nous contacter",""",
        ),
        (
            """developerName: "Denis Guillot en LinkedIn",
            backToHome: "Volver al Inicio",
        },
        contact: {
            title: "Contáctanos",""",
            """developerName: "Denis Guillot en LinkedIn",
            officeLabel: "Oficina",
            phoneLabel: "Teléfono",
            backToHome: "Volver al Inicio",
        },
        contact: {
            title: "Contáctanos",""",
        ),
    ]
    for old, new in about_patches:
        if old not in raw:
            continue
        raw = raw.replace(old, new, 1)

    contact_en_old = """contact: {
            title: "Contact Us",
            intro: "We'd love to hear from you. Reach out with any questions or feedback.",
            businessLabel: "For business inquiries and support, please email us at:",
            generalLabel: "For general inquiries, you can also reach us at:",
            backToHome: "Back to Home",
        },"""
    contact_en_new = """contact: {
            title: "Contact Us",
            intro: "Reach Bill Maniac / PT. DEVINCI GROUP INDONESIA for sales, subscriptions, and support.",
            officeLabel: "Office address",
            phoneLabel: "Phone / WhatsApp",
            emailLabel: "Email",
            businessLabel: "Business & billing",
            generalLabel: "General inquiries",
            whatsappCta: "Chat on WhatsApp",
            checkoutCta: "Go to Checkout",
            hours: "Business hours: Mon–Fri, 09:00–18:00 WIB.",
            backToHome: "Back to Home",
        },"""
    contact_fr_old = """contact: {
            title: "Nous contacter",
            intro: "Nous serions ravis d'avoir de vos nouvelles. Contactez-nous pour toute question ou commentaire.",
            businessLabel: "Pour les demandes commerciales et le support, veuillez nous envoyer un e-mail à :",
            generalLabel: "Pour les demandes générales, vous pouvez également nous joindre à :",
            backToHome: "Retour à l'accueil",
        },"""
    contact_fr_new = """contact: {
            title: "Nous contacter",
            intro: "Contactez Bill Maniac / PT. DEVINCI GROUP INDONESIA pour les ventes, abonnements et support.",
            officeLabel: "Adresse du bureau",
            phoneLabel: "Téléphone / WhatsApp",
            emailLabel: "E-mail",
            businessLabel: "Commercial & facturation",
            generalLabel: "Demandes générales",
            whatsappCta: "Discuter sur WhatsApp",
            checkoutCta: "Aller au paiement",
            hours: "Horaires : lun–ven, 09:00–18:00 WIB.",
            backToHome: "Retour à l'accueil",
        },"""
    contact_es_old = """contact: {
            title: "Contáctanos",
            intro: "Nos encantaría saber de ti. Contáctanos con cualquier pregunta o comentario.",
            businessLabel: "Para consultas comerciales y soporte, por favor envíanos un correo electrónico a:",
            generalLabel: "Para consultas generales, también puedes contactarnos en:",
            backToHome: "Volver al Inicio",
        },"""
    contact_es_new = """contact: {
            title: "Contáctanos",
            intro: "Contacta a Bill Maniac / PT. DEVINCI GROUP INDONESIA para ventas, suscripciones y soporte.",
            officeLabel: "Dirección de la oficina",
            phoneLabel: "Teléfono / WhatsApp",
            emailLabel: "Correo",
            businessLabel: "Negocios y facturación",
            generalLabel: "Consultas generales",
            whatsappCta: "Chatear por WhatsApp",
            checkoutCta: "Ir al checkout",
            hours: "Horario: lun–vie, 09:00–18:00 WIB.",
            backToHome: "Volver al Inicio",
        },"""
    raw = replace_contact_block(raw, contact_en_old, contact_en_new)
    raw = replace_contact_block(raw, contact_fr_old, contact_fr_new)
    raw = replace_contact_block(raw, contact_es_old, contact_es_new)

    # pricing notes + CTAs for paid plans
    raw = raw.replace(
        '{ text: "Private receipt storage" }], cta: "Go Pro", isPopular: true }',
        '{ text: "Private receipt storage" }], cta: "Checkout — Pro", isPopular: true }',
        1,
    )
    raw = raw.replace(
        '{ text: "Private receipt storage" }], cta: "Go Maniac Mode", isPopular: false }',
        '{ text: "Private receipt storage" }], cta: "Checkout — Maniac", isPopular: false }',
        1,
    )
    raw = raw.replace(
        'subTitle: "Start for free, then upgrade when you\'re ready for more power.",',
        'subTitle: "Start for free, then upgrade when you\'re ready for more power.",\n            mostPopular: "Most Popular",\n            checkoutNote: "Paid plans: complete checkout by email or WhatsApp. We activate your yearly Pro or Maniac access after payment confirmation.",',
        1,
    )

    # French / Spanish CTAs
    raw = raw.replace('cta: "Passer Pro", isPopular: true', 'cta: "Paiement — Pro", isPopular: true', 1)
    raw = raw.replace('cta: "Passer en mode Maniac", isPopular: false', 'cta: "Paiement — Maniac", isPopular: false', 1)
    raw = raw.replace(
        'subTitle: "Commencez gratuitement, puis passez à la version supérieure lorsque vous êtes prêt pour plus de puissance.",',
        'subTitle: "Commencez gratuitement, puis passez à la version supérieure lorsque vous êtes prêt pour plus de puissance.",\n            mostPopular: "Le plus populaire",\n            checkoutNote: "Offres payantes : finalisez via e-mail ou WhatsApp. Nous activons votre accès annuel après confirmation du paiement.",',
        1,
    )
    raw = raw.replace('cta: "Pasar a Pro", isPopular: true', 'cta: "Checkout — Pro", isPopular: true', 1)
    raw = raw.replace('cta: "Pasar a Modo Maniac", isPopular: false', 'cta: "Checkout — Maniac", isPopular: false', 1)
    raw = raw.replace(
        'subTitle: "Comienza gratis, luego mejora cuando estés listo para más potencia.",',
        'subTitle: "Comienza gratis, luego mejora cuando estés listo para más potencia.",\n            mostPopular: "Más popular",\n            checkoutNote: "Planes de pago: completa el checkout por correo o WhatsApp. Activamos tu acceso anual tras confirmar el pago.",',
        1,
    )

    # Insert services + checkout translation objects before each language's about block... easier: before contact after about already done.
    # Add after each contact block's closing - actually insert before blog after contact.
    services_en = """
        services: {
            eyebrow: "Products & Services",
            title: "What Bill Maniac offers",
            intro: "AI expense management for freelancers, finance teams, and companies — with private cloud storage on Cloudflare.",
            items: [
                { title: "AI Receipt Scanning", text: "Capture or upload JPG/PNG/PDF receipts on web and Android. Gemini extracts vendor, date, totals, and category.", bullets: ["Camera & batch upload", "80 scans/month on Pro", "500 scans/month on Maniac"] },
                { title: "Private Cloud Expense Database", text: "Your bills and receipt files stay in your Bill Maniac Pro cloud (Cloudflare D1 + R2), not a shared public drive.", bullets: ["Encrypted-in-transit access", "Per-account isolation", "PIN lock on clients"] },
                { title: "Analytics & Budgets", text: "Track spending by period, category, and vendor. Set budgets and spot trends early.", bullets: ["Weekly / 15-day / monthly views", "Category breakdowns", "Vendor rankings"] },
                { title: "Exports & Reporting", text: "Download CSV or polished Excel reports, and printable monthly documents for accounting.", bullets: ["CSV & XLSX export", "Monthly reports", "Receipt image links in spreadsheets"] },
            ],
            ctaPricing: "See Prices",
            ctaCheckout: "Start Checkout",
            backToHome: "Back to Home",
        },
        checkout: {
            eyebrow: "Checkout",
            title: "Subscribe to Bill Maniac",
            intro: "Choose your plan and send a yearly subscription request. We confirm payment details by WhatsApp or email, then activate your account.",
            selectPlan: "Select a plan",
            planFree: "FREE",
            planPro: "PRO MODE — $18/year",
            planManiac: "MANIAC MODE — $60/year",
            fieldPlan: "Plan",
            fieldName: "Full name",
            fieldEmail: "Email",
            fieldCompany: "Company (optional)",
            fieldNotes: "Notes",
            placeholderName: "Your name",
            placeholderEmail: "you@company.com",
            placeholderCompany: "Company name",
            placeholderNotes: "Preferred payment method, invoice needs, etc.",
            whatsappCta: "Send via WhatsApp",
            emailCta: "Send via Email",
            help: "Online card checkout is coming soon. For now we complete yearly fees manually with payment instructions.",
            summaryTitle: "Order summary",
            summaryBullets: ["Yearly access to Bill Maniac Pro cloud", "Activation after payment confirmation", "Support from PT. DEVINCI GROUP INDONESIA"],
            sellerTitle: "Seller",
            phoneLabel: "Phone",
            emailLabel: "Email",
            messageIntro: "Hello Bill Maniac team, I would like to subscribe:",
            messageOutro: "Please send payment instructions. Thank you.",
            emailSubject: "Bill Maniac subscription request — {plan}",
            backToPricing: "Back to Pricing",
        },"""
    services_fr = """
        services: {
            eyebrow: "Produits & Services",
            title: "Ce que propose Bill Maniac",
            intro: "Gestion des dépenses par IA pour indépendants, équipes finance et entreprises — avec stockage cloud privé sur Cloudflare.",
            items: [
                { title: "Scan de reçus par IA", text: "Capturez ou téléversez des reçus JPG/PNG/PDF sur le web et Android. Gemini extrait commerçant, date, totaux et catégorie.", bullets: ["Caméra & lots", "80 scans/mois en Pro", "500 scans/mois en Maniac"] },
                { title: "Base de dépenses cloud privée", text: "Vos factures et fichiers restent dans votre cloud Bill Maniac Pro (Cloudflare D1 + R2).", bullets: ["Accès chiffré en transit", "Isolation par compte", "Verrouillage PIN"] },
                { title: "Analytique & budgets", text: "Suivez les dépenses par période, catégorie et fournisseur.", bullets: ["Vues hebdo / 15 jours / mois", "Répartition par catégorie", "Classement des fournisseurs"] },
                { title: "Exports & rapports", text: "CSV, Excel et rapports mensuels pour la comptabilité.", bullets: ["Export CSV & XLSX", "Rapports mensuels", "Liens d'images de reçus"] },
            ],
            ctaPricing: "Voir les tarifs",
            ctaCheckout: "Commencer le paiement",
            backToHome: "Retour à l'accueil",
        },
        checkout: {
            eyebrow: "Paiement",
            title: "S'abonner à Bill Maniac",
            intro: "Choisissez votre offre et envoyez une demande d'abonnement annuel. Nous confirmons le paiement par WhatsApp ou e-mail, puis activons votre compte.",
            selectPlan: "Choisir une offre",
            planFree: "GRATUIT",
            planPro: "MODE PRO — 18€/an",
            planManiac: "MODE MANIAC — 60€/an",
            fieldPlan: "Offre",
            fieldName: "Nom complet",
            fieldEmail: "E-mail",
            fieldCompany: "Société (optionnel)",
            fieldNotes: "Notes",
            placeholderName: "Votre nom",
            placeholderEmail: "vous@entreprise.com",
            placeholderCompany: "Nom de la société",
            placeholderNotes: "Mode de paiement, facture, etc.",
            whatsappCta: "Envoyer via WhatsApp",
            emailCta: "Envoyer par e-mail",
            help: "Le paiement par carte en ligne arrive bientôt. Pour l'instant les frais annuels sont finalisés manuellement avec instructions de paiement.",
            summaryTitle: "Récapitulatif",
            summaryBullets: ["Accès annuel au cloud Bill Maniac Pro", "Activation après confirmation de paiement", "Support PT. DEVINCI GROUP INDONESIA"],
            sellerTitle: "Vendeur",
            phoneLabel: "Téléphone",
            emailLabel: "E-mail",
            messageIntro: "Bonjour l'équipe Bill Maniac, je souhaite m'abonner :",
            messageOutro: "Merci de m'envoyer les instructions de paiement.",
            emailSubject: "Demande d'abonnement Bill Maniac — {plan}",
            backToPricing: "Retour aux tarifs",
        },"""
    services_es = """
        services: {
            eyebrow: "Productos y servicios",
            title: "Qué ofrece Bill Maniac",
            intro: "Gestión de gastos con IA para freelancers, equipos financieros y empresas — con almacenamiento cloud privado en Cloudflare.",
            items: [
                { title: "Escaneo de recibos con IA", text: "Captura o sube recibos JPG/PNG/PDF en web y Android. Gemini extrae comercio, fecha, totales y categoría.", bullets: ["Cámara y lotes", "80 escaneos/mes en Pro", "500 escaneos/mes en Maniac"] },
                { title: "Base de gastos en cloud privado", text: "Tus facturas y archivos permanecen en tu cloud Bill Maniac Pro (Cloudflare D1 + R2).", bullets: ["Acceso cifrado en tránsito", "Aislamiento por cuenta", "Bloqueo PIN"] },
                { title: "Analítica y presupuestos", text: "Controla el gasto por periodo, categoría y proveedor.", bullets: ["Vistas semanal / 15 días / mes", "Desglose por categoría", "Ranking de proveedores"] },
                { title: "Exportaciones e informes", text: "CSV, Excel e informes mensuales para contabilidad.", bullets: ["Exportación CSV y XLSX", "Informes mensuales", "Enlaces a imágenes de recibos"] },
            ],
            ctaPricing: "Ver precios",
            ctaCheckout: "Ir al checkout",
            backToHome: "Volver al inicio",
        },
        checkout: {
            eyebrow: "Checkout",
            title: "Suscribirse a Bill Maniac",
            intro: "Elige tu plan y envía una solicitud de suscripción anual. Confirmamos el pago por WhatsApp o correo y luego activamos tu cuenta.",
            selectPlan: "Selecciona un plan",
            planFree: "GRATIS",
            planPro: "MODO PRO — 18€/año",
            planManiac: "MODO MANIAC — 60€/año",
            fieldPlan: "Plan",
            fieldName: "Nombre completo",
            fieldEmail: "Correo",
            fieldCompany: "Empresa (opcional)",
            fieldNotes: "Notas",
            placeholderName: "Tu nombre",
            placeholderEmail: "tu@empresa.com",
            placeholderCompany: "Nombre de la empresa",
            placeholderNotes: "Método de pago, factura, etc.",
            whatsappCta: "Enviar por WhatsApp",
            emailCta: "Enviar por correo",
            help: "El pago con tarjeta online llegará pronto. Por ahora las cuotas anuales se completan manualmente con instrucciones de pago.",
            summaryTitle: "Resumen",
            summaryBullets: ["Acceso anual al cloud Bill Maniac Pro", "Activación tras confirmar el pago", "Soporte de PT. DEVINCI GROUP INDONESIA"],
            sellerTitle: "Vendedor",
            phoneLabel: "Teléfono",
            emailLabel: "Correo",
            messageIntro: "Hola equipo Bill Maniac, quiero suscribirme:",
            messageOutro: "Por favor envíen instrucciones de pago. Gracias.",
            emailSubject: "Solicitud de suscripción Bill Maniac — {plan}",
            backToPricing: "Volver a precios",
        },"""

    # Insert services/checkout after each contact block
    raw = raw.replace(contact_en_new, contact_en_new + services_en, 1)
    raw = raw.replace(contact_fr_new, contact_fr_new + services_fr, 1)
    raw = raw.replace(contact_es_new, contact_es_new + services_es, 1)

    raw = patch_pricing_plan_limits(raw)
    raw = patch_pro_annual_price(raw)
    raw = patch_terms_in_translations(raw)
    return patch_data_deletion_in_translations(raw)


def patch_language_context(src: str) -> str:
    # ensure language is exported from context if checkout needs it
    if "language," in src or "language }" in src or "language:" in src:
        return src
    # try to add language to hook return
    if "export function useLanguage" in src or "useLanguage =" in src:
        # decode and inspect
        pass
    return src


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r'(<script type="importmap">)(.*?)(</script>)', html, re.S)
    assert m
    imap = json.loads(m.group(2))
    imports = imap["imports"]

    def get(key: str) -> str:
        return base64.b64decode(imports[key].split(",", 1)[1]).decode("utf-8")

    def set_(key: str, src: str) -> None:
        imports[key] = b64(src)

    set_("@/components/Contact", CONTACT_SRC)
    set_("@/components/Checkout", CHECKOUT_SRC)
    set_("@/components/Services", SERVICES_SRC)
    set_("@/components/Pricing", PRICING_SRC)
    set_("@/components/About", ABOUT_SRC)
    set_("@/components/Footer", FOOTER_SRC)
    set_("@/components/Header", HEADER_SRC)
    set_("@/components/Terms", TERMS_SRC)
    set_("@/components/DataDeletion", DATA_DELETION_SRC)
    set_("@/App", patch_app_data_deletion(patch_app(get("@/App"))))
    set_("@/seo", patch_seo_data_deletion(patch_seo(get("@/seo"))))
    set_("@/translations", patch_translations(get("@/translations")))

    print("LanguageContext already exports language")

    imap["imports"] = imports
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print("index.html patched", INDEX.stat().st_size)


if __name__ == "__main__":
    main()
