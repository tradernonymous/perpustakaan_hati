import { createHash, randomBytes } from "node:crypto";
import { siteUrl } from "../site";

export const GOOGLE_READER_COOKIE = "ph_google_reader";

export function googleReaderConfig() {
  const clientId = process.env.GOOGLE_READER_CLIENT_ID;
  const secret = process.env.GOOGLE_READER_CLIENT_SECRET;
  if (!clientId || !secret || !process.env.DOWNLOAD_SECRET) return null;
  return { clientId, secret, callback: `${siteUrl()}/api/pustaka/google/callback` };
}

export function googleAuthorization(config: NonNullable<ReturnType<typeof googleReaderConfig>>) {
  const state = randomBytes(32).toString("base64url");
  const verifier = randomBytes(48).toString("base64url");
  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.callback,
    response_type: "code",
    scope: "openid email",
    state,
    code_challenge: createHash("sha256").update(verifier).digest("base64url"),
    code_challenge_method: "S256",
  });
  return { url: `https://accounts.google.com/o/oauth2/v2/auth?${params}`, state, verifier };
}

export async function googleReaderEmail(
  config: NonNullable<ReturnType<typeof googleReaderConfig>>,
  code: string,
  verifier: string,
): Promise<string | null> {
  const token = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    body: new URLSearchParams({
      client_id: config.clientId, client_secret: config.secret, redirect_uri: config.callback,
      grant_type: "authorization_code", code, code_verifier: verifier,
    }),
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
  if (!token.ok) return null;
  const credentials = await token.json() as { access_token?: unknown };
  if (typeof credentials.access_token !== "string") return null;
  const response = await fetch("https://openidconnect.googleapis.com/v1/userinfo", {
    headers: { authorization: `Bearer ${credentials.access_token}` },
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) return null;
  const account = await response.json() as { sub?: unknown; email?: unknown; email_verified?: unknown };
  if (typeof account.sub !== "string" || !account.sub || account.email_verified !== true || typeof account.email !== "string") return null;
  const email = account.email.toLowerCase();
  // Verify other email domains through the application's email link before granting purchases.
  return /^[a-z0-9.+]+@gmail\.com$/.test(email) ? email : null;
}
