import { createHmac, timingSafeEqual } from "node:crypto";

export type TokenPayload = { k: string; [key: string]: unknown };

const mac = (body: string, secret: string) => createHmac("sha256", secret).update(body).digest("base64url");

/** Signed, expiring token: base64url(json).hmac. `now` and `ttl` are in seconds. */
export function signToken(payload: TokenPayload, secret: string, ttlSeconds: number, now = Math.floor(Date.now() / 1000)): string {
  const body = Buffer.from(JSON.stringify({ ...payload, exp: now + ttlSeconds })).toString("base64url");
  return `${body}.${mac(body, secret)}`;
}

export function verifyToken(token: string, secret: string, now = Math.floor(Date.now() / 1000)): (TokenPayload & { exp: number }) | null {
  if (!secret) return null;
  const [body, sig, extra] = token.split(".");
  if (!body || !sig || extra !== undefined) return null;
  const expected = Buffer.from(mac(body, secret));
  const given = Buffer.from(sig);
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) return null;
  try {
    const p = JSON.parse(Buffer.from(body, "base64url").toString("utf8")) as TokenPayload & { exp: number };
    return typeof p.exp === "number" && p.exp >= now ? p : null;
  } catch {
    return null;
  }
}
