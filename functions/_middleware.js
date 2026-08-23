// Password-protects the whole site with HTTP Basic Auth.
// Multiple username/password pairs, stored as JSON in the SITE_USERS
// environment variable (set in the Cloudflare dashboard, not in git):
//   {"sonia":"...", "andreas":"...", "guest":"..."}
export async function onRequest(context) {
  const auth = context.request.headers.get("Authorization");
  let users = {};
  try {
    users = JSON.parse(context.env.SITE_USERS || "{}");
  } catch {
    return new Response("Site not configured", { status: 500 });
  }

  if (Object.keys(users).length === 0) {
    return new Response("Site not configured", { status: 500 });
  }

  if (auth) {
    const [scheme, encoded] = auth.split(" ");
    if (scheme === "Basic" && encoded) {
      const decoded = atob(encoded);
      const idx = decoded.indexOf(":");
      const user = decoded.slice(0, idx);
      const pass = decoded.slice(idx + 1);
      if (users[user] && users[user] === pass) {
        return context.next();
      }
    }
  }

  return new Response("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Jaxie\'s Art"' },
  });
}
