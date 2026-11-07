import { createHash, timingSafeEqual } from "node:crypto";

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
