import { isAdmin } from "@/src/server/auth";
import { getThreadsStore } from "@/src/server/instance";
import { refreshLongLived, ThreadsError } from "@/src/server/threads";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** POST /api/auth/threads/refresh: extends the 60-day token. Refreshing sooner than 24h after issue fails at Meta. */
export async function POST(req: Request) {
  if (!isAdmin(req, process.env.ADMIN_TOKEN)) {
    return Response.json({ error: "Unauthorized" }, { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Perpustakaan Hati admin", charset="UTF-8"', "Cache-Control": "no-store" } });
  }

  const store = getThreadsStore();
  const token = store.get();
  if (!token) return Response.json({ error: "Threads is not connected." }, { status: 404, headers: { "Cache-Control": "no-store" } });
  if (token.expiresAt <= Date.now()) {
    return Response.json({ error: "Token expired. Reconnect through /api/auth/threads/start." }, { status: 400, headers: { "Cache-Control": "no-store" } });
  }

  try {
    const next = await refreshLongLived(token.accessToken);
    store.save({ ...token, accessToken: next.accessToken, expiresAt: Date.now() + next.expiresIn * 1000 });
    return Response.json(
      { refreshed: true, expiresAt: new Date(Date.now() + next.expiresIn * 1000).toISOString() },
      { headers: { "Cache-Control": "no-store" } },
    );
  } catch (e) {
    const detail = e instanceof ThreadsError ? e.message : "Unexpected error.";
    return Response.json({ error: detail }, { status: 502, headers: { "Cache-Control": "no-store" } });
  }
}
