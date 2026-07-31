#!/usr/bin/env node
/**
 * Generate 15 blog posts (EN + FR + ES + ID) via OpenAI.
 * Output: config/blog-posts.json
 */
import { writeFileSync, existsSync, readFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const OUT = join(ROOT, "config/blog-posts.json");

const SCHEDULE = [
  { slug: "getting-started-bill-maniac", iso: "2025-05-05", topic: "Getting started with Bill Maniac in 5 minutes" },
  { slug: "ai-receipt-scanning-guide", iso: "2025-06-05", topic: "How AI receipt scanning works and best practices" },
  { slug: "ai-receipt-scanner-benefits", iso: "2025-07-05", topic: "Top 5 benefits of an AI receipt scanner for freelancers" },
  { slug: "freelance-expense-management", iso: "2025-08-05", topic: "Freelance expense management without spreadsheets" },
  { slug: "small-business-expense-tracker", iso: "2025-09-05", topic: "Why small businesses need a dedicated expense tracker" },
  { slug: "year-end-expense-review", iso: "2025-10-05", topic: "Year-end expense review checklist" },
  { slug: "digital-receipts-tax-deductions", iso: "2025-11-05", topic: "Digital receipts for tax deductions and audits" },
  { slug: "private-cloud-vs-spreadsheets", iso: "2025-12-05", topic: "Private cloud storage vs Google Sheets for bills" },
  { slug: "new-year-finance-organization", iso: "2026-01-05", topic: "Organize your finances for the new year" },
  { slug: "bill-maniac-android-guide", iso: "2026-02-05", topic: "Bill Maniac Android app: scan on the go with PIN lock" },
  { slug: "category-budgets-that-work", iso: "2026-03-05", topic: "Category budgets that actually stick" },
  { slug: "export-csv-excel-accountant", iso: "2026-04-05", topic: "Export CSV and Excel for your accountant" },
  { slug: "privacy-first-expense-tracking", iso: "2026-05-05", topic: "Privacy-first expense tracking on Cloudflare" },
  { slug: "improve-receipt-scan-accuracy", iso: "2026-06-05", topic: "Tips to improve receipt OCR accuracy" },
  { slug: "bill-maniac-pricing-plans", iso: "2026-07-05", topic: "Free vs Pro vs Maniac: choosing the right plan" },
];

function loadEnv() {
  const p = join(ROOT, ".env");
  if (!existsSync(p)) return;
  for (const line of readFileSync(p, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#") || !t.includes("=")) continue;
    const i = t.indexOf("=");
    const k = t.slice(0, i).trim();
    let v = t.slice(i + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    if (!(k in process.env) && !v.includes("set locally")) process.env[k] = v;
  }
}

async function openAi(apiKey, user) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: process.env.OPENAI_BLOG_MODEL || "gpt-4o-mini",
      temperature: 0.5,
      response_format: { type: "json_object" },
      messages: [
        {
          role: "system",
          content: `You write SEO blog posts for Bill Maniac (billmaniac.win), an AI expense tracker with private Cloudflare cloud storage and Android app by PT. DEVINCI GROUP INDONESIA.
Return valid JSON only.`,
        },
        { role: "user", content: user },
      ],
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || res.statusText);
  return JSON.parse(data.choices[0].message.content);
}

function formatEnDate(iso) {
  const d = new Date(iso + "T12:00:00Z");
  return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
}

async function generateBatch(apiKey, items) {
  const spec = items
    .map(
      (x) =>
        `- slug: ${x.slug}\n  publishDate: ${x.iso} (display as ${formatEnDate(x.iso)})\n  topic: ${x.topic}`,
    )
    .join("\n");

  const prompt = `Create ${items.length} blog posts for Bill Maniac.

Posts (publish in first week of month — use exact display dates):
${spec}

Each post JSON:
{
  "slug": "...",
  "title": "60 chars max, compelling for SEO",
  "author": "The Bill Maniac Team",
  "date": "Month D, YYYY",
  "content": [
    { "type": "p", "text": "intro paragraph" },
    { "type": "h3", "text": "section heading" },
    { "type": "p", "text": "..." },
    { "type": "ul", "items": ["bullet 1", "bullet 2"] },
    { "type": "strong", "text": "optional callout label" },
    { "type": "h3", "text": "Conclusion" },
    { "type": "p", "text": "closing with soft CTA to try Bill Maniac" }
  ]
}

Rules:
- 6–10 content blocks per post, 500–800 words total
- Accurate product facts: AI OCR, D1+R2 cloud, CSV/Excel export, Free/Pro/Maniac plans, Android PIN
- No fake statistics
- Mention billmaniac.win naturally once

Return: { "posts": [ ...${items.length} posts in same order ] }`;

  const { posts } = await openAi(apiKey, prompt);
  return posts;
}

async function translatePosts(apiKey, enPosts) {
  const prompt = `Translate these Bill Maniac blog posts to French (fr), Spanish (es), and Indonesian (id).
Keep slug identical. Localize dates (fr: "5 mai 2025", es: "5 de mayo de 2025", id: "5 Mei 2025").
Author: fr "L'équipe Bill Maniac", es "El equipo de Bill Maniac", id "Tim Bill Maniac".
Preserve content block types (p, h3, ul, strong).

English posts:
${JSON.stringify(enPosts)}

Return:
{
  "fr": { "posts": [...] },
  "es": { "posts": [...] },
  "id": { "posts": [...] }
}`;

  return openAi(apiKey, prompt);
}

async function main() {
  loadEnv();
  const apiKey = process.env.OPENAI_API_KEY?.trim();
  if (!apiKey?.startsWith("sk-")) {
    console.error("Missing OPENAI_API_KEY in .env");
    process.exit(1);
  }

  mkdirSync(join(ROOT, "config"), { recursive: true });
  const allEn = [];

  for (let i = 0; i < SCHEDULE.length; i += 5) {
    const batch = SCHEDULE.slice(i, i + 5);
    console.log(`Generating EN batch ${i / 5 + 1}… (${batch.map((b) => b.slug).join(", ")})`);
    const posts = await generateBatch(apiKey, batch);
    allEn.push(...posts);
  }

  // Newest first (use schedule ISO dates)
  const isoBySlug = Object.fromEntries(SCHEDULE.map((s) => [s.slug, s.iso]));
  allEn.sort((a, b) => isoBySlug[b.slug].localeCompare(isoBySlug[a.slug]));

  console.log("Translating to fr, es, id (batch 1)…");
  const t1 = await translatePosts(apiKey, allEn.slice(0, 8));
  console.log("Translating to fr, es, id (batch 2)…");
  const t2 = await translatePosts(apiKey, allEn.slice(8));

  const mergeLang = (lang) => ({
    posts: [...(t1[lang]?.posts || []), ...(t2[lang]?.posts || [])].sort(
      (a, b) => isoBySlug[b.slug].localeCompare(isoBySlug[a.slug]),
    ),
  });

  const out = {
    generatedAt: new Date().toISOString(),
    schedule: SCHEDULE,
    en: { posts: allEn },
    fr: mergeLang("fr"),
    es: mergeLang("es"),
    id: mergeLang("id"),
  };

  writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n", "utf8");
  console.log(`Wrote ${allEn.length} posts × 4 languages → ${OUT}`);
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
