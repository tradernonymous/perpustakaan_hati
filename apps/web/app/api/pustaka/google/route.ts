import { tipsPage } from "@/src/tips";
import { cookies } from "next/headers";
import { GOOGLE_READER_COOKIE, googleAuthorization, googleReaderConfig } from "@/src/server/google-reader";

export async function GET(request: Request) {
  const config = googleReaderConfig();
  if (!config) return new Response(null, { status: 303, headers: { location: "/pustaka?google=unavailable" } });
  const page = tipsPage(new URL(request.url).searchParams.get("halaman"));
  const { url, state, verifier } = googleAuthorization(config);
  (await cookies()).set(GOOGLE_READER_COOKIE, `${state}.${verifier}.${page ?? ""}`, {
    httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: 600,
  });
  return new Response(null, { status: 303, headers: { location: url, "cache-control": "no-store" } });
}
