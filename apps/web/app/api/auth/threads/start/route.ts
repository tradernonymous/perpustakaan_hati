import { randomBytes } from "node:crypto";
import { isAdmin } from "@/src/server/auth";
import { authorizeUrl, stateCookie, threadsConfig } from "@/src/server/threads";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/auth/threads/start
 * Admin-only. The browser asks for the ADMIN_TOKEN password, then we send the
 * account to the Threads authorization window. The state nonce is bound to
 * this browser by an HttpOnly cookie.
 */
export function GET(req: Request) {
  if (!isAdmin(req, process.env.ADMIN_TOKEN)) {
    return new Response("Unauthorized", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="Perpustakaan Hati admin", charset="UTF-8"',
        "Cache-Control": "no-store",
      },
    });
  }

  const config = threadsConfig();
  if (!config) {
    return new Response("Threads is not configured. Set THREADS_APP_ID and THREADS_APP_SECRET.", {
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
