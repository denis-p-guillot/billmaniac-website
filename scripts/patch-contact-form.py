#!/usr/bin/env python3
"""Replace Contact page with enquiry form (Cloudflare Turnstile + /api/contact)."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "dist" / "index.html"
MARKER = "CONTACT_FORM_V1"

CONTACT_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from 'react';
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const EMAIL_CONTACT = "contact@billmaniac.win";
const EMAIL_BILLING = "billing@billmaniac.win";
const EMAIL_SUPPORT = "support@billmaniac.win";
const ADDRESS_LINES = ["Menara Ravindo, Lantai 12", "Jl. Kebon Sirih Kav. 75", "RT 001 / RW 001", "Kelurahan Kebon Sirih, Kecamatan Menteng", "Jakarta Pusat 10340", "DKI Jakarta, Indonesia"];
const TURNSTILE_SCRIPT = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
/* CONTACT_FORM_V1 */

function loadTurnstileScript() {
  if (typeof window !== "undefined" && window.turnstile) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src^="${TURNSTILE_SCRIPT}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("turnstile_load_failed")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.src = TURNSTILE_SCRIPT;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("turnstile_load_failed"));
    document.head.appendChild(script);
  });
}

const Contact = () => {
  const { t } = useLanguage();
  const turnstileRef = useRef(null);
  const widgetIdRef = useRef(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [website, setWebsite] = useState("");
  const [turnstileToken, setTurnstileToken] = useState("");
  const [turnstileSiteKey, setTurnstileSiteKey] = useState("");
  const [turnstileRequired, setTurnstileRequired] = useState(false);
  const [status, setStatus] = useState("idle");
  const [errorKey, setErrorKey] = useState("");
  const onBack = (event) => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    navigateToPath("/");
  };
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/contact");
        const data = await res.json();
        if (cancelled) return;
        const siteKey = data.turnstileSiteKey || "";
        const enabled = Boolean(data.turnstileEnabled && siteKey);
        setTurnstileSiteKey(siteKey);
        setTurnstileRequired(enabled);
        if (!enabled) return;
        await loadTurnstileScript();
        if (cancelled || !turnstileRef.current || !window.turnstile) return;
        widgetIdRef.current = window.turnstile.render(turnstileRef.current, {
          sitekey: siteKey,
          theme: "dark",
          callback: (token) => setTurnstileToken(token),
          "expired-callback": () => setTurnstileToken(""),
          "error-callback": () => setTurnstileToken(""),
        });
      } catch {
        if (!cancelled) setTurnstileRequired(false);
      }
    })();
    return () => {
      cancelled = true;
      if (widgetIdRef.current != null && typeof window !== "undefined" && window.turnstile) {
        window.turnstile.remove(widgetIdRef.current);
        widgetIdRef.current = null;
      }
    };
  }, []);
  const onSubmit = async (event) => {
    event.preventDefault();
    if (status === "submitting") return;
    setErrorKey("");
    if (turnstileRequired && !turnstileToken) {
      setErrorKey("captcha");
      return;
    }
    setStatus("submitting");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          subject,
          message,
          website,
          turnstileToken,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (data.error === "captcha") setErrorKey("captcha");
        else if (data.error === "validation") setErrorKey("validation");
        else setErrorKey("generic");
        setStatus("idle");
        if (turnstileRequired && window.turnstile && widgetIdRef.current != null) {
          window.turnstile.reset(widgetIdRef.current);
          setTurnstileToken("");
        }
        return;
      }
      setStatus("success");
      setName("");
      setEmail("");
      setSubject("");
      setMessage("");
      setWebsite("");
      if (turnstileRequired && window.turnstile && widgetIdRef.current != null) {
        window.turnstile.reset(widgetIdRef.current);
        setTurnstileToken("");
      }
    } catch {
      setErrorKey("generic");
      setStatus("idle");
    }
  };
  const errorMessage = errorKey === "captcha"
    ? t.contact.formErrorCaptcha
    : errorKey === "validation"
      ? t.contact.formErrorValidation
      : errorKey === "generic"
        ? t.contact.formErrorGeneric
        : "";
  return _jsx("section", {
    id: "contact",
    className: "bg-slate-950 py-20 sm:py-28",
    children: _jsxs("div", {
      className: "max-w-6xl mx-auto px-4 sm:px-6 lg:px-8",
      children: [
        _jsxs("div", {
          className: "text-center",
          children: [
            _jsx("h1", { className: "text-4xl font-extrabold text-white sm:text-5xl", children: t.contact.title }),
            _jsx("p", { className: "mt-4 text-lg text-slate-400", children: t.contact.intro }),
          ],
        }),
        _jsxs("div", {
          className: "mt-12 grid gap-6 lg:grid-cols-2",
          children: [
            _jsxs("div", {
              className: "space-y-6",
              children: [
                _jsxs("div", {
                  className: "bg-slate-900 p-8 rounded-lg border border-slate-800",
                  children: [
                    _jsx("h2", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: t.contact.officeLabel }),
                    _jsx("p", { className: "mt-3 text-lg font-semibold text-white", children: "PT. DEVINCI GROUP INDONESIA" }),
                    _jsx("p", { className: "mt-3 text-slate-300 whitespace-pre-line", children: ADDRESS_LINES.join("\n") }),
                  ],
                }),
                _jsxs("div", {
                  className: "bg-slate-900 p-8 rounded-lg border border-slate-800 space-y-5",
                  children: [
                    _jsx("h2", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: t.contact.emailLabel }),
                    _jsxs("p", {
                      className: "text-slate-300",
                      children: [
                        _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.publicLabel || "Public contact" }),
                        _jsx("a", {
                          href: `mailto:${EMAIL_CONTACT}`,
                          className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                          children: EMAIL_CONTACT,
                        }),
                      ],
                    }),
                    _jsxs("p", {
                      className: "text-slate-300",
                      children: [
                        _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.businessLabel }),
                        _jsx("a", {
                          href: `mailto:${EMAIL_BILLING}`,
                          className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                          children: EMAIL_BILLING,
                        }),
                      ],
                    }),
                    _jsxs("p", {
                      className: "text-slate-300",
                      children: [
                        _jsx("span", { className: "block text-sm text-slate-500", children: t.contact.generalLabel }),
                        _jsx("a", {
                          href: `mailto:${EMAIL_SUPPORT}`,
                          className: "font-semibold text-brand-primary hover:text-brand-secondary underline",
                          children: EMAIL_SUPPORT,
                        }),
                      ],
                    }),
                    _jsx("p", { className: "text-sm text-slate-500", children: t.contact.hours }),
                  ],
                }),
              ],
            }),
            _jsxs("div", {
              className: "bg-slate-900 p-8 rounded-lg border border-slate-800",
              children: [
                _jsx("h2", { className: "text-sm font-semibold uppercase tracking-wider text-brand-primary", children: t.contact.formTitle }),
                status === "success"
                  ? _jsxs("div", {
                      className: "mt-6 rounded-lg border border-emerald-700/50 bg-emerald-950/40 p-6",
                      children: [
                        _jsx("p", { className: "text-lg font-semibold text-emerald-300", children: t.contact.formSuccessTitle }),
                        _jsx("p", { className: "mt-2 text-slate-300", children: t.contact.formSuccessMessage }),
                        _jsx("button", {
                          type: "button",
                          onClick: () => setStatus("idle"),
                          className: "mt-4 text-sm font-semibold text-brand-primary hover:text-brand-secondary",
                          children: t.contact.formSendAnother,
                        }),
                      ],
                    })
                  : _jsxs("form", {
                      className: "mt-6 space-y-5",
                      onSubmit: onSubmit,
                      noValidate: true,
                      children: [
                        _jsxs("div", {
                          className: "absolute -left-[9999px] opacity-0 h-0 w-0 overflow-hidden",
                          "aria-hidden": "true",
                          children: [
                            _jsx("label", { htmlFor: "contact-website", children: "Website" }),
                            _jsx("input", {
                              id: "contact-website",
                              type: "text",
                              name: "website",
                              tabIndex: -1,
                              autoComplete: "off",
                              value: website,
                              onChange: (e) => setWebsite(e.target.value),
                            }),
                          ],
                        }),
                        _jsxs("div", {
                          children: [
                            _jsx("label", { htmlFor: "contact-name", className: "block text-sm font-medium text-slate-300", children: t.contact.formNameLabel }),
                            _jsx("input", {
                              id: "contact-name",
                              type: "text",
                              name: "name",
                              required: true,
                              autoComplete: "name",
                              value: name,
                              onChange: (e) => setName(e.target.value),
                              placeholder: t.contact.formNamePlaceholder,
                              className: "mt-2 w-full rounded-md border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-500 focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary",
                            }),
                          ],
                        }),
                        _jsxs("div", {
                          children: [
                            _jsx("label", { htmlFor: "contact-email", className: "block text-sm font-medium text-slate-300", children: t.contact.formEmailLabel }),
                            _jsx("input", {
                              id: "contact-email",
                              type: "email",
                              name: "email",
                              required: true,
                              autoComplete: "email",
                              value: email,
                              onChange: (e) => setEmail(e.target.value),
                              placeholder: t.contact.formEmailPlaceholder,
                              className: "mt-2 w-full rounded-md border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-500 focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary",
                            }),
                          ],
                        }),
                        _jsxs("div", {
                          children: [
                            _jsx("label", { htmlFor: "contact-subject", className: "block text-sm font-medium text-slate-300", children: t.contact.formSubjectLabel }),
                            _jsx("input", {
                              id: "contact-subject",
                              type: "text",
                              name: "subject",
                              value: subject,
                              onChange: (e) => setSubject(e.target.value),
                              placeholder: t.contact.formSubjectPlaceholder,
                              className: "mt-2 w-full rounded-md border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-500 focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary",
                            }),
                          ],
                        }),
                        _jsxs("div", {
                          children: [
                            _jsx("label", { htmlFor: "contact-message", className: "block text-sm font-medium text-slate-300", children: t.contact.formMessageLabel }),
                            _jsx("textarea", {
                              id: "contact-message",
                              name: "message",
                              required: true,
                              rows: 6,
                              value: message,
                              onChange: (e) => setMessage(e.target.value),
                              placeholder: t.contact.formMessagePlaceholder,
                              className: "mt-2 w-full rounded-md border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder:text-slate-500 focus:border-brand-primary focus:outline-none focus:ring-1 focus:ring-brand-primary resize-y min-h-[140px]",
                            }),
                          ],
                        }),
                        turnstileRequired
                          ? _jsxs("div", {
                              children: [
                                _jsx("div", { ref: turnstileRef, className: "min-h-[65px]" }),
                                !turnstileSiteKey
                                  ? _jsx("p", { className: "mt-2 text-sm text-slate-500", children: t.contact.formTurnstileLoading })
                                  : null,
                              ],
                            })
                          : null,
                        errorMessage
                          ? _jsx("p", { className: "text-sm text-red-400", role: "alert", children: errorMessage })
                          : null,
                        _jsx("button", {
                          type: "submit",
                          disabled: status === "submitting",
                          className: "inline-flex w-full items-center justify-center rounded-md bg-brand-primary px-6 py-3 text-sm font-semibold text-white hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-60 transition-colors min-h-[44px]",
                          children: status === "submitting" ? t.contact.formSubmitting : t.contact.formSubmit,
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

FORM_KEYS_EN = """
            "formTitle": "Send us a message",
            "formNameLabel": "Your name",
            "formNamePlaceholder": "Jane Doe",
            "formEmailLabel": "Your email",
            "formEmailPlaceholder": "you@example.com",
            "formSubjectLabel": "Subject (optional)",
            "formSubjectPlaceholder": "How can we help?",
            "formMessageLabel": "Message",
            "formMessagePlaceholder": "Tell us about your enquiry…",
            "formSubmit": "Send message",
            "formSubmitting": "Sending…",
            "formSuccessTitle": "Message sent",
            "formSuccessMessage": "Thanks for reaching out. We'll reply to your email as soon as we can.",
            "formSendAnother": "Send another message",
            "formErrorGeneric": "Something went wrong. Please try again in a moment.",
            "formErrorCaptcha": "Please complete the security check.",
            "formErrorValidation": "Please check your details and try again.",
            "formTurnstileLoading": "Loading security check…\""""

FORM_KEYS_FR = """
            "formTitle": "Envoyez-nous un message",
            "formNameLabel": "Votre nom",
            "formNamePlaceholder": "Jane Doe",
            "formEmailLabel": "Votre e-mail",
            "formEmailPlaceholder": "vous@exemple.com",
            "formSubjectLabel": "Objet (facultatif)",
            "formSubjectPlaceholder": "Comment pouvons-nous vous aider ?",
            "formMessageLabel": "Message",
            "formMessagePlaceholder": "Décrivez votre demande…",
            "formSubmit": "Envoyer le message",
            "formSubmitting": "Envoi…",
            "formSuccessTitle": "Message envoyé",
            "formSuccessMessage": "Merci pour votre message. Nous vous répondrons par e-mail dès que possible.",
            "formSendAnother": "Envoyer un autre message",
            "formErrorGeneric": "Une erreur s'est produite. Veuillez réessayer.",
            "formErrorCaptcha": "Veuillez compléter la vérification de sécurité.",
            "formErrorValidation": "Veuillez vérifier vos informations et réessayer.",
            "formTurnstileLoading": "Chargement de la vérification…\""""

FORM_KEYS_ES = """
            "formTitle": "Envíanos un mensaje",
            "formNameLabel": "Tu nombre",
            "formNamePlaceholder": "Jane Doe",
            "formEmailLabel": "Tu correo",
            "formEmailPlaceholder": "tu@ejemplo.com",
            "formSubjectLabel": "Asunto (opcional)",
            "formSubjectPlaceholder": "¿En qué podemos ayudarte?",
            "formMessageLabel": "Mensaje",
            "formMessagePlaceholder": "Cuéntanos tu consulta…",
            "formSubmit": "Enviar mensaje",
            "formSubmitting": "Enviando…",
            "formSuccessTitle": "Mensaje enviado",
            "formSuccessMessage": "Gracias por contactarnos. Responderemos a tu correo lo antes posible.",
            "formSendAnother": "Enviar otro mensaje",
            "formErrorGeneric": "Algo salió mal. Inténtalo de nuevo en un momento.",
            "formErrorCaptcha": "Completa la verificación de seguridad.",
            "formErrorValidation": "Revisa tus datos e inténtalo de nuevo.",
            "formTurnstileLoading": "Cargando verificación…\""""

FORM_KEYS_ID = """
            "formTitle": "Kirim pesan kepada kami",
            "formNameLabel": "Nama Anda",
            "formNamePlaceholder": "Jane Doe",
            "formEmailLabel": "Email Anda",
            "formEmailPlaceholder": "anda@contoh.com",
            "formSubjectLabel": "Subjek (opsional)",
            "formSubjectPlaceholder": "Bagaimana kami bisa membantu?",
            "formMessageLabel": "Pesan",
            "formMessagePlaceholder": "Ceritakan pertanyaan Anda…",
            "formSubmit": "Kirim pesan",
            "formSubmitting": "Mengirim…",
            "formSuccessTitle": "Pesan terkirim",
            "formSuccessMessage": "Terima kasih telah menghubungi kami. Kami akan membalas email Anda secepatnya.",
            "formSendAnother": "Kirim pesan lain",
            "formErrorGeneric": "Terjadi kesalahan. Silakan coba lagi.",
            "formErrorCaptcha": "Selesaikan pemeriksaan keamanan.",
            "formErrorValidation": "Periksa detail Anda dan coba lagi.",
            "formTurnstileLoading": "Memuat pemeriksaan keamanan…\""""

TRANSLATION_PATCHES = [
    (
        '            "backToHome": "Back to Home"\n        },\n        "services":',
        f'            "backToHome": "Back to Home",{FORM_KEYS_EN}\n        }},\n        "services":',
    ),
    (
        '            "backToHome": "Retour à l\'accueil"\n        },\n        "services":',
        f'            "backToHome": "Retour à l\'accueil",{FORM_KEYS_FR}\n        }},\n        "services":',
    ),
    (
        '            "backToHome": "Volver al Inicio"\n        },\n        "services":',
        f'            "backToHome": "Volver al Inicio",{FORM_KEYS_ES}\n        }},\n        "services":',
    ),
    (
        '            "backToHome": "Kembali ke Beranda"\n        },\n        "services":',
        f'            "backToHome": "Kembali ke Beranda",{FORM_KEYS_ID}\n        }},\n        "services":',
    ),
]


def b64(text: str) -> str:
    return "data:text/javascript;base64," + base64.b64encode(text.encode("utf-8")).decode("ascii")


def patch_translations(src: str) -> str:
    if "formTitle" in src and "formSubmit" in src:
        return src
    out = src
    for old, new in TRANSLATION_PATCHES:
        if old not in out:
            marker = new.split("\n", 1)[0].strip().strip(",")
            if marker.replace('"', "") in out:
                continue
            raise SystemExit(f"Missing translation snippet:\n{old[:120]}…")
        out = out.replace(old, new, 1)
    return out


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r"(<script type=\"importmap\">)(.*?)(</script>)", html, re.S)
    if not m:
        raise SystemExit("importmap not found")

    imap = json.loads(m.group(2))
    imports = imap["imports"]
    contact_key = "@/components/Contact"
    trans_key = "@/translations"

    imports[contact_key] = b64(CONTACT_SRC)

    trans_src = base64.b64decode(imports[trans_key].split(",", 1)[1]).decode("utf-8")
    imports[trans_key] = b64(patch_translations(trans_src))

    imap["imports"] = imports
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print(f"Patched Contact form + translations in {INDEX}")


if __name__ == "__main__":
    main()
