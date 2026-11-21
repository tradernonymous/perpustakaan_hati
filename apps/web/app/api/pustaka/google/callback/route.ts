import { TIPS_PATH, tipsPage } from "@/src/tips";
import { cookies } from "next/headers";
import { GOOGLE_READER_COOKIE, googleReaderConfig, googleReaderEmail } from "@/src/server/google-reader";
import { startReaderSession } from "@/src/server/reader-session";

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const jar = await cookies();
  const [state, verifier, pageValue] = jar.get(GOOGLE_READER_COOKIE)?.value.split(".") ?? [];
  jar.delete(GOOGLE_READER_COOKIE);
  const code = params.get("code");
  const config = googleReaderConfig();
  const email = config && code && state && verifier && state === params.get("state")
    ? await googleReaderEmail(config, code, verifier).catch(() => null)
    : null;
  if (email) await startReaderSession(email);
  const page = tipsPage(pageValue);
  const returnQuery = page ? `&halaman=${page}` : "";
  return new Response(null, {
    status: 303,
    headers: { location: email ? (page ? `${TIPS_PATH}?halaman=${page}` : "/pustaka") : `/pustaka?google=fallback${returnQuery}`, "cache-control": "no-store" },
  });
}
