import {
  sendContactEmail,
  validateContactPayload,
  verifyTurnstile,
} from "../contact-lib.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function clientIp(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    ""
  );
}

function handleConfig(env) {
  const turnstileSiteKey = (env.TURNSTILE_SITE_KEY || "").trim();
  return json({
    ok: true,
    turnstileSiteKey: turnstileSiteKey || null,
    turnstileEnabled: Boolean(turnstileSiteKey && env.TURNSTILE_SECRET_KEY),
  });
}

async function handleSubmit(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "invalid_json" }, 400);
  }

  // Honeypot — pretend success for bots.
  if (String(body?.website || "").trim()) {
    return json({ ok: true });
  }

  const validated = validateContactPayload(body);
  if (!validated.ok) {
    return json({ ok: false, error: "validation", fields: validated.errors }, 400);
  }

  const turnstileOk = await verifyTurnstile(
    env,
    body?.turnstileToken || body?.turnstile,
    clientIp(request),
  );
  if (!turnstileOk) {
    return json({ ok: false, error: "captcha" }, 403);
  }

  try {
    await sendContactEmail(env, validated.data);
  } catch (err) {
    console.error("Contact email failed:", err);
    return json({ ok: false, error: "send_failed" }, 502);
  }

  return json({ ok: true });
}

/**
 * /api/contact
 * GET → public Turnstile site key
 * POST → submit enquiry (Turnstile + Resend)
 */
export async function onRequest(context) {
  const { request, env } = context;
  const method = request.method.toUpperCase();

  if (method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-methods": "GET, HEAD, POST, OPTIONS",
        "access-control-allow-headers": "content-type",
      },
    });
  }

  if (method === "GET" || method === "HEAD") {
    const res = handleConfig(env);
    if (method === "HEAD") {
      return new Response(null, { status: res.status, headers: res.headers });
    }
    return res;
  }

  if (method === "POST") {
    return handleSubmit(request, env);
  }

  return json({ ok: false, error: "method_not_allowed" }, 405);
}
