const APK_CONTENT_TYPE = "application/vnd.android.package-archive";

export async function onRequestGet(context) {
  const { env, params } = context;
  const segments = params.path;
  const key = Array.isArray(segments) ? segments.join("/") : segments;

  if (!key || key.includes("..")) {
    return new Response("Not found", { status: 404 });
  }

  const bucket = env.DOWNLOADS;
  if (!bucket) {
    return new Response("Downloads storage is not configured", { status: 503 });
  }

  const object = await bucket.get(key);
  if (!object) {
    return new Response("Not found", { status: 404 });
  }

  const filename = key.split("/").pop() || "download.apk";
  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("Content-Type", APK_CONTENT_TYPE);
  headers.set("Content-Disposition", `attachment; filename="${filename}"`);
  // APK updates must not be edge-cached — stale builds break auth/signup fixes.
  headers.set("Cache-Control", "no-store, must-revalidate");
  headers.set("CDN-Cache-Control", "no-store");

  return new Response(object.body, { headers });
}
