#!/usr/bin/env node
/**
 * Shared helpers for AI SEO optimization.
 */
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
export const ROOT = join(__dirname, "..");
const OVERRIDES_JSON_PATH = join(ROOT, "functions/seo-overrides.json");
const OVERRIDES_JS_PATH = join(ROOT, "functions/seo-overrides.js");
export const SIGNALS_PATH = join(ROOT, "config/seo-signals.json");
export const REPORT_PATH = join(ROOT, "config/seo-ai-report.json");

export const PRODUCT_CONTEXT = `
Bill Maniac (billmaniac.win) — AI expense tracker for web + Android.
Company: PT. DEVINCI GROUP INDONESIA (Jakarta).
Core value: scan receipts with AI, private Cloudflare cloud (D1 + R2), categorize spending, export CSV/Excel.
Plans: Free, Pro ($18/yr), Maniac ($60/yr).
Audiences: freelancers, small businesses, finance teams, Indonesia + global English/French/Spanish.
Differentiators: private cloud (not Google Sheets), Android app with PIN/biometric, no vendor lock-in exports.
`.trim();

export function loadEnvFile() {
  for (const name of [".env", ".env.local"]) {
    const path = join(ROOT, name);
    if (!existsSync(path)) continue;
    for (const line of readFileSync(path, "utf8").split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
      const i = trimmed.indexOf("=");
      const k = trimmed.slice(0, i).trim();
      let v = trimmed.slice(i + 1).trim();
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      if (!(k in process.env)) process.env[k] = v;
    }
  }
}

export async function loadSeoPages() {
  const mod = await import(pathToFileURL(join(ROOT, "functions/seo-config.js")).href);
  return mod.SEO_PAGES;
}

export function loadSignals() {
  if (!existsSync(SIGNALS_PATH)) return null;
  try {
    return JSON.parse(readFileSync(SIGNALS_PATH, "utf8"));
  } catch {
    return null;
  }
}

export function validatePageMeta(path, meta) {
  const errors = [];
  if (!meta.title || meta.title.length < 20) errors.push("title too short");
  if (meta.title && meta.title.length > 70) errors.push("title too long");
  if (!meta.description || meta.description.length < 80) errors.push("description too short");
  if (meta.description && meta.description.length > 170) errors.push("description too long");
  if (errors.length) {
    throw new Error(`${path}: ${errors.join(", ")}`);
  }
  return {
    title: meta.title.trim(),
    description: meta.description.trim(),
    keywords: (meta.keywords || "").trim(),
  };
}

export async function callOpenAi({ apiKey, model, system, user }) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      temperature: 0.4,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    const msg = data.error?.message || res.statusText;
    throw new Error(`OpenAI API error (${res.status}): ${msg}`);
  }

  const content = data.choices?.[0]?.message?.content;
  if (!content) throw new Error("OpenAI returned empty content");
  return { parsed: JSON.parse(content), model: data.model || model };
}

export function buildOptimizationPrompt({ pages, signals, focusPaths }) {
  const pageList = focusPaths
    .map((path) => {
      const p = pages[path];
      return `- ${path} [${p.index === false ? "noindex" : "index"}]
  title: ${p.title}
  description: ${p.description}
  keywords: ${p.keywords || "(none)"}`;
    })
    .join("\n");

  const signalsBlock = signals
    ? `\nPerformance signals (from Search Console / Analytics export):\n${JSON.stringify(signals, null, 2)}\n`
    : "";

  return `${signalsBlock}
Current pages:
${pageList}

Optimize ONLY the pages listed above for organic search growth.
Prioritize high-intent queries: receipt scanner app, expense tracker, AI receipt OCR, freelancer expenses, small business bills, Android receipt app.
Keep copy accurate — do not invent features.
Titles: 45–60 chars when possible. Meta descriptions: 130–155 chars with a clear benefit + CTA verb.
Return JSON:
{
  "strategy": "2-4 sentence SEO strategy summary",
  "priorities": ["path1", "path2"],
  "pages": {
    "/path": { "title": "...", "description": "...", "keywords": "comma, separated" }
  },
  "contentIdeas": [
    { "page": "/blog", "topic": "...", "targetQuery": "...", "rationale": "..." }
  ]
}`;
}
