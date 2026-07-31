#!/usr/bin/env python3
"""Add APK download CTA on /android, homepage hero, and update copy in dist/index.html."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"
APK_HREF = "https://billmaniac.win/downloads/billmaniac-pro.apk"
APK_FILENAME = "billmaniac-pro.apk"
RELATIVE_APK_HREF = "/downloads/billmaniac-pro.apk"

FOOTER_NAV_OLD = """    if (!href || href.startsWith("//") || href.includes("://")) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();"""

FOOTER_NAV_NEW = """    if (!href || href.startsWith("//") || href.includes("://")) return;
    if (
      a.hasAttribute("download") ||
      href.startsWith("/downloads/") ||
      /^\\/downloads\\//.test(href) ||
      /\\.(apk|aab|zip|pdf)$/i.test(href)
    ) {
      return;
    }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();"""

OLD_BUTTONS = """              _jsxs("div", {
                className: "mt-8 flex flex-col sm:flex-row items-center justify-center gap-3",
                children: [
                  _jsx("a", {
                    href: "https://my.billmaniac.win",
                    className: "inline-flex items-center justify-center rounded-md bg-brand-primary px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-brand-dark transition-colors",
                    children: a.ctaWeb
                  }),
                  _jsx("a", {
                    href: "#android-features",
                    className: "inline-flex items-center justify-center rounded-md bg-slate-800 px-6 py-3 text-sm font-semibold text-white border border-slate-700 hover:bg-slate-700 transition-colors",
                    children: a.ctaFeatures
                  })
                ]
              }),
              _jsx("p", { className: "mt-4 text-sm text-slate-500", children: a.note })"""

NEW_BUTTONS = f"""              _jsxs("div", {{
                className: "mt-8 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3",
                children: [
                  _jsx("a", {{
                    href: "{APK_HREF}",
                    className: "inline-flex items-center justify-center rounded-md bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 transition-colors w-full sm:w-auto min-h-[44px]",
                    children: a.ctaApk || "Download Android App"
                  }}),
                  _jsx("a", {{
                    href: "https://my.billmaniac.win",
                    className: "inline-flex items-center justify-center rounded-md bg-brand-primary px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-brand-dark transition-colors",
                    children: a.ctaWeb
                  }}),
                  _jsx("a", {{
                    href: "#android-features",
                    className: "inline-flex items-center justify-center rounded-md bg-slate-800 px-6 py-3 text-sm font-semibold text-white border border-slate-700 hover:bg-slate-700 transition-colors",
                    children: a.ctaFeatures
                  }})
                ]
              }}),
              _jsx("p", {{ className: "mt-4 text-sm text-slate-500", children: a.apkMeta || a.note }}),
              _jsx("p", {{ className: "mt-2 text-sm text-slate-500", children: a.note }})"""

HERO_OLD = """            _jsx("div", { className: "mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start", children: _jsx("a", { href: "https://my.billmaniac.win", className: "w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-brand-primary rounded-lg hover:bg-brand-dark transition-colors shadow-lg", children: t.hero.cta }) }),
            _jsx("p", { className: "mt-4 text-sm text-slate-500", children: t.hero.socialProof })"""

HERO_NEW = f"""            _jsxs("div", {{
              className: "mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start",
              children: [
                _jsx("a", {{
                  href: "{APK_HREF}",
                  className: "w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-emerald-600 rounded-lg hover:bg-emerald-500 transition-colors shadow-lg min-h-[48px]",
                  children: t.hero.ctaApk || "Download Android App"
                }}),
                _jsx("a", {{
                  href: "https://my.billmaniac.win",
                  className: "w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-brand-primary rounded-lg hover:bg-brand-dark transition-colors shadow-lg min-h-[48px]",
                  children: t.hero.cta
                }})
              ]
            }}),
            _jsx("p", {{ className: "mt-4 text-sm text-slate-500", children: t.hero.apkMeta || t.hero.socialProof }}),
            _jsx("p", {{ className: "mt-2 text-sm text-slate-500", children: t.hero.socialProof }})"""

TRANSLATION_PATCHES = [
    (
        '"ctaFeatures": "See Android Features",',
        '"ctaFeatures": "See Android Features",\n'
        '            "ctaApk": "Download Android APK",\n'
        '            "apkMeta": "Version 0.1.4 · direct install (enable Install unknown apps if prompted).",',
    ),
    (
        '"note": "Android APK / Play listing coming soon. Sign in on web today with email or Google — the same account works on Android."',
        '"note": "Use the same email or Google account on Android and web. Google Play internal testing link coming soon."',
    ),
    (
        '"ctaFeatures": "Voir les fonctions Android",',
        '"ctaFeatures": "Voir les fonctions Android",\n'
        '            "ctaApk": "Télécharger l’APK Android",\n'
        '            "apkMeta": "Version 0.1.4 · installation directe (autorisez les sources inconnues si demandé).",',
    ),
    (
        '"note": "APK / fiche Play bientôt disponibles. Connectez-vous sur le web par e-mail ou Google — le même compte fonctionne sur Android."',
        '"note": "Utilisez le même compte e-mail ou Google sur Android et le web. Lien de test Google Play bientôt disponible."',
    ),
    (
        '"ctaFeatures": "Ver funciones Android",',
        '"ctaFeatures": "Ver funciones Android",\n'
        '            "ctaApk": "Descargar APK Android",\n'
        '            "apkMeta": "Versión 0.1.4 · instalación directa (habilite orígenes desconocidos si se solicita).",',
    ),
    (
        '"note": "APK / ficha de Play próximamente. Inicia sesión en la web con correo o Google — la misma cuenta funciona en Android."',
        '"note": "Usa la misma cuenta de correo o Google en Android y la web. Enlace de prueba en Google Play próximamente."',
    ),
    (
        '"ctaFeatures": "Lihat Fitur Android",',
        '"ctaFeatures": "Lihat Fitur Android",\n'
        '            "ctaApk": "Unduh APK Android",\n'
        '            "apkMeta": "Versi 0.1.4 · instalasi langsung (izinkan aplikasi tidak dikenal jika diminta).",',
    ),
    (
        '"note": "APK Android / listing Play segera hadir. Masuk di web dengan email atau Google — akun yang sama berfungsi di Android."',
        '"note": "Gunakan akun email atau Google yang sama di Android dan web. Tautan uji Google Play segera hadir."',
    ),
    (
        '"cta": "Get Started for Free",',
        '"cta": "Get Started for Free",\n'
        '            "ctaApk": "Download Android App",\n'
        '            "apkMeta": "Version 0.1.4 · direct install on Android.",',
    ),
    (
        '"cta": "Commencez gratuitement",',
        '"cta": "Commencez gratuitement",\n'
        '            "ctaApk": "Télécharger l’app Android",\n'
        '            "apkMeta": "Version 0.1.4 · installation directe sur Android.",',
    ),
    (
        '"cta": "Empieza gratis",',
        '"cta": "Empieza gratis",\n'
        '            "ctaApk": "Descargar app Android",\n'
        '            "apkMeta": "Versión 0.1.4 · instalación directa en Android.",',
    ),
    (
        '"cta": "Mulai gratis",',
        '"cta": "Mulai gratis",\n'
        '            "ctaApk": "Unduh Aplikasi Android",\n'
        '            "apkMeta": "Versi 0.1.4 · instalasi langsung di Android.",',
    ),
]


CTA_STYLED_MARKER = "cta-btn-emerald"

DOWNLOAD_ICON = """export const DownloadIcon = ({ className }) => (_jsxs("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", className: className, children: [_jsx("path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" }), _jsx("polyline", { points: "7 10 12 15 17 10" }), _jsx("line", { x1: "12", y1: "15", x2: "12", y2: "3" })] }));"""

SPARKLES_ICON = """export const SparklesIcon = ({ className }) => (_jsxs("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", className: className, children: [_jsx("path", { d: "M12 3l1.4 5.2L18.5 10l-5.1 1.8L12 17l-1.4-5.2L5.5 10l5.1-1.8L12 3z" }), _jsx("path", { d: "M5 19l.9 1.8L7.7 22l-1.8.9L4 22l-.9-1.8L1.3 19l1.8-.9L4 16.2l.9 1.8z" })] }));"""

LOG_IN_ICON = """export const LogInIcon = ({ className }) => (_jsxs("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", className: className, children: [_jsx("path", { d: "M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" }), _jsx("polyline", { points: "10 17 15 12 10 7" }), _jsx("line", { x1: "15", y1: "12", x2: "3", y2: "12" })] }));"""

USER_PLUS_ICON = """export const UserPlusIcon = ({ className }) => (_jsxs("svg", { xmlns: "http://www.w3.org/2000/svg", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", className: className, children: [_jsx("path", { d: "M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" }), _jsx("circle", { cx: "8.5", cy: "7", r: "4" }), _jsx("line", { x1: "20", y1: "8", x2: "20", y2: "14" }), _jsx("line", { x1: "23", y1: "11", x2: "17", y2: "11" })] }));"""

BTN_EMERALD_LG = (
    "cta-btn-emerald group inline-flex items-center justify-center gap-2.5 rounded-xl px-8 py-4 "
    "text-lg font-bold text-white bg-gradient-to-b from-emerald-500 to-emerald-600 "
    "shadow-lg shadow-emerald-950/40 ring-1 ring-white/15 hover:from-emerald-400 hover:to-emerald-500 "
    "hover:shadow-emerald-500/30 active:scale-[0.98] transition-all duration-200 "
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 "
    "focus-visible:outline-emerald-400 w-full sm:w-auto min-h-[52px]"
)

BTN_PRIMARY_LG = (
    "cta-btn-primary group inline-flex items-center justify-center gap-2.5 rounded-xl px-8 py-4 "
    "text-lg font-bold text-white bg-gradient-to-b from-brand-primary to-brand-dark "
    "shadow-lg shadow-indigo-950/50 ring-1 ring-white/15 hover:from-indigo-500 hover:to-brand-dark "
    "hover:shadow-brand-primary/30 active:scale-[0.98] transition-all duration-200 "
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 "
    "focus-visible:outline-brand-primary w-full sm:w-auto min-h-[52px]"
)

BTN_EMERALD_SM = (
    "cta-btn-emerald group inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 "
    "text-sm font-semibold text-white bg-gradient-to-b from-emerald-500 to-emerald-600 "
    "shadow-lg shadow-emerald-950/40 ring-1 ring-white/15 hover:from-emerald-400 hover:to-emerald-500 "
    "hover:shadow-emerald-500/30 active:scale-[0.98] transition-all duration-200 "
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 "
    "focus-visible:outline-emerald-400 w-full sm:w-auto min-h-[44px]"
)

BTN_PRIMARY_SM = (
    "cta-btn-primary group inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 "
    "text-sm font-semibold text-white bg-gradient-to-b from-brand-primary to-brand-dark "
    "shadow-lg shadow-indigo-950/50 ring-1 ring-white/15 hover:from-indigo-500 hover:to-brand-dark "
    "hover:shadow-brand-primary/30 active:scale-[0.98] transition-all duration-200 "
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 "
    "focus-visible:outline-brand-primary w-full sm:w-auto min-h-[44px]"
)

BTN_GHOST_SM = (
    "cta-btn-ghost group inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 "
    "text-sm font-semibold text-white bg-slate-800/90 border border-slate-600/80 "
    "shadow-md shadow-black/20 ring-1 ring-white/5 hover:bg-slate-700 hover:border-slate-500 "
    "active:scale-[0.98] transition-all duration-200 w-full sm:w-auto min-h-[44px]"
)

HERO_BUTTONS_PLAIN = f"""            _jsxs("div", {{
              className: "mt-10 flex flex-col sm:flex-row gap-4 justify-center lg:justify-start",
              children: [
                _jsx("a", {{
                  href: "{APK_HREF}",
                  className: "w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-emerald-600 rounded-lg hover:bg-emerald-500 transition-colors shadow-lg min-h-[48px]",
                  children: t.hero.ctaApk || "Download Android App"
                }}),
                _jsx("a", {{
                  href: "https://my.billmaniac.win",
                  className: "w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-brand-primary rounded-lg hover:bg-brand-dark transition-colors shadow-lg min-h-[48px]",
                  children: t.hero.cta
                }})
              ]
            }}),"""

HERO_BUTTONS_STYLED = f"""            _jsxs("div", {{
              className: "mt-10 flex flex-col sm:flex-row flex-wrap gap-4 justify-center lg:justify-start",
              children: [
                _jsxs("a", {{
                  href: "{APK_HREF}",
                  className: "{BTN_EMERALD_LG}",
                  children: [
                    _jsx(DownloadIcon, {{ "aria-hidden": "true", className: "h-5 w-5 shrink-0 opacity-95 group-hover:translate-y-0.5 transition-transform" }}),
                    _jsx("span", {{ children: t.hero.ctaApk || "Download Android App" }})
                  ]
                }}),
                _jsxs("a", {{
                  href: "https://my.billmaniac.win",
                  className: "{BTN_PRIMARY_LG}",
                  children: [
                    _jsx(SparklesIcon, {{ "aria-hidden": "true", className: "h-5 w-5 shrink-0 opacity-95" }}),
                    _jsx("span", {{ children: t.hero.cta }})
                  ]
                }})
              ]
            }}),"""

ANDROID_BUTTONS_PLAIN = f"""              _jsxs("div", {{
                className: "mt-8 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3",
                children: [
                  _jsx("a", {{
                    href: "{APK_HREF}",
                    className: "inline-flex items-center justify-center rounded-md bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 transition-colors w-full sm:w-auto min-h-[44px]",
                    children: a.ctaApk || "Download Android App"
                  }}),
                  _jsx("a", {{
                    href: "https://my.billmaniac.win",
                    className: "inline-flex items-center justify-center rounded-md bg-brand-primary px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-brand-dark transition-colors",
                    children: a.ctaWeb
                  }}),
                  _jsx("a", {{
                    href: "#android-features",
                    className: "inline-flex items-center justify-center rounded-md bg-slate-800 px-6 py-3 text-sm font-semibold text-white border border-slate-700 hover:bg-slate-700 transition-colors",
                    children: a.ctaFeatures
                  }})
                ]
              }}),"""

ANDROID_BUTTONS_STYLED = f"""              _jsxs("div", {{
                className: "mt-8 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3",
                children: [
                  _jsxs("a", {{
                    href: "{APK_HREF}",
                    className: "{BTN_EMERALD_SM}",
                    children: [
                      _jsx(DownloadIcon, {{ "aria-hidden": "true", className: "h-4 w-4 shrink-0 group-hover:translate-y-0.5 transition-transform" }}),
                      _jsx("span", {{ children: a.ctaApk || "Download Android App" }})
                    ]
                  }}),
                  _jsxs("a", {{
                    href: "https://my.billmaniac.win",
                    className: "{BTN_PRIMARY_SM}",
                    children: [
                      _jsx(SparklesIcon, {{ "aria-hidden": "true", className: "h-4 w-4 shrink-0" }}),
                      _jsx("span", {{ children: a.ctaWeb }})
                    ]
                  }}),
                  _jsxs("a", {{
                    href: "#android-features",
                    className: "{BTN_GHOST_SM}",
                    children: [
                      _jsx(ArrowRightIcon, {{ "aria-hidden": "true", className: "h-4 w-4 shrink-0 group-hover:translate-x-0.5 transition-transform" }}),
                      _jsx("span", {{ children: a.ctaFeatures }})
                    ]
                  }})
                ]
              }}),"""

HEADER_LOGIN_PLAIN = """                  _jsx("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-block text-sm font-semibold bg-slate-700 text-white px-3 py-2 rounded-md hover:bg-slate-600 transition-colors",
                    children: t.header.login,
                  }),"""

HEADER_LOGIN_STYLED = """                  _jsxs("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-flex items-center gap-1.5 text-sm font-semibold bg-slate-800/90 text-white px-3.5 py-2 rounded-lg border border-slate-600/70 shadow-sm hover:bg-slate-700 hover:border-slate-500 active:scale-[0.98] transition-all duration-200",
                    children: [
                      _jsx(LogInIcon, { "aria-hidden": "true", className: "h-4 w-4 shrink-0 opacity-90" }),
                      _jsx("span", { children: t.header.login })
                    ],
                  }),"""

HEADER_SIGNUP_PLAIN = """                  _jsx("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-block text-sm font-semibold bg-brand-primary text-white px-3 py-2 rounded-md hover:bg-brand-dark transition-colors shadow-lg",
                    children: t.header.signUp,
                  }),"""

HEADER_SIGNUP_STYLED = """                  _jsxs("a", {
                    href: "https://my.billmaniac.win",
                    className: "hidden sm:inline-flex items-center gap-1.5 text-sm font-semibold text-white px-3.5 py-2 rounded-lg bg-gradient-to-b from-brand-primary to-brand-dark shadow-lg shadow-indigo-950/40 ring-1 ring-white/10 hover:from-indigo-500 hover:to-brand-dark active:scale-[0.98] transition-all duration-200",
                    children: [
                      _jsx(UserPlusIcon, { "aria-hidden": "true", className: "h-4 w-4 shrink-0 opacity-95" }),
                      _jsx("span", { children: t.header.signUp })
                    ],
                  }),"""


def b64(src: str) -> str:
    return "data:application/javascript;base64," + base64.b64encode(
        src.encode("utf-8")
    ).decode("ascii")


def patch_constants_icons(src: str) -> str:
    if "export const DownloadIcon" in src:
        return src
    marker = "export const MenuIcon"
    if marker not in src:
        raise SystemExit("constants layout changed — update patch-android-download.py")
    icons = "\n".join([DOWNLOAD_ICON, SPARKLES_ICON, LOG_IN_ICON, USER_PLUS_ICON]) + "\n"
    return src.replace(marker, icons + marker, 1)


def patch_hero_button_styling(src: str) -> str:
    if CTA_STYLED_MARKER in src:
        return src
    if "DownloadIcon" not in src:
        src = src.replace(
            "import { useLanguage } from '@/LanguageContext';",
            "import { useLanguage } from '@/LanguageContext';\nimport { DownloadIcon, SparklesIcon } from '@/constants';",
            1,
        )
    if HERO_BUTTONS_PLAIN in src:
        return src.replace(HERO_BUTTONS_PLAIN, HERO_BUTTONS_STYLED, 1)
    raise SystemExit("Hero buttons layout changed — update patch-android-download.py")


def patch_android_button_styling(src: str) -> str:
    if CTA_STYLED_MARKER in src:
        return src
    src = src.replace(
        "import { ArrowLeftIcon } from '@/constants';",
        "import { ArrowLeftIcon, ArrowRightIcon, DownloadIcon, SparklesIcon } from '@/constants';",
        1,
    )
    if ANDROID_BUTTONS_PLAIN in src:
        return src.replace(ANDROID_BUTTONS_PLAIN, ANDROID_BUTTONS_STYLED, 1)
    raise SystemExit("Android buttons layout changed — update patch-android-download.py")


def patch_contact_remove_phone(src: str) -> str:
    if "PHONE_TEL" not in src:
        return src
    src = re.sub(
        r'const PHONE_DISPLAY = "[^"]*";\nconst PHONE_TEL = "[^"]*";\nconst WA = "[^"]*";\n',
        "",
        src,
        count=1,
    )
    phone_block = """                _jsxs("p", {
                  className: "mt-6 text-slate-300",
                  children: [
                    _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.phoneLabel }),
                    _jsx("a", {
                      href: `tel:${PHONE_TEL}`,
                      className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                      children: PHONE_DISPLAY,
                    }),
                  ],
                }),"""
    actions_old = """                _jsxs("div", {
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
                }),"""
    actions_new = """                _jsx("div", {
                  className: "mt-6",
                  children: _jsx("a", {
                    href: "/checkout",
                    className: "inline-flex items-center justify-center px-4 py-2 rounded-md bg-brand-primary text-white text-sm font-semibold hover:bg-brand-dark",
                    children: t.contact.checkoutCta,
                  }),
                }),"""
    if phone_block in src:
        src = src.replace(phone_block, "", 1)
    if actions_old in src:
        src = src.replace(actions_old, actions_new, 1)
    if "PHONE_TEL" in src:
        raise SystemExit("Contact phone block changed — update patch_contact_remove_phone")
    return src


def patch_header_button_styling(src: str) -> str:
    if "hidden sm:inline-flex items-center gap-1.5" in src:
        return src
    src = src.replace(
        "import { BillManiacLogo } from '@/constants';",
        "import { BillManiacLogo, LogInIcon, UserPlusIcon } from '@/constants';",
        1,
    )
    out = src.replace(HEADER_LOGIN_PLAIN, HEADER_LOGIN_STYLED, 1)
    out = out.replace(HEADER_SIGNUP_PLAIN, HEADER_SIGNUP_STYLED, 1)
    if out == src:
        raise SystemExit("Header buttons layout changed — update patch-android-download.py")
    return out


def patch_android_component(src: str) -> str:
    if APK_HREF in src and "ctaApk ||" in src:
        return src
    src = src.replace(
        f'href: "{RELATIVE_APK_HREF}",\n                    download: "{APK_FILENAME}",',
        f'href: "{APK_HREF}",',
        1,
    )
    src = src.replace(
        'children: a.ctaApk\n                  }),',
        'children: a.ctaApk || "Download Android App"\n                  }),',
        1,
    )
    src = src.replace(
        'className: "inline-flex items-center justify-center rounded-md bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 transition-colors",',
        'className: "inline-flex items-center justify-center rounded-md bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:bg-emerald-500 transition-colors w-full sm:w-auto min-h-[44px]",',
        1,
    )
    if APK_HREF in src and "ctaApk ||" in src:
        return src
    if OLD_BUTTONS not in src:
        raise SystemExit("Android component layout changed — update patch-android-download.py")
    return src.replace(OLD_BUTTONS, NEW_BUTTONS, 1)


def patch_hero_component(src: str) -> str:
    if APK_HREF in src and "t.hero.ctaApk" in src:
        return src
    if HERO_OLD not in src:
        raise SystemExit("Hero component layout changed — update patch-android-download.py")
    return src.replace(HERO_OLD, HERO_NEW, 1)


def patch_footer_nav(src: str) -> str:
    if FOOTER_NAV_NEW.split("\n", 1)[1].strip() in src:
        return src
    if FOOTER_NAV_OLD not in src:
        raise SystemExit("Footer nav interceptor changed — update patch-android-download.py")
    return src.replace(FOOTER_NAV_OLD, FOOTER_NAV_NEW, 1)


def patch_translations(src: str) -> str:
    out = src
    for old, new in TRANSLATION_PATCHES:
        if old not in out:
            marker = new.split("\n", 1)[0].strip().strip(",")
            if marker in out:
                continue
            raise SystemExit(f"Missing translation snippet: {old[:60]}…")
        out = out.replace(old, new, 1)
    return out


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r'(<script type="importmap">)(.*?)(</script>)', html, re.S)
    if not m:
        raise SystemExit("importmap not found")

    imap = json.loads(m.group(2))
    imports = imap["imports"]

    contact_key = "@/components/Contact"
    android_key = "@/components/Android"
    hero_key = "@/components/Hero"
    header_key = "@/components/Header"
    footer_key = "@/components/Footer"
    trans_key = "@/translations"
    const_key = "@/constants"
    contact_src = base64.b64decode(imports[contact_key].split(",", 1)[1]).decode("utf-8")
    android_src = base64.b64decode(imports[android_key].split(",", 1)[1]).decode("utf-8")
    hero_src = base64.b64decode(imports[hero_key].split(",", 1)[1]).decode("utf-8")
    header_src = base64.b64decode(imports[header_key].split(",", 1)[1]).decode("utf-8")
    footer_src = base64.b64decode(imports[footer_key].split(",", 1)[1]).decode("utf-8")
    trans_src = base64.b64decode(imports[trans_key].split(",", 1)[1]).decode("utf-8")
    const_src = base64.b64decode(imports[const_key].split(",", 1)[1]).decode("utf-8")

    imports[const_key] = b64(patch_constants_icons(const_src))
    imports[contact_key] = b64(patch_contact_remove_phone(contact_src))
    imports[android_key] = b64(
        patch_android_button_styling(patch_android_component(android_src))
    )
    imports[hero_key] = b64(patch_hero_button_styling(patch_hero_component(hero_src)))
    imports[header_key] = b64(patch_header_button_styling(header_src))
    imports[footer_key] = b64(patch_footer_nav(footer_src))
    imports[trans_key] = b64(patch_translations(trans_src))

    imap["imports"] = imports
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print(f"Patched CTA buttons (Hero, Android, Header), icons, translations in {INDEX}")


if __name__ == "__main__":
    main()
