import { isAdmin } from "@/src/server/auth";
import { toCsv } from "@/src/server/csv";
import { getStore } from "@/src/server/instance";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** GET /admin/subscribers: CSV of every sign-up. Browser asks for a password; use ADMIN_TOKEN. */
export function GET(req: Request) {
  if (!isAdmin(req, process.env.ADMIN_TOKEN)) {
    return new Response("Unauthorized", {
      status: 401,
      headers: { "WWW-Authenticate": 'Basic realm="Perpustakaan Hati admin", charset="UTF-8"', "Cache-Control": "no-store" },
    });
  }
  const rows = getStore().list().map((r) => [r.id, r.email, r.phone, r.created_at]);
  return new Response(toCsv(["id", "email", "phone", "created_at"], rows), {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="subscribers.csv"',
      "Cache-Control": "no-store",
    },
  });
}
