import { cookies } from "next/headers";
import { signToken, verifyToken } from "./tokens";

export const READER_COOKIE = "ph_reader";
const SESSION_SECONDS = 7 * 24 * 60 * 60;

export function readerClaim(token: string | undefined, kind: "lib" | "reader") {
  const secret = process.env.DOWNLOAD_SECRET;
  if (!secret || !token || token.length > 2048) return null;
  const payload = verifyToken(token, secret);
  return payload?.k === kind && typeof payload.e === "string" ? { email: payload.e, page: payload.p } : null;
}

export async function activeReader(): Promise<string | null> {
  const jar = await cookies();
  return readerClaim(jar.get(READER_COOKIE)?.value, "reader")?.email ?? null;
}

export async function startReaderSession(email: string): Promise<void> {
  const secret = process.env.DOWNLOAD_SECRET;
  if (!secret) throw new Error("Reader sessions are unavailable");
  const jar = await cookies();
  jar.set(READER_COOKIE, signToken({ k: "reader", e: email }, secret, SESSION_SECONDS), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_SECONDS,
  });
}
