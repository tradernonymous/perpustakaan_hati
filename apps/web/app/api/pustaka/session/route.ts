import { TIPS_PATH, tipsPage } from "@/src/tips";
import { cookies } from "next/headers";
import { READER_COOKIE, readerClaim, startReaderSession } from "@/src/server/reader-session";

export async function GET(request: Request) {
  const token = new URL(request.url).searchParams.get("t") ?? undefined;
  const claim = readerClaim(token, "lib");
  if (claim) await startReaderSession(claim.email);
  const page = tipsPage(claim?.page);
  return new Response(null, {
    status: 303,
    headers: { location: claim ? (page ? `${TIPS_PATH}?halaman=${page}` : "/pustaka") : "/pustaka?expired=1", "cache-control": "no-store", "referrer-policy": "no-referrer" },
  });
}

export async function POST() {
  const jar = await cookies();
  jar.delete(READER_COOKIE);
  return new Response(null, { status: 303, headers: { location: "/pustaka" } });
}
