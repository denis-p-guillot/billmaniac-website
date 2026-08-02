#!/usr/bin/env node
/**
 * Import GA4 "Pages and screens" CSV export into config/seo-signals.json.
 *
 * Usage:
 *   npm run seo:import-ga4 -- ~/Downloads/Pages_and_screens_Page_path_and_screen_class.csv
 *   node scripts/import-ga4-pages.mjs path/to/export.csv
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const OUT = join(ROOT, "config/seo-signals.json");

function parseGa4Csv(text) {
  const lines = text.split(/\r?\n/);
  const rows = [];
  let header = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    if (!header) {
      header = trimmed.split(",").map((h) => h.trim());
      continue;
    }
    const cols = trimmed.split(",");
    const record = {};
    header.forEach((key, i) => {
      record[key] = (cols[i] ?? "").trim();
    });
    rows.push(record);
  }

  return rows;
}

function num(value) {
  const n = Number(String(value).replace(/,/g, ""));
  return Number.isFinite(n) ? n : 0;
}

function main() {
  const input = process.argv[2];
  if (!input) {
    console.error("Usage: node scripts/import-ga4-pages.mjs <ga4-pages-export.csv>");
    process.exit(1);
  }

  const csvPath = resolve(input);
  if (!existsSync(csvPath)) {
    console.error(`File not found: ${csvPath}`);
    process.exit(1);
  }

  const rows = parseGa4Csv(readFileSync(csvPath, "utf8"));
  const pathKey = "Page path and screen class";

  const topPages = rows
    .filter((row) => row[pathKey] && !row[pathKey].startsWith("/checkout"))
    .map((row) => ({
      path: row[pathKey],
      views: num(row.Views),
      activeUsers: num(row["Active users"]),
      viewsPerUser: num(row["Views per active user"]),
      avgEngagementSec: num(row["Average engagement time per active user"]),
      events: num(row["Event count"]),
    }))
    .sort((a, b) => b.views - a.views);

  const totalViews = topPages.reduce((sum, p) => sum + p.views, 0);
  const highEngagement = topPages
    .filter((p) => p.avgEngagementSec >= 60 && p.views >= 3)
    .map((p) => p.path);

  const signals = {
    updatedAt: new Date().toISOString().slice(0, 10),
    source: `GA4 Pages export: ${csvPath.split("/").pop()}`,
    dateRange: "See CSV header (# Start date / End date)",
    summary: {
      totalViews,
      pageCount: topPages.length,
      highEngagementPaths: highEngagement,
      topPath: topPages[0]?.path ?? "/",
    },
    topPages,
    topQueries: [],
    notes: [
      "Imported from GA4 Pages and screens export.",
      "High engagement paths are commercial-intent pages — prioritize meta titles/descriptions there.",
      "Add GSC Queries CSV to topQueries for query-level optimization (npm run seo:optimize).",
    ],
  };

  writeFileSync(OUT, JSON.stringify(signals, null, 2) + "\n", "utf8");
  console.log(`Wrote ${OUT}`);
  console.log(`  ${topPages.length} pages, ${totalViews} total views`);
  console.log(`  High engagement: ${highEngagement.join(", ") || "(none)"}`);
  console.log("\nNext: npm run seo:optimize -- --apply && npm run deploy");
}

main();
