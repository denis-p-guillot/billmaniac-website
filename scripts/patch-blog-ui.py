#!/usr/bin/env python3
"""Replace Blog page with sortable, paginated layout and publisher badges."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "dist/index.html"
MARKER = "BLOG_UI_V1"

BLOG_SRC = r'''import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from 'react';
import { useLanguage } from '@/LanguageContext';
import { ArrowLeftIcon } from '@/constants';
import { navigateToPath } from '@/seo';

const POSTS_PER_PAGE = 2;
/* BLOG_UI_V1 */

function parsePublishedAt(post) {
    if (post.publishedAt)
        return post.publishedAt;
    const parsed = Date.parse(post.date);
    if (!Number.isNaN(parsed))
        return new Date(parsed).toISOString().slice(0, 10);
    return "1970-01-01";
}

function renderContent(content) {
    if (!content)
        return null;
    return content.map((item, index) => {
        switch (item.type) {
            case 'h3':
                return _jsx("h3", { className: "text-xl font-bold text-white mt-10 mb-3 first:mt-0", children: item.text }, index);
            case 'h4':
                return _jsx("h4", { className: "text-lg font-semibold text-slate-100 mt-8 mb-2", children: item.text }, index);
            case 'p':
                return _jsx("p", { className: "mb-4 text-base leading-7 text-slate-300", children: item.text }, index);
            case 'strong':
                return _jsx("p", { className: "font-semibold text-white mt-6 mb-2 text-base", children: item.text }, index);
            case 'ul':
                return (_jsx("ul", { className: "list-disc list-outside space-y-2 mb-4 pl-5 text-base text-slate-300", children: item.items.map((li, i) => _jsx("li", { className: "leading-7", children: li }, i)) }, index));
            default:
                return null;
        }
    });
}

const Blog = () => {
    const { t } = useLanguage();
    const blog = t.blog;
    const { posts, comingSoonTitle, comingSoonText, eyebrow, sortLabel, sortNewest, sortOldest, publisherBadge, publishedOn, previous, next, pageLabel, ofLabel, showingLabel, articlesLabel } = blog;
    const [sort, setSort] = useState("newest");
    const [page, setPage] = useState(1);
    const sorted = useMemo(() => {
        const list = [...(posts || [])];
        list.sort((a, b) => {
            const da = parsePublishedAt(a);
            const db = parsePublishedAt(b);
            return sort === "newest" ? db.localeCompare(da) : da.localeCompare(db);
        });
        return list;
    }, [posts, sort]);
    const total = sorted.length;
    const totalPages = Math.max(1, Math.ceil(total / POSTS_PER_PAGE));
    const currentPage = Math.min(page, totalPages);
    const startIdx = (currentPage - 1) * POSTS_PER_PAGE;
    const visible = sorted.slice(startIdx, startIdx + POSTS_PER_PAGE);
    const rangeStart = total === 0 ? 0 : startIdx + 1;
    const rangeEnd = Math.min(startIdx + POSTS_PER_PAGE, total);
    const onSortChange = (event) => {
        setSort(event.target.value);
        setPage(1);
    };
    const goToPage = (nextPage) => {
        setPage(nextPage);
        if (typeof document !== "undefined") {
            document.getElementById("blog")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };
    const onBack = (event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0)
            return;
        event.preventDefault();
        navigateToPath("/");
    };
    return (_jsx("section", { id: "blog", className: "bg-slate-950 py-20 sm:py-28", children: _jsxs("div", { className: "max-w-5xl mx-auto px-4 sm:px-6 lg:px-8", children: [_jsxs("div", { className: "text-center max-w-3xl mx-auto", children: [_jsx("p", { className: "text-sm font-semibold uppercase tracking-widest text-indigo-400", children: eyebrow || "Insights & updates" }), _jsx("h1", { className: "mt-3 text-4xl font-extrabold text-white sm:text-5xl tracking-tight", children: blog.title }), _jsx("p", { className: "mt-5 text-lg leading-relaxed text-slate-400", children: blog.intro })] }), posts && posts.length > 0 ? (_jsxs("div", { children: [_jsxs("div", { className: "mt-12 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between", children: [_jsxs("label", { className: "flex items-center gap-3 text-sm text-slate-400", children: [_jsx("span", { className: "font-medium text-slate-300", children: sortLabel || "Sort by" }), _jsxs("select", { value: sort, onChange: onSortChange, className: "rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm font-medium text-slate-100 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30", children: [_jsx("option", { value: "newest", children: sortNewest || "Newest first" }), _jsx("option", { value: "oldest", children: sortOldest || "Oldest first" })] })] }), _jsxs("p", { className: "text-sm text-slate-500", children: [showingLabel || "Showing", " ", _jsxs("span", { className: "font-medium text-slate-300", children: [rangeStart, "\u2013", rangeEnd] }), " ", ofLabel || "of", " ", _jsxs("span", { className: "font-medium text-slate-300", children: [total, " ", articlesLabel || "articles"] })] })] }), _jsx("div", { className: "mt-10 space-y-10", children: visible.map((post) => (_jsxs("article", { id: post.slug, className: "overflow-hidden rounded-2xl border border-slate-800/80 bg-gradient-to-b from-slate-900 via-slate-900/95 to-slate-950 p-8 shadow-xl ring-1 ring-white/5 sm:p-10", children: [_jsxs("header", { className: "space-y-4 border-b border-slate-800/80 pb-6", children: [_jsxs("div", { className: "flex flex-wrap items-center gap-3", children: [_jsxs("span", { className: "inline-flex items-center gap-1.5 rounded-full bg-indigo-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-indigo-300 ring-1 ring-inset ring-indigo-400/25", children: [_jsx("span", { className: "h-1.5 w-1.5 rounded-full bg-indigo-400", "aria-hidden": "true" }), publisherBadge || "Bill Maniac Admin"] }), _jsxs("span", { className: "text-sm text-slate-500", children: [publishedOn || "Published", " ", _jsx("time", { dateTime: parsePublishedAt(post), className: "font-medium text-slate-300", children: post.date })] })] }), _jsx("h2", { className: "text-2xl font-bold leading-tight text-white sm:text-3xl", children: post.title })] }), _jsx("div", { className: "mt-8", children: renderContent(post.content) })] }, post.slug))) }), totalPages > 1 ? (_jsxs("nav", { className: "mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center", "aria-label": "Blog pagination", children: [_jsx("button", { type: "button", onClick: () => goToPage(currentPage - 1), disabled: currentPage <= 1, className: "inline-flex min-w-[7rem] items-center justify-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40", children: previous || "Previous" }), _jsxs("p", { className: "text-sm text-slate-400", children: [_jsx("span", { className: "text-slate-500", children: pageLabel || "Page" }), " ", _jsx("span", { className: "font-semibold text-white", children: currentPage }), " ", _jsx("span", { className: "text-slate-500", children: ofLabel || "of" }), " ", _jsx("span", { className: "font-semibold text-white", children: totalPages })] }), _jsx("button", { type: "button", onClick: () => goToPage(currentPage + 1), disabled: currentPage >= totalPages, className: "inline-flex min-w-[7rem] items-center justify-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40", children: next || "Next" })] }) : null] })) : (_jsxs("div", { className: "mt-12 space-y-4 rounded-2xl border border-slate-800 bg-slate-900/80 p-12 text-center shadow-xl sm:p-16", children: [_jsx("h2", { className: "text-2xl font-bold text-white sm:text-3xl", children: comingSoonTitle || "Coming Soon!" }), _jsx("p", { className: "mx-auto max-w-lg text-base leading-relaxed text-slate-400", children: comingSoonText || "We're working on bringing you insightful articles. Stay tuned!" })] })), _jsx("div", { className: "mt-14 text-center", children: _jsxs("a", { href: "/", onClick: onBack, className: "inline-flex items-center gap-2 text-sm font-semibold text-slate-400 transition-colors hover:text-white", children: [_jsx(ArrowLeftIcon, { "aria-hidden": "true", className: "h-4 w-4" }), blog.backToHome] }) })] }) }));
};
export default Blog;
'''

INTRO_UPDATES = {
    "en": (
        '"intro": "Tips, tricks, and updates on managing your finances like a maniac."',
        '"intro": "Expert guides on receipt scanning, expense tracking, and private cloud finance from the Bill Maniac team."',
    ),
    "fr": (
        '"intro": "Astuces, conseils et actualités sur la gestion de vos finances comme un maniaque."',
        '"intro": "Guides d\'experts sur la numérisation des reçus, le suivi des dépenses et la finance cloud privée, par l\'équipe Bill Maniac."',
    ),
    "es": (
        '"intro": "Consejos, trucos y actualizaciones sobre cómo administrar tus finanzas como un maníaco."',
        '"intro": "Guías expertas sobre escaneo de recibos, control de gastos y finanzas en la nube privada, del equipo Bill Maniac."',
    ),
    "id": (
        '"intro": "Tips, trik, dan update tentang mengelola keuangan Anda seperti maniac."',
        '"intro": "Panduan ahli tentang pemindaian struk, pelacakan pengeluaran, dan keuangan cloud pribadi dari tim Bill Maniac."',
    ),
}

UI_KEYS = {
    "en": """
            "eyebrow": "Insights & updates",
            "sortLabel": "Sort by",
            "sortNewest": "Newest first",
            "sortOldest": "Oldest first",
            "publisherBadge": "Bill Maniac Admin",
            "publishedOn": "Published",
            "previous": "Previous",
            "next": "Next",
            "pageLabel": "Page",
            "ofLabel": "of",
            "showingLabel": "Showing",
            "articlesLabel": "articles",""",
    "fr": """
            "eyebrow": "Actualités & conseils",
            "sortLabel": "Trier par",
            "sortNewest": "Plus récents",
            "sortOldest": "Plus anciens",
            "publisherBadge": "Bill Maniac Admin",
            "publishedOn": "Publié le",
            "previous": "Précédent",
            "next": "Suivant",
            "pageLabel": "Page",
            "ofLabel": "sur",
            "showingLabel": "Affichage",
            "articlesLabel": "articles",""",
    "es": """
            "eyebrow": "Noticias y guías",
            "sortLabel": "Ordenar por",
            "sortNewest": "Más recientes",
            "sortOldest": "Más antiguos",
            "publisherBadge": "Bill Maniac Admin",
            "publishedOn": "Publicado el",
            "previous": "Anterior",
            "next": "Siguiente",
            "pageLabel": "Página",
            "ofLabel": "de",
            "showingLabel": "Mostrando",
            "articlesLabel": "artículos",""",
    "id": """
            "eyebrow": "Wawasan & pembaruan",
            "sortLabel": "Urutkan",
            "sortNewest": "Terbaru dulu",
            "sortOldest": "Terlama dulu",
            "publisherBadge": "Bill Maniac Admin",
            "publishedOn": "Diterbitkan",
            "previous": "Sebelumnya",
            "next": "Berikutnya",
            "pageLabel": "Halaman",
            "ofLabel": "dari",
            "showingLabel": "Menampilkan",
            "articlesLabel": "artikel",""",
}

COMING_SOON_AFTER = {
    "en": '"comingSoonText": "We\'re working on bringing you insightful articles. Stay tuned!",',
    "fr": '"comingSoonText": "Nous travaillons à vous apporter des articles pertinents. Restez à l\'écoute !",',
    "es": '"comingSoonText": "Estamos trabajando para traerte artículos interesantes. ¡Mantente atento!",',
    "id": '"comingSoonText": "Kami sedang menyiapkan artikel-artikel bermanfaat. Pantau terus!",',
}


def b64(text: str) -> str:
    return "data:text/javascript;base64," + base64.b64encode(text.encode("utf-8")).decode("ascii")


def patch_translations(trans: str) -> str:
    for lang, (old_intro, new_intro) in INTRO_UPDATES.items():
        if old_intro in trans:
            trans = trans.replace(old_intro, new_intro, 1)
        elif new_intro not in trans:
            raise SystemExit(f"intro string not found for {lang}")

    if '"publisherBadge"' not in trans:
        for lang, anchor in COMING_SOON_AFTER.items():
            if anchor not in trans:
                raise SystemExit(f"comingSoonText anchor not found for {lang}")
            trans = trans.replace(anchor, anchor + UI_KEYS[lang], 1)

    return trans


def main() -> None:
    if MARKER not in BLOG_SRC:
        raise SystemExit(f"Missing marker {MARKER} in BLOG_SRC")

    html = INDEX.read_text()
    m = re.search(r"(<script type=\"importmap\">)(.*?)(</script>)", html, re.S)
    if not m:
        raise SystemExit("importmap not found")

    imap = json.loads(m.group(2))
    trans = base64.b64decode(imap["imports"]["@/translations"].split(",", 1)[1]).decode("utf-8")
    trans = patch_translations(trans)
    imap["imports"]["@/translations"] = b64(trans)

    blog_key = "@/components/Blog"
    imap["imports"][blog_key] = b64(BLOG_SRC)

    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print(f"Patched blog UI in {INDEX}")


if __name__ == "__main__":
    main()
