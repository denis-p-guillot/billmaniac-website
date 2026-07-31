# Bill Maniac public website

Marketing site for **[billmaniac.win](https://billmaniac.win)** on Cloudflare Pages.

## SEO (Cloudflare-compatible)

| Piece | Role |
|-------|------|
| `functions/seo-config.js` | Source of truth for pages + meta |
| `functions/_middleware.js` | Serves `/sitemap.xml` and `/sitemap-images.xml` with explicit XML headers |
| `functions/api/sitemap-notify.js` | Authenticated endpoint to push URLs to search engines |
| `dist/robots.txt` | Points crawlers at the sitemap |
| `dist/{INDEXNOW_KEY}.txt` | IndexNow ownership proof |
| `functions/_middleware.js` | Per-path title / canonical / Open Graph injection |
| `dist/_redirects` / `_headers` | Clean URLs + cache hints |

## Automatic sitemap update + submit

### 1. Regenerate sitemap (from SEO config)

```bash
npm run sitemap:generate
```

Writes `dist/sitemap.xml`, the IndexNow key file, and `functions/_sitemap-meta.js`.

### 2. Submit to sitemap / IndexNow APIs

```bash
# Direct IndexNow submit from this machine
npm run sitemap:submit -- --force

# Or call the live Cloudflare endpoint (uses Pages secrets)
npm run sitemap:submit:api
```

**Services used**
- **IndexNow** (`api.indexnow.org`) — Bing, Yandex, Seznam, Naver, …
- **Bing Webmaster `SubmitFeed`** — optional, if `BING_WEBMASTER_API_KEY` is set
- **Google** — anonymous sitemap ping is deprecated; set `GOOGLE_SITEMAP_PING_URL` only if you have a custom notifier / Search Console automation

### 3. One-shot deploy (build sitemap → Pages → notify)

```bash
cp .env.example .env   # fill secrets once
npm run deploy
```

### Cloudflare Pages secrets

```bash
# IndexNow key (same value as config/indexnow.key)
npx wrangler pages secret put INDEXNOW_KEY --project-name=billmaniac-website

# Protects POST /api/sitemap-notify
npx wrangler pages secret put SITEMAP_NOTIFY_SECRET --project-name=billmaniac-website

# Optional
npx wrangler pages secret put BING_WEBMASTER_API_KEY --project-name=billmaniac-website

# Contact form (/api/contact) — relay enquiries to contact@billmaniac.win via Resend
npx wrangler pages secret put TURNSTILE_SECRET_KEY --project-name=billmaniac-website
npx wrangler pages secret put RESEND_API_KEY --project-name=billmaniac-website
```

Plain vars (in `wrangler.json` or Pages Settings): `TURNSTILE_SITE_KEY`, `CONTACT_TO_EMAIL`, optional `CONTACT_FROM_EMAIL`.

## Analytics (SEO insights)

`scripts/patch-analytics.py` runs on every deploy and:

- Keeps **Google Analytics 4** (`G-FY5RTLMWZ9`) with `send_page_view: false` so the SPA does not double-count
- Sends a **page view on every client route change** (`/contact`, `/pricing`, etc.) via `@/seo` — critical for measuring SEO landing pages
- Fires a **`contact_form_submit`** event when the contact form succeeds
- Optionally injects **Cloudflare Web Analytics** when `CF_WEB_ANALYTICS_TOKEN` is set in `.env`

Link GA4 to [Google Search Console](https://search.google.com/search-console) (GA4 Admin → Product links → Search Console links) to correlate queries with on-site behaviour.

## AI SEO optimization

Programmatic loop to improve meta titles/descriptions from search intent + optional GSC signals:

| Piece | Role |
|-------|------|
| `functions/seo-config.js` | Base SEO for every route (server + sitemap) |
| `functions/seo-overrides.json` | AI-generated title/description/keyword patches (reviewable in git) |
| `scripts/seo-ai-optimize.mjs` | Calls OpenAI, writes overrides + report |
| `scripts/sync-client-seo.mjs` | Syncs merged SEO into SPA `@/seo` (runs on deploy) |
| `config/seo-signals.example.json` | Template for GSC/GA4 performance export |

```bash
cp config/seo-signals.example.json config/seo-signals.json   # optional
# OPENAI_API_KEY in .env

npm run seo:optimize                    # dry-run → config/seo-ai-report.json
npm run seo:optimize -- --apply         # write overrides + sync client
npm run deploy                          # publish + IndexNow
```

Update `config/seo-signals.json` monthly with top queries/pages from Search Console so the AI prioritizes pages with impressions but low CTR.

Optional plain var (not secret) for `<lastmod>`:

```bash
npx wrangler pages deployment tail --project-name=billmaniac-website
# or set SITEMAP_LASTMOD in the Pages project Settings → Environment variables
```

### Cron / external automation

Point any scheduler (GitHub Actions, cron-job.org, …) at:

```bash
curl -X POST https://billmaniac.win/api/sitemap-notify \
  -H "Authorization: Bearer $SITEMAP_NOTIFY_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"force":true}'
```

Add pages to `functions/seo-config.js` → run `npm run deploy` (or generate + submit). The live `/sitemap.xml` always mirrors the config.

## Deploy (Pages only)

```bash
npm run deploy:pages
```
