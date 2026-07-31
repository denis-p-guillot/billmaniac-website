const NAME_MAX = 120;
const SUBJECT_MAX = 200;
const MESSAGE_MIN = 10;
const MESSAGE_MAX = 5000;

export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || "").trim());
}

export function normalizeEmail(email) {
  return String(email || "").trim().toLowerCase();
}

export function validateContactPayload(body) {
  const errors = {};
  const name = String(body?.name || "").trim();
  const email = normalizeEmail(body?.email);
  const subject = String(body?.subject || "").trim();
  const message = String(body?.message || "").trim();

  if (!name || name.length > NAME_MAX) {
    errors.name = "invalid";
  }
  if (!isValidEmail(email)) {
    errors.email = "invalid";
  }
  if (subject.length > SUBJECT_MAX) {
    errors.subject = "invalid";
  }
  if (message.length < MESSAGE_MIN || message.length > MESSAGE_MAX) {
    errors.message = "invalid";
  }

  return {
    ok: Object.keys(errors).length === 0,
    errors,
    data: { name, email, subject, message },
  };
}

export async function verifyTurnstile(env, token, remoteIp) {
  const secret = env.TURNSTILE_SECRET_KEY;
  if (!secret) return true;
  if (!token) return false;

  const body = new URLSearchParams({
    secret,
    response: token,
  });
  if (remoteIp) body.set("remoteip", remoteIp);

  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await res.json();
  return data.success === true;
}

/** Normalize RESEND_API_KEY (trim, strip accidental "Bearer " prefix). */
export function resolveResendApiKey(env) {
  let key = String(env.RESEND_API_KEY || "")
    .trim()
    .replace(/^Bearer\s+/i, "");
  if (key.startsWith("re_")) return key;

  for (const name of Object.keys(env)) {
    if (!name.startsWith("re_")) continue;
    const value = String(env[name] || "")
      .trim()
      .replace(/^Bearer\s+/i, "");
    if (value.startsWith("re_")) return value;
    if (name.startsWith("re_")) return name;
  }
  return key;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export async function sendContactEmail(env, { name, email, subject, message }) {
  const apiKey = resolveResendApiKey(env);
  const to = (env.CONTACT_TO_EMAIL || "contact@billmaniac.win").trim();
  const from =
    env.CONTACT_FROM_EMAIL || "Bill Maniac Website <noreply@billmaniac.win>";
  const mailSubject = subject || `Website enquiry from ${name}`;

  const text = [
    "New contact form submission on billmaniac.win",
    "",
    `Name: ${name}`,
    `Email: ${email}`,
    `Subject: ${mailSubject}`,
    "",
    message,
  ].join("\n");

  const html = [
    "<p><strong>New contact form submission</strong> on billmaniac.win</p>",
    "<table cellpadding=\"4\" cellspacing=\"0\">",
    `<tr><td><strong>Name</strong></td><td>${escapeHtml(name)}</td></tr>`,
    `<tr><td><strong>Email</strong></td><td>${escapeHtml(email)}</td></tr>`,
    `<tr><td><strong>Subject</strong></td><td>${escapeHtml(mailSubject)}</td></tr>`,
    "</table>",
    `<p style="white-space:pre-wrap">${escapeHtml(message)}</p>`,
  ].join("");

  if (!apiKey) {
    console.log(`[Contact email] To: ${to}\n${text}`);
    return { delivered: false, devLogged: true };
  }

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      "User-Agent": "BillManiacWebsite/1.0 (Cloudflare Pages)",
    },
    body: JSON.stringify({
      from,
      reply_to: email,
      to: [to],
      subject: `[Bill Maniac] ${mailSubject}`,
      html,
      text,
      tags: [{ name: "category", value: "contact" }],
    }),
  });

  if (!res.ok) {
    const detail = await res.text();
    console.error(`Resend contact email failed (${res.status}): ${detail}`);
    throw new Error("EMAIL_SEND_FAILED");
  }

  return { delivered: true, devLogged: false };
}
