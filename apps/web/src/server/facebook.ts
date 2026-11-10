/** Facebook Login (admin only). Server-side: the app secret never leaves here. */
import type { Env } from "../env";
import { readCookie, secureCookie } from "./threads";

export type FacebookConfig = {
  appId: string;
  appSecret: string;
  redirectUri: string;
  /** Numeric Facebook user ids allowed to become admin. Empty means nobody. */
  allowedIds: string[];
};

const AUTHORIZE_URL = "https://www.facebook.com/dialog/oauth";
// Unversioned endpoints resolve to the oldest supported Graph version, so this
// does not break when a versioned path retires.
const GRAPH_URL = "https://graph.facebook.com";
const STATE_COOKIE = "ph_fb_state";
const STATE_TTL_SECONDS = 600;
const SCOPE = "public_profile";

export class FacebookError extends Error {}

/** Null when the app is not configured, so every caller fails closed. */
export function facebookConfig(env: Env = process.env): FacebookConfig | null {
  const appId = env.FACEBOOK_APP_ID?.trim();
  const appSecret = env.FACEBOOK_APP_SECRET?.trim();
  if (!appId || !appSecret) return null;
  const base = (env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
  return {
    appId,
    appSecret,
    redirectUri: env.FACEBOOK_REDIRECT_URI?.trim() || `${base}/api/auth/facebook/callback`,
    allowedIds: (env.ADMIN_FACEBOOK_IDS ?? "")
      .split(",")
      .map((id) => id.trim())
      .filter(Boolean),
  };
}

export function authorizeUrl(config: FacebookConfig, state: string): string {
  const params = new URLSearchParams({
    client_id: config.appId,
    redirect_uri: config.redirectUri,
    state,
    scope: SCOPE,
    response_type: "code",
  });
  return `${AUTHORIZE_URL}?${params.toString()}`;
}

export function isAllowed(config: FacebookConfig, id: string): boolean {
  return config.allowedIds.includes(id);
}

type FetchLike = typeof fetch;

async function json(res: Response, op: string): Promise<Record<string, unknown>> {
  let payload: unknown;
  try {
    payload = await res.json();
  } catch {
    throw new FacebookError(`${op} failed: Facebook returned an invalid response.`);
  }
  if (!res.ok || !payload || typeof payload !== "object" || "error" in payload) {
    throw new FacebookError(`${op} failed (HTTP ${res.status}). Check the app settings and retry.`);
  }
  return payload as Record<string, unknown>;
}

/** Authorization code -> user access token. */
export async function exchangeCode(
  config: FacebookConfig,
  code: string,
  fetchImpl: FetchLike = fetch,
): Promise<string> {
  const params = new URLSearchParams({
    client_id: config.appId,
    client_secret: config.appSecret,
    redirect_uri: config.redirectUri,
    code,
  });
  const payload = await json(await fetchImpl(`${GRAPH_URL}/oauth/access_token?${params.toString()}`), "Facebook code exchange");
  const token = payload.access_token;
  if (typeof token !== "string" || !token) throw new FacebookError("Facebook code exchange failed: no access token.");
  return token;
}

/** The signed-in account's id and name. */
export async function profile(accessToken: string, fetchImpl: FetchLike = fetch): Promise<{ id: string; name: string }> {
  const params = new URLSearchParams({ fields: "id,name", access_token: accessToken });
  const payload = await json(await fetchImpl(`${GRAPH_URL}/me?${params.toString()}`), "Facebook profile lookup");
  if (typeof payload.id !== "string" || !payload.id) {
    throw new FacebookError("Facebook profile lookup failed: no id in the response.");
  }
  return { id: payload.id, name: typeof payload.name === "string" ? payload.name : "" };
}

export const FACEBOOK_STATE_COOKIE = STATE_COOKIE;
export const FACEBOOK_STATE_MAX_AGE = STATE_TTL_SECONDS;

export function stateCookie(state: string, config: FacebookConfig): string {
  const secure = secureCookie(config.redirectUri) ? "; Secure" : "";
  return `${STATE_COOKIE}=${state}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${STATE_TTL_SECONDS}${secure}`;
}

export function clearedStateCookie(config: FacebookConfig): string {
  const secure = secureCookie(config.redirectUri) ? "; Secure" : "";
  return `${STATE_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure}`;
}

export { readCookie, secureCookie };