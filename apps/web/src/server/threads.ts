/** Threads (Meta) OAuth, read-only client. Server-side only: the app secret never leaves here. */
import type { Env } from "../env";

export type ThreadsConfig = {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  scopes: string;
};

const AUTHORIZE_URL = "https://threads.com/oauth/authorize";
const GRAPH_URL = "https://graph.threads.com";
const STATE_COOKIE = "ph_threads_state";
const STATE_TTL_SECONDS = 600;

export class ThreadsError extends Error {}

/**
 * Returns null when the app is not configured, so every caller can fail closed
 * instead of sending a request with empty credentials.
 */
export function threadsConfig(env: Env = process.env): ThreadsConfig | null {
  const clientId = env.THREADS_APP_ID?.trim();
  const clientSecret = env.THREADS_APP_SECRET?.trim();
  if (!clientId || !clientSecret) return null;
  const base = (env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
  return {
    clientId,
    clientSecret,
    redirectUri: env.THREADS_REDIRECT_URI?.trim() || `${base}/api/auth/threads/callback`,
    scopes: env.THREADS_SCOPES?.trim() || "threads_basic",
  };
}

export function authorizeUrl(config: ThreadsConfig, state: string): string {
  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: config.scopes,
    response_type: "code",
    state,
  });
  return `${AUTHORIZE_URL}?${params.toString()}`;
}

type FetchLike = typeof fetch;

async function graphJson(res: Response, op: string): Promise<Record<string, unknown>> {
  let payload: unknown;
  try {
    payload = await res.json();
  } catch {
    throw new ThreadsError(`${op} failed: Threads returned an invalid response.`);
  }
  if (!res.ok || !payload || typeof payload !== "object" || "error" in payload) {
    throw new ThreadsError(`${op} failed (HTTP ${res.status}). Check the app settings and reconnect.`);
  }
  return payload as Record<string, unknown>;
}

function tokenPair(payload: Record<string, unknown>, op: string): { accessToken: string; expiresIn: number } {
  const accessToken = payload.access_token;
  const expiresIn = Number(payload.expires_in);
  if (typeof accessToken !== "string" || !accessToken || !Number.isFinite(expiresIn) || expiresIn <= 0) {
    throw new ThreadsError(`${op} failed: Threads returned an invalid token response.`);
  }
  return { accessToken, expiresIn };
}

/** Code -> short-lived token -> 60-day long-lived token. */
export async function exchangeCode(
  config: ThreadsConfig,
  code: string,
  fetchImpl: FetchLike = fetch,
): Promise<{ accessToken: string; expiresIn: number }> {
  const short = await fetchImpl(`${GRAPH_URL}/oauth/access_token`, {
    method: "POST",
    body: new URLSearchParams({
      client_id: config.clientId,
      client_secret: config.clientSecret,
      redirect_uri: config.redirectUri,
      grant_type: "authorization_code",
      code,
    }),
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  const shortPayload = await graphJson(short, "Threads code exchange");
  const shortToken = shortPayload.access_token;
  if (typeof shortToken !== "string" || !shortToken) {
    throw new ThreadsError("Threads code exchange failed: no access token.");
  }

  const params = new URLSearchParams({
    grant_type: "th_exchange_token",
    client_secret: config.clientSecret,
    access_token: shortToken,
  });
  const long = await fetchImpl(`${GRAPH_URL}/access_token?${params.toString()}`);
  return tokenPair(await graphJson(long, "Threads long-lived token exchange"), "Threads long-lived token exchange");
}

/** Extends a live long-lived token by another 60 days. */
export async function refreshLongLived(
  accessToken: string,
  fetchImpl: FetchLike = fetch,
): Promise<{ accessToken: string; expiresIn: number }> {
  const params = new URLSearchParams({
    grant_type: "th_refresh_token",
    access_token: accessToken,
  });
  const res = await fetchImpl(`${GRAPH_URL}/refresh_access_token?${params.toString()}`);
  return tokenPair(await graphJson(res, "Threads token refresh"), "Threads token refresh");
}

export async function threadsProfile(
  accessToken: string,
  fetchImpl: FetchLike = fetch,
): Promise<{ id: string; username: string }> {
  const res = await fetchImpl(`${GRAPH_URL}/v1.0/me?fields=id,username`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const payload = await graphJson(res, "Threads profile lookup");
  if (typeof payload.id !== "string" || typeof payload.username !== "string") {
    throw new ThreadsError("Threads profile lookup failed: unexpected payload.");
  }
  return { id: payload.id, username: payload.username };
}

export const THREADS_STATE_COOKIE = STATE_COOKIE;
export const THREADS_STATE_MAX_AGE = STATE_TTL_SECONDS;

/** Minimal cookie reader for route handlers; no cookie parsing dependency. */
export function readCookie(header: string | null, name: string): string | null {
  if (!header) return null;
  for (const part of header.split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    if (part.slice(0, i).trim() === name) return decodeURIComponent(part.slice(i + 1).trim());
  }
  return null;
}

export function secureCookie(redirectUri: string): boolean {
  return redirectUri.startsWith("https://");
}

export function stateCookie(state: string, config: ThreadsConfig): string {
  const secure = secureCookie(config.redirectUri) ? "; Secure" : "";
  return `${STATE_COOKIE}=${state}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${STATE_TTL_SECONDS}${secure}`;
}

export function clearedStateCookie(config: ThreadsConfig): string {
  const secure = secureCookie(config.redirectUri) ? "; Secure" : "";
  return `${STATE_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure}`;
}
