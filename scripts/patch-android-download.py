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
        '            "apkMeta": "Version 0.1.1 · direct install (enable Install unknown apps if prompted).",',
    ),
    (
        '"note": "Android APK / Play listing coming soon. Sign in on web today with email or Google — the same account works on Android."',
        '"note": "Use the same email or Google account on Android and web. Google Play internal testing link coming soon."',
    ),
    (
        '"ctaFeatures": "Voir les fonctions Android",',
        '"ctaFeatures": "Voir les fonctions Android",\n'
        '            "ctaApk": "Télécharger l’APK Android",\n'
        '            "apkMeta": "Version 0.1.1 · installation directe (autorisez les sources inconnues si demandé).",',
    ),
    (
        '"note": "APK / fiche Play bientôt disponibles. Connectez-vous sur le web par e-mail ou Google — le même compte fonctionne sur Android."',
        '"note": "Utilisez le même compte e-mail ou Google sur Android et le web. Lien de test Google Play bientôt disponible."',
    ),
    (
        '"ctaFeatures": "Ver funciones Android",',
        '"ctaFeatures": "Ver funciones Android",\n'
        '            "ctaApk": "Descargar APK Android",\n'
        '            "apkMeta": "Versión 0.1.1 · instalación directa (habilite orígenes desconocidos si se solicita).",',
    ),
    (
        '"note": "APK / ficha de Play próximamente. Inicia sesión en la web con correo o Google — la misma cuenta funciona en Android."',
        '"note": "Usa la misma cuenta de correo o Google en Android y la web. Enlace de prueba en Google Play próximamente."',
    ),
    (
        '"ctaFeatures": "Lihat Fitur Android",',
        '"ctaFeatures": "Lihat Fitur Android",\n'
        '            "ctaApk": "Unduh APK Android",\n'
        '            "apkMeta": "Versi 0.1.1 · instalasi langsung (izinkan aplikasi tidak dikenal jika diminta).",',
    ),
    (
        '"note": "APK Android / listing Play segera hadir. Masuk di web dengan email atau Google — akun yang sama berfungsi di Android."',
        '"note": "Gunakan akun email atau Google yang sama di Android dan web. Tautan uji Google Play segera hadir."',
    ),
    (
        '"cta": "Get Started for Free",',
        '"cta": "Get Started for Free",\n'
        '            "ctaApk": "Download Android App",\n'
        '            "apkMeta": "Version 0.1.1 · direct install on Android.",',
    ),
    (
        '"cta": "Commencez gratuitement",',
        '"cta": "Commencez gratuitement",\n'
        '            "ctaApk": "Télécharger l’app Android",\n'
        '            "apkMeta": "Version 0.1.1 · installation directe sur Android.",',
    ),
    (
        '"cta": "Empieza gratis",',
        '"cta": "Empieza gratis",\n'
        '            "ctaApk": "Descargar app Android",\n'
        '            "apkMeta": "Versión 0.1.1 · instalación directa en Android.",',
    ),
    (
        '"cta": "Mulai gratis",',
        '"cta": "Mulai gratis",\n'
        '            "ctaApk": "Unduh Aplikasi Android",\n'
        '            "apkMeta": "Versi 0.1.1 · instalasi langsung di Android.",',
    ),
]


def b64(src: str) -> str:
    return "data:application/javascript;base64," + base64.b64encode(
        src.encode("utf-8")
    ).decode("ascii")


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

    android_key = "@/components/Android"
    hero_key = "@/components/Hero"
    footer_key = "@/components/Footer"
    trans_key = "@/translations"
    android_src = base64.b64decode(imports[android_key].split(",", 1)[1]).decode("utf-8")
    hero_src = base64.b64decode(imports[hero_key].split(",", 1)[1]).decode("utf-8")
    footer_src = base64.b64decode(imports[footer_key].split(",", 1)[1]).decode("utf-8")
    trans_src = base64.b64decode(imports[trans_key].split(",", 1)[1]).decode("utf-8")

    imports[android_key] = b64(patch_android_component(android_src))
    imports[hero_key] = b64(patch_hero_component(hero_src))
    imports[footer_key] = b64(patch_footer_nav(footer_src))
    imports[trans_key] = b64(patch_translations(trans_src))

    imap["imports"] = imports
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print(f"Patched Android + Hero download CTAs, translations, footer nav in {INDEX}")


if __name__ == "__main__":
    main()
