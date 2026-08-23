// Password-protects the whole site with HTTP Basic Auth.
// Username/password come from Cloudflare Pages environment variables
// (set in the dashboard, not committed to git).
export async function onRequest(context) {
  const auth = context.request.headers.get("Authorization");
  const EXPECTED_USER = context.env.SITE_USERNAME || "sonia";
  const EXPECTED_PASS = context.env.SITE_PASSWORD;

  if (!EXPECTED_PASS) {
    // No password configured — fail closed rather than open.
    return new Response("Site not configured", { status: 500 });
  }

  if (auth) {
    const [scheme, encoded] = auth.split(" ");
    if (scheme === "Basic" && encoded) {
      const decoded = atob(encoded);
      const idx = decoded.indexOf(":");
      const user = decoded.slice(0, idx);
      const pass = decoded.slice(idx + 1);
      if (user === EXPECTED_USER && pass === EXPECTED_PASS) {
        return context.next();
      }
    }
  }

  return new Response("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Sonia\'s Drawings"' },
  });
}
