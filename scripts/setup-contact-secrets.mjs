#!/usr/bin/env node
/**
 * Configure Cloudflare Pages secrets for the contact form:
 *   TURNSTILE_SECRET_KEY, RESEND_API_KEY
 *
 * Usage:
 *   RESEND_API_KEY=re_... node scripts/setup-contact-secrets.mjs
 *
 * Turnstile secret (pick one):
 *   - TURNSTILE_SECRET_KEY=reuse existing secret (same as auth worker)
 *   - CLOUDFLARE_API_TOKEN with Account → Turnstile → Edit → rotate widget secret
 *
 * Uses Wrangler OAuth for Pages secrets (unset CLOUDFLARE_API_TOKEN in shell).
 */
import { spawnSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const ACCOUNT_ID = "9345927ca3f495f89fdaddea61a5e3f9";
const PROJECT = "billmaniac-website";
const SITE_KEY = "0x4AAAAAAD7WNLls--dAbzwY";
const WIDGET_NAME = "BillManiac Email Auth";
const AUTH_DIR = join(ROOT, "..", "billmaniac-pro", "workers", "auth");

function loadEnvFile() {
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

function run(cmd, args, { input, cwd = ROOT, oauth = false } = {}) {
  const env = { ...process.env, CLOUDFLARE_ACCOUNT_ID: ACCOUNT_ID };
  if (oauth) {
    delete env.CLOUDFLARE_API_TOKEN;
    delete env.CF_API_TOKEN;
  }
  const res = spawnSync(cmd, args, {
    cwd,
    input,
    env,
    encoding: "utf8",
    stdio: ["pipe", "pipe", "pipe"],
  });
  if (res.status !== 0) {
    throw new Error(
      res.stderr?.trim() || res.stdout?.trim() || `${cmd} ${args.join(" ")} failed`,
    );
  }
  return res.stdout;
}

async function cfFetch(token, path, init = {}) {
  const res = await fetch(`https://api.cloudflare.com/client/v4${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  const data = await res.json();
  if (!data.success) {
    const message =
      data.errors?.map((e) => e.message).join("; ") || "Cloudflare API error";
    throw new Error(message);
  }
  return data;
}

async function resolveTurnstileSecret() {
  if (process.env.TURNSTILE_SECRET_KEY?.trim()) {
    console.log("Using TURNSTILE_SECRET_KEY from environment.");
    return process.env.TURNSTILE_SECRET_KEY.trim();
  }

  const token =
    process.env.CLOUDFLARE_SETUP_TOKEN?.trim() ||
    process.env.CLOUDFLARE_API_TOKEN?.trim() ||
    "";
  if (!token) {
    throw new Error(
      "Missing Turnstile secret. Set TURNSTILE_SECRET_KEY, or CLOUDFLARE_API_TOKEN with Account → Turnstile → Edit to rotate the widget secret.",
    );
  }

  const widgets = (await cfFetch(token, `/accounts/${ACCOUNT_ID}/challenges/widgets?per_page=50`))
    .result;
  const widget =
    widgets.find((w) => w.sitekey === SITE_KEY) ||
    widgets.find((w) => w.name === WIDGET_NAME);
  if (!widget?.sitekey) {
    throw new Error(`Turnstile widget "${WIDGET_NAME}" not found.`);
  }

  console.log(`Rotating Turnstile secret for "${widget.name}"…`);
  const rotated = await cfFetch(
    token,
    `/accounts/${ACCOUNT_ID}/challenges/widgets/${widget.sitekey}/rotate_secret`,
    {
      method: "POST",
      body: JSON.stringify({ invalidate_immediately: true }),
    },
  );
  const secret = rotated.result?.secret;
  if (!secret) throw new Error("Turnstile rotate_secret did not return a secret.");
  console.log("Obtained new Turnstile secret (old secret invalidated).");
  return secret;
}

function putPagesSecret(name, value) {
  console.log(`Setting Pages secret ${name}…`);
  run(
    "npx",
    ["wrangler", "pages", "secret", "put", name, "--project-name", PROJECT],
    { input: `${value}\n`, oauth: true },
  );
}

function putAuthSecret(name, value) {
  if (!existsSync(join(AUTH_DIR, "wrangler.toml"))) {
    console.log("Auth worker not found — skipping auth Turnstile sync.");
    return;
  }
  console.log(`Syncing auth worker secret ${name}…`);
  run(
    "npx",
    ["wrangler", "secret", "put", name, "--name", "billmaniac-pro-auth"],
    { input: `${value}\n`, cwd: AUTH_DIR, oauth: true },
  );
}

async function verifyContactApi() {
  const res = await fetch("https://billmaniac.win/api/contact");
  const data = await res.json();
  if (!data.ok) throw new Error("Contact API health check failed.");
  console.log("Contact API:", JSON.stringify(data));
  if (!data.turnstileEnabled) {
    console.warn("Warning: turnstileEnabled is still false (check secret name / redeploy).");
  }
}

async function main() {
  loadEnvFile();

  const resendKey = process.env.RESEND_API_KEY?.trim();
  if (!resendKey?.startsWith("re_")) {
    console.error(
      "Missing RESEND_API_KEY. Create one at https://resend.com/api-keys then rerun:\n\n" +
        "  RESEND_API_KEY=re_... node scripts/setup-contact-secrets.mjs",
    );
    process.exit(1);
  }

  let turnstileSecret;
  let rotated = false;
  try {
    if (process.env.TURNSTILE_SECRET_KEY?.trim()) {
      turnstileSecret = process.env.TURNSTILE_SECRET_KEY.trim();
    } else {
      turnstileSecret = await resolveTurnstileSecret();
      rotated = true;
    }
  } catch (err) {
    console.error(`Turnstile setup failed: ${err.message}`);
    console.error(
      "\nOption A — reuse auth worker secret (if you saved it):\n" +
        "  TURNSTILE_SECRET_KEY=... RESEND_API_KEY=re_... node scripts/setup-contact-secrets.mjs\n\n" +
        "Option B — rotate via Cloudflare API token with Turnstile Edit:\n" +
        "  CLOUDFLARE_API_TOKEN=... RESEND_API_KEY=re_... node scripts/setup-contact-secrets.mjs\n\n" +
        "Option C — Cloudflare dashboard → Turnstile → rotate secret, then use Option A.",
    );
    process.exit(1);
  }

  putPagesSecret("TURNSTILE_SECRET_KEY", turnstileSecret);
  putPagesSecret("RESEND_API_KEY", resendKey);

  if (rotated) {
    putAuthSecret("TURNSTILE_SECRET_KEY", turnstileSecret);
    console.log("Auth worker Turnstile secret updated to match rotation.");
  }

  console.log("\nSecrets stored on billmaniac-website (production).");
  console.log("Waiting a few seconds for Pages to propagate secrets…");
  await new Promise((r) => setTimeout(r, 5000));

  await verifyContactApi();
  console.log("\nDone. Test the form at https://billmaniac.win/contact");
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
