import { isAdmin } from "@/src/server/auth";
import { getThreadsStore } from "@/src/server/instance";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** GET /api/auth/threads/status: admin-only health of the stored connection. Never returns the token. */
export function GET(req: Request) {
  if (!isAdmin(req, process.env.ADMIN_TOKEN)) {
    return Response.json({ error: "Unauthorized" }, { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Perpustakaan Hati admin", charset="UTF-8"', "Cache-Control": "no-store" } });
  }

  const token = getThreadsStore().get();
  if (!token) return Response.json({ connected: false }, { headers: { "Cache-Control": "no-store" } });

  const msLeft = token.expiresAt - Date.now();
  return Response.json(
    {
      connected: msLeft > 0,
      username: token.username,
      scopes: token.scopes.split(","),
      expiresAt: new Date(token.expiresAt).toISOString(),
      daysLeft: Math.max(0, Math.floor(msLeft / 86_400_000)),
    },
    { headers: { "Cache-Control": "no-store" } },
  );
}
