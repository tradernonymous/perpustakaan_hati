import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { authorizeUrl, exchangeCode, readCookie, refreshLongLived, stateCookie, threadsConfig, ThreadsError } from "@/src/server/threads";
import { openThreadsStore, type ThreadsStore } from "@/src/server/threads-store";
import { GET as start } from "@/app/api/auth/threads/start/route";

const env = { SITE_URL: "https://perpustakaanhati.test", THREADS_APP_ID: "123456", THREADS_APP_SECRET: "s3cret-value" };

type Call = { url: string; init?: RequestInit };
const fakeFetch = (responses: unknown[], calls: Call[]) =>
  (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), init });
    return Response.json(responses.shift() ?? {});
  }) as typeof fetch;

describe("threadsConfig", () => {
  it("returns null when the app id or secret is missing", () => {
    expect(threadsConfig({})).toBeNull();
    expect(threadsConfig({ THREADS_APP_ID: "1" })).toBeNull();
    expect(threadsConfig({ THREADS_APP_SECRET: "x" })).toBeNull();
  });

  it("derives the callback from SITE_URL and defaults to threads_basic", () => {
    expect(threadsConfig(env)).toEqual({
      clientId: "123456",
      clientSecret: "s3cret-value",
      redirectUri: "https://perpustakaanhati.test/api/auth/threads/callback",
      scopes: "threads_basic",
    });
  });

  it("honours an explicit redirect and scope list", () => {
    const config = threadsConfig({ ...env, THREADS_REDIRECT_URI: "https://x.test/cb", THREADS_SCOPES: "threads_basic,threads_content_publish" });
    expect(config?.redirectUri).toBe("https://x.test/cb");
    expect(config?.scopes).toBe("threads_basic,threads_content_publish");
  });
});

describe("authorizeUrl", () => {
  it("builds the Threads authorization window with every required parameter", () => {
    const url = new URL(authorizeUrl(threadsConfig(env)!, "state-123"));
    expect(`${url.origin}${url.pathname}`).toBe("https://threads.com/oauth/authorize");
    expect(url.searchParams.get("client_id")).toBe("123456");
    expect(url.searchParams.get("redirect_uri")).toBe("https://perpustakaanhati.test/api/auth/threads/callback");
    expect(url.searchParams.get("scope")).toBe("threads_basic");
    expect(url.searchParams.get("response_type")).toBe("code");
    expect(url.searchParams.get("state")).toBe("state-123");
  });
});

describe("exchangeCode", () => {
  it("exchanges the code and upgrades to a long-lived token", async () => {
    const calls: Call[] = [];
    const fetchImpl = fakeFetch([
      { access_token: "short-token", token_type: "bearer", user_id: 1 },
      { access_token: "long-token", token_type: "bearer", expires_in: 5_183_944 },
    ], calls);

    const result = await exchangeCode(threadsConfig(env)!, "auth-code", fetchImpl);
    expect(result).toEqual({ accessToken: "long-token", expiresIn: 5_183_944 });
    expect(calls[0].url).toBe("https://graph.threads.com/oauth/access_token");
    expect(calls[0].init?.method).toBe("POST");
    const body = new URLSearchParams(String(calls[0].init?.body));
    expect(body.get("grant_type")).toBe("authorization_code");
    expect(body.get("code")).toBe("auth-code");
    expect(calls[1].url).toContain("grant_type=th_exchange_token");
    expect(calls[1].url).toContain("access_token=short-token");
  });

  it("fails closed without leaking the app secret", async () => {
    const calls: Call[] = [];
    const fetchImpl = fakeFetch([{ error: { message: "bad code", code: 400 } }], calls);
    const error = await exchangeCode(threadsConfig(env)!, "bad", fetchImpl).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ThreadsError);
    expect(String(error)).not.toContain("s3cret-value");
  });

  it("rejects a token payload without a positive lifetime", async () => {
    const calls: Call[] = [];
    const fetchImpl = fakeFetch([{ access_token: "short" }, { access_token: "long", expires_in: 0 }], calls);
    await expect(exchangeCode(threadsConfig(env)!, "code", fetchImpl)).rejects.toBeInstanceOf(ThreadsError);
  });
});

describe("refreshLongLived", () => {
  it("uses the refresh grant and returns the new lifetime", async () => {
    const calls: Call[] = [];
    const fetchImpl = fakeFetch([{ access_token: "fresh", expires_in: 5_183_944 }], calls);
    await expect(refreshLongLived("old", fetchImpl)).resolves.toEqual({ accessToken: "fresh", expiresIn: 5_183_944 });
    expect(calls[0].url).toContain("https://graph.threads.com/refresh_access_token?");
    expect(calls[0].url).toContain("grant_type=th_refresh_token");
  });
});

describe("cookies", () => {
  it("reads a named cookie and ignores the rest", () => {
    expect(readCookie("a=1; ph_threads_state=abc123; b=2", "ph_threads_state")).toBe("abc123");
    expect(readCookie("a=1", "ph_threads_state")).toBeNull();
    expect(readCookie(null, "ph_threads_state")).toBeNull();
  });

  it("marks the state cookie HttpOnly, Lax, and Secure on https", () => {
    const cookie = stateCookie("abc", threadsConfig(env)!);
    expect(cookie).toContain("ph_threads_state=abc");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Secure");
    expect(stateCookie("abc", threadsConfig({ ...env, SITE_URL: "http://localhost:3000" })!)).not.toContain("Secure");
  });
});

describe("threads store", () => {
  let dir: string;
  let store: ThreadsStore;
  beforeEach(() => {
    dir = mkdtempSync(path.join(tmpdir(), "ph-threads-"));
    store = openThreadsStore(path.join(dir, "threads.db"));
  });
  afterEach(() => {
    store.close();
    rmSync(dir, { recursive: true, force: true });
  });

  it("saves one connection and overwrites it on reconnect", () => {
    expect(store.get()).toBeNull();
    store.save({ accessToken: "a", userId: "1", username: "rahimam", scopes: "threads_basic", expiresAt: 1 });
    store.save({ accessToken: "b", userId: "1", username: "rahimam", scopes: "threads_basic,threads_content_publish", expiresAt: 2 });
    expect(store.get()).toEqual({ accessToken: "b", userId: "1", username: "rahimam", scopes: "threads_basic,threads_content_publish", expiresAt: 2 });
    store.clear();
    expect(store.get()).toBeNull();
  });
});

describe("GET /api/auth/threads/start", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("refuses without the admin token", () => {
    vi.stubEnv("ADMIN_TOKEN", "admin-token");
    const res = start(new Request("https://x.test/api/auth/threads/start"));
    expect(res.status).toBe(401);
    expect(res.headers.get("www-authenticate")).toContain("Basic");
  });

  it("fails closed when the Threads app is not configured", () => {
    vi.stubEnv("ADMIN_TOKEN", "admin-token");
    vi.stubEnv("THREADS_APP_ID", "");
    vi.stubEnv("THREADS_APP_SECRET", "");
    const res = start(new Request("https://x.test/api/auth/threads/start", { headers: { authorization: "Bearer admin-token" } }));
    expect(res.status).toBe(503);
  });

  it("redirects to Threads with a state cookie", () => {
    vi.stubEnv("ADMIN_TOKEN", "admin-token");
    vi.stubEnv("THREADS_APP_ID", "123456");
    vi.stubEnv("THREADS_APP_SECRET", "s3cret-value");
    vi.stubEnv("SITE_URL", "https://perpustakaanhati.test");
    const res = start(new Request("https://x.test/api/auth/threads/start", { headers: { authorization: "Bearer admin-token" } }));
    expect(res.status).toBe(302);
    expect(res.headers.get("location")).toContain("https://threads.com/oauth/authorize?");
    expect(res.headers.get("set-cookie")).toContain("ph_threads_state=");
  });
});
