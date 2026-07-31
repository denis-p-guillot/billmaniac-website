#!/usr/bin/env python3
"""Inject SEO analytics: GA4 SPA page views + optional Cloudflare Web Analytics."""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "dist" / "index.html"
GA_ID = os.environ.get("GA_MEASUREMENT_ID", "G-FY5RTLMWZ9").strip() or "G-FY5RTLMWZ9"
CF_BEACON = os.environ.get("CF_WEB_ANALYTICS_TOKEN", "").strip()
MARKER = "ANALYTICS_SPA_V1"

SEO_TRACKING = rf"""
export const GA_MEASUREMENT_ID = "{GA_ID}";

/** Track SPA navigations for GA4 (SEO landing-page performance). */
export function trackPageView(seo) {{
  if (typeof window === "undefined" || !seo) return;
  const path = seo.path === "/" ? "/" : seo.path;
  const pageLocation = `${{SITE_ORIGIN}}${{path}}`;
  if (typeof window.gtag === "function") {{
    window.gtag("config", GA_MEASUREMENT_ID, {{
      page_path: path,
      page_title: seo.title,
      page_location: pageLocation,
    }});
  }}
}}

/** Track key conversion events (contact form, etc.). */
export function trackEvent(name, params = {{}}) {{
  if (typeof window === "undefined" || typeof window.gtag !== "function") return;
  window.gtag("event", name, params);
}}
/* {MARKER} */
"""

GA_BODY = f"""    <!-- Consent Manager and Analytics moved to the end of body to prevent render-blocking -->
    <script type="text/javascript" data-cmp-ab="1" src="https://cdn.consentmanager.net/delivery/autoblocking/4d59b5b6b2102.js" data-cmp-host="a.delivery.consentmanager.net" data-cmp-cdn="cdn.consentmanager.net" data-cmp-codesrc="16"></script>
    
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}" data-cmp-ab-ignore="1"></script>
    <script data-cmp-ab-ignore="1">
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}', {{
        send_page_view: false,
        anonymize_ip: true,
        allow_google_signals: true,
        allow_ad_personalization_signals: false
      }});
    </script>"""

CF_BEACON_SNIPPET = ""
if CF_BEACON:
    beacon_json = json.dumps({"token": CF_BEACON, "spa": True}, separators=(",", ":"))
    CF_BEACON_SNIPPET = f"""
    <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{beacon_json}'></script>"""


def b64(text: str) -> str:
    return "data:text/javascript;base64," + base64.b64encode(text.encode("utf-8")).decode("ascii")


def patch_seo_module(src: str) -> str:
    if MARKER in src:
        src = re.sub(r"/\* ANALYTICS_SPA_V1 \*/\n?", "", src)
        src = re.sub(
            r"\nexport const GA_MEASUREMENT_ID =[\s\S]*?/\* ANALYTICS_SPA_V1 \*/\n?",
            "\n",
            src,
        )

    if "export function trackPageView" in src:
        src = re.sub(
            r"export const GA_MEASUREMENT_ID =[\s\S]*?/\* ANALYTICS_SPA_V1 \*/\n?",
            "",
            src,
        )

    if "export function applyClientSeo(seo)" not in src:
        raise SystemExit("applyClientSeo not found in @/seo")

    if MARKER not in src:
        insert_at = src.find("export function applyClientSeo")
        if insert_at < 0:
            raise SystemExit("Could not locate applyClientSeo in @/seo")
        src = src[:insert_at] + SEO_TRACKING + "\n" + src[insert_at:]

    if "trackPageView(seo)" not in src:
        old = "  setMetaProperty('twitter:image', DEFAULT_OG_IMAGE);\n}"
        new = "  setMetaProperty('twitter:image', DEFAULT_OG_IMAGE);\n  trackPageView(seo);\n}"
        if old not in src:
            raise SystemExit("applyClientSeo body changed — update patch-analytics.py")
        src = src.replace(old, new, 1)

    return src


def patch_contact_form(src: str) -> str:
    if "contact_form_submit" in src:
        return src
    old = "      setStatus(\"success\");"
    new = """      if (typeof window.gtag === "function") {
        window.gtag("event", "contact_form_submit", { page_path: "/contact", method: "form" });
      }
      setStatus("success");"""
    if old not in src:
        return src
    return src.replace(old, new, 1)


def patch_index_html(html: str) -> str:
    body_pattern = re.compile(
        r"<!-- Consent Manager and Analytics moved to the end of body[\s\S]*?"
        r"gtag\('config', 'G-[^']+'\);\s*\n\s*</script>",
        re.M,
    )
    if not body_pattern.search(html):
        raise SystemExit("Analytics block not found in dist/index.html")
    html = body_pattern.sub(GA_BODY.strip(), html, count=1)

    html = re.sub(
        r'\n\s*<script defer src="https://static\.cloudflareinsights\.com/beacon\.min\.js"[^>]*></script>',
        "",
        html,
    )
    if CF_BEACON_SNIPPET:
        html = html.replace("</body>", CF_BEACON_SNIPPET + "\n  </body>", 1)

    return html


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r"(<script type=\"importmap\">)(.*?)(</script>)", html, re.S)
    if not m:
        raise SystemExit("importmap not found")

    imap = json.loads(m.group(2))
    imports = imap["imports"]

    seo_key = "@/seo"
    contact_key = "@/components/Contact"
    seo_src = base64.b64decode(imports[seo_key].split(",", 1)[1]).decode("utf-8")
    imports[seo_key] = b64(patch_seo_module(seo_src))

    if contact_key in imports:
        contact_src = base64.b64decode(imports[contact_key].split(",", 1)[1]).decode("utf-8")
        imports[contact_key] = b64(patch_contact_form(contact_src))

    imap["imports"] = imports
    html = html[: m.start()] + m.group(1) + json.dumps(imap, separators=(",", ":")) + m.group(3) + html[m.end() :]
    html = patch_index_html(html)
    INDEX.write_text(html)

    extras = []
    if CF_BEACON:
        extras.append("Cloudflare Web Analytics")
    print(
        f"Patched GA4 SPA tracking ({GA_ID}) in {INDEX}"
        + (f" + {', '.join(extras)}" if extras else "")
    )


if __name__ == "__main__":
    main()
