const APK_KEYS = ["billmaniac-pro.apk", "billmaniac-pro-v8.apk"];
const APK_CONTENT_TYPE = "application/vnd.android.package-archive";

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

/**
 * POST /api/upload-apk
 * Auth: Authorization: Bearer <SITEMAP_NOTIFY_SECRET>
 * Body: raw APK bytes
 */
export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method.toUpperCase();

  if (method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-methods": "POST, OPTIONS",
        "access-control-allow-headers": "authorization, content-type, x-sitemap-notify-secret",
      },
    });
  }

  if (method !== "POST") {
    return json({ ok: false, error: `Method ${method} not allowed` }, 405);
  }

  const gate = assertAuthorized(request, env);
  if (!gate.ok) return gate.response;

  const bucket = env.DOWNLOADS;
  if (!bucket) {
    return json({ ok: false, error: "Downloads storage is not configured" }, 503);
  }

  const bytes = await request.arrayBuffer();
  if (!bytes.byteLength) {
    return json({ ok: false, error: "Empty request body" }, 400);
  }

  for (const key of APK_KEYS) {
    await bucket.put(key, bytes, {
      httpMetadata: {
        contentType: APK_CONTENT_TYPE,
        cacheControl: "no-store, must-revalidate",
      },
    });
  }

  return json({
    ok: true,
    keys: APK_KEYS,
    bytes: bytes.byteLength,
    url: "https://billmaniac.win/downloads/billmaniac-pro-v8.apk",
  });
}
