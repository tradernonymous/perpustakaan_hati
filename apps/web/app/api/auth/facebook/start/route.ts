import { randomBytes } from "node:crypto";
import { authorizeUrl, facebookConfig, stateCookie } from "@/src/server/facebook";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/auth/facebook/start
 * Sends the browser to Facebook with a state nonce bound to this browser by an
 * HttpOnly cookie. Fails closed when the app or the allowlist is missing.
 */
export function GET() {
  const config = facebookConfig();
  if (!config) {
    return new Response("Facebook login is not configured. Set FACEBOOK_APP_ID and FACEBOOK_APP_SECRET.", {
      status: 503,
      headers: { "Cache-Control": "no-store", "Content-Type": "text/plain; charset=utf-8" },
    });
  }
  if (config.allowedIds.length === 0) {
    return new Response("No admin account is allowed yet. Set ADMIN_FACEBOOK_IDS to the numeric Facebook id.", {
      status: 503,
      headers: { "Cache-Control": "no-store", "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  const state = randomBytes(32).toString("base64url");
  return new Response(null, {
    status: 302,
    headers: {
      Location: authorizeUrl(config, state),
      "Set-Cookie": stateCookie(state, config),
      "Cache-Control": "no-store",
    },
  });
}