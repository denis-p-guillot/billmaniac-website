import { buildSitemapXml, listSitemapEntries, notifySearchEngines } from "../sitemap-lib.js";
import { SITE_ORIGIN } from "../seo-config.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function readToken(request) {
  const auth = request.headers.get("authorization") || "";
  if (auth.toLowerCase().startsWith("bearer ")) return auth.slice(7).trim();
  return (request.headers.get("x-sitemap-notify-secret") || "").trim();
}

function assertAuthorized(request, env) {
  const expected = (env.SITEMAP_NOTIFY_SECRET || "").trim();
  if (!expected) {
    return {
      ok: false,
      response: json(
        {
          ok: false,
          error: "SITEMAP_NOTIFY_SECRET is not configured on this Pages project",
        },
        503,
      ),
    };
  }
  const token = readToken(request);
  if (!token || token !== expected) {
    return { ok: false, response: json({ ok: false, error: "Unauthorized" }, 401) };
  }
  return { ok: true };
}

async function handleStatus(env) {
  const lastmod = env.SITEMAP_LASTMOD || new Date().toISOString().slice(0, 10);
  return json({
    ok: true,
    site: SITE_ORIGIN,
    lastmod,
    urlCount: listSitemapEntries(lastmod).length,
    sitemapXmlBytes: buildSitemapXml(lastmod).length,
    indexNowConfigured: Boolean(env.INDEXNOW_KEY),
    bingConfigured: Boolean(env.BING_WEBMASTER_API_KEY),
  });
}

async function handleNotify(env) {
  const result = await notifySearchEngines(env, {
    lastmod: env.SITEMAP_LASTMOD,
  });

  // IndexNow 429 = rate limited but request was understood; treat as soft success.
  const softOk =
    result.ok ||
    result.indexNow?.status === 429 ||
    result.indexNow?.status === 202 ||
    result.indexNow?.status === 200;

  return json(
    {
      ok: softOk,
      rateLimited: result.indexNow?.status === 429,
      site: SITE_ORIGIN,
      sitemapPreviewUrl: `${SITE_ORIGIN}/sitemap.xml`,
      urlSample: listSitemapEntries(env.SITEMAP_LASTMOD)
        .slice(0, 3)
        .map((e) => e.loc),
      ...result,
    },
    softOk ? 200 : 502,
  );
}

/**
 * /api/sitemap-notify
 * Auth: Authorization: Bearer <SITEMAP_NOTIFY_SECRET>
 * GET/HEAD → status; POST → submit to IndexNow (+ optional Bing/Google)
 */
export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method.toUpperCase();

  if (method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-methods": "GET, HEAD, POST, OPTIONS",
        "access-control-allow-headers": "authorization, content-type, x-sitemap-notify-secret",
      },
    });
  }

  const gate = assertAuthorized(request, env);
  if (!gate.ok) return gate.response;

  if (method === "GET" || method === "HEAD") {
    const res = await handleStatus(env);
    if (method === "HEAD") {
      return new Response(null, { status: res.status, headers: res.headers });
    }
    return res;
  }

  if (method === "POST") {
    return handleNotify(env);
  }

  return json({ ok: false, error: `Method ${method} not allowed` }, 405);
}
