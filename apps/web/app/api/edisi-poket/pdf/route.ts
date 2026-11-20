import { pocketDownload } from "@/src/server/poket-books";
import { activeReader } from "@/src/server/reader-session";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  if (!(await activeReader())) {
    return new Response(null, { status: 303, headers: { location: "/pustaka", "cache-control": "no-store" } });
  }
  return pocketDownload("edisi-poket");
}
