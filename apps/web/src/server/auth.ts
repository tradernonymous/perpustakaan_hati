import { createHash, createHmac, timingSafeEqual } from "node:crypto";

// Hash both sides first so timingSafeEqual always compares equal-length buffers.
function safeEqual(a: string, b: string): boolean {
  const ha = createHash("sha256").update(a).digest();
  const hb = createHash("sha256").update(b).digest();
  return timingSafeEqual(ha, hb);
}

/**
 * Admin check for server-only routes. Accepts `Authorization: Bearer <token>`
 * or HTTP Basic with the token as the password (any user name), so a browser
 * can open the CSV export with its built-in login box. The token is never read
 * from the URL, so it cannot leak into logs or browser history.
 */
export function isAdmin(req: Request, token: string | undefined): boolean {
  if (!token) return false;
  const header = req.headers.get("authorization") ?? "";
  if (header.startsWith("Bearer ")) return safeEqual(header.slice(7), token);
  if (header.startsWith("Basic ")) {
    const decoded = Buffer.from(header.slice(6), "base64").toString("utf8");
    const i = decoded.indexOf(":");
    return i >= 0 && safeEqual(decoded.slice(i + 1), token);
  }
  return false;
}

/* ------------------------------------------------------------------ */
/* Facebook sign-in sessions                                            */
/* ------------------------------------------------------------------ */

export const ADMIN_SESSION_COOKIE = "ph_admin_session";
const SESSION_TTL_SECONDS = 60 * 60 * 8;

function readCookie(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    if (part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return null;
}

/**
 * Stateless session: `<expiresAt>.<hmac>`, signed with ADMIN_TOKEN. No session
 * store to run on Railway, and rotating ADMIN_TOKEN signs everyone out.
 */
export function issueAdminSession(token: string, opts: { secure: boolean }): string {
  const expires = Date.now() + SESSION_TTL_SECONDS * 1000;
  const sig = createHmac("sha256", token).update(String(expires)).digest("base64url");
  return `${ADMIN_SESSION_COOKIE}=${expires}.${sig}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${SESSION_TTL_SECONDS}${opts.secure ? "; Secure" : ""}`;
}

export function clearAdminSession(opts: { secure: boolean }): string {
  return `${ADMIN_SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${opts.secure ? "; Secure" : ""}`;
}

/** True only for a present, unexpired, correctly signed session cookie. */
export function isAdminSession(req: Request, token: string | undefined): boolean {
  if (!token) return false;
  const raw = readCookie(req.headers.get("cookie"), ADMIN_SESSION_COOKIE);
  if (!raw) return false;
  const dot = raw.indexOf(".");
  if (dot <= 0) return false;
  const expires = raw.slice(0, dot);
  const sig = raw.slice(dot + 1);
  const expiresAt = Number(expires);
  if (!Number.isFinite(expiresAt) || expiresAt < Date.now()) return false;
  const expected = createHmac("sha256", token).update(expires).digest("base64url");
  return safeEqual(sig, expected);
}

/** Either credential opens the admin area: the signed session, or the token. */
export function isAdminRequest(req: Request, token: string | undefined): boolean {
  return isAdminSession(req, token) || isAdmin(req, token);
}