import { pocketDownload } from "@/src/server/poket-books";
import { activeReader } from "@/src/server/reader-session";

export const runtime = "nodejs";

export async function GET(_request: Request, { params }: { params: Promise<{ slug: string }> }) {
  if (!(await activeReader())) return new Response(null, { status: 401, headers: { "cache-control": "no-store" } });
  return pocketDownload((await params).slug);
}
