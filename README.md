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
```

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
