#!/usr/bin/env python3
"""Inject config/blog-posts.json into @/translations for en, fr, es, id."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "dist/index.html"
BLOG_JSON = ROOT / "config/blog-posts.json"


def b64(text: str) -> str:
    return "data:text/javascript;base64," + base64.b64encode(text.encode("utf-8")).decode("ascii")


def posts_to_js(posts: list, indent: str = "                ") -> str:
    """Serialize posts as a flat JS array (one object per post, no extra wrapper [])."""
    chunks = []
    for post in posts:
        raw = json.dumps(post, ensure_ascii=False, indent=4)
        lines = raw.splitlines()
        chunks.append("\n".join(indent + line for line in lines))
    return ",\n".join(chunks)


def find_bracket_end(text: str, open_idx: int) -> int:
    """Return index after the matching closing ] for text[open_idx] == '['."""
    depth = 0
    i = open_idx
    while i < len(text):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise SystemExit("posts array end not found")


def replace_posts_block(trans: str, lang: str, posts: list) -> str:
    lang_order = ["en", "fr", "es", "id"]
    idx = lang_order.index(lang)
    pos = 0
    blog_start = -1
    for _ in range(idx + 1):
        blog_start = trans.find('"blog": {', pos)
        if blog_start < 0:
            raise SystemExit(f"blog section not found for lang {lang}")
        pos = blog_start + 1

    posts_label = trans.find('"posts": [', blog_start)
    if posts_label < 0:
        raise SystemExit(f'"posts" not found in blog for {lang}')

    array_start = posts_label + len('"posts": ')
    array_end = find_bracket_end(trans, array_start)
    new_posts = '"posts": [\n' + posts_to_js(posts) + "\n            ]"
    return trans[:posts_label] + new_posts + trans[array_end:]


def main() -> None:
    if not BLOG_JSON.exists():
        raise SystemExit(f"Missing {BLOG_JSON} — run: node scripts/generate-blog-posts.mjs")

    data = json.loads(BLOG_JSON.read_text())
    html = INDEX.read_text()
    m = re.search(r"(<script type=\"importmap\">)(.*?)(</script>)", html, re.S)
    if not m:
        raise SystemExit("importmap not found")

    imap = json.loads(m.group(2))
    trans = base64.b64decode(imap["imports"]["@/translations"].split(",", 1)[1]).decode("utf-8")

    for lang in ("en", "fr", "es", "id"):
        posts = data[lang]["posts"]
        trans = replace_posts_block(trans, lang, posts)
        print(f"  {lang}: {len(posts)} posts")

    imap["imports"]["@/translations"] = b64(trans)

    blog_key = "@/components/Blog"
    blog_src = base64.b64decode(imap["imports"][blog_key].split(",", 1)[1]).decode("utf-8")
    blog_old = '(_jsxs("article", { className: "bg-slate-900 p-8 sm:p-12 rounded-lg border border-slate-800 shadow-xl", children:'
    blog_new = '(_jsxs("article", { id: post.slug, className: "bg-slate-900 p-8 sm:p-12 rounded-lg border border-slate-800 shadow-xl", children:'
    if blog_old in blog_src and "id: post.slug" not in blog_src:
        imap["imports"][blog_key] = b64(blog_src.replace(blog_old, blog_new, 1))

    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print(f"Patched blog posts in {INDEX}")


if __name__ == "__main__":
    main()
