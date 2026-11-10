import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { isAdminSession, issueAdminSession } from "@/src/server/auth";
import {
  authorizeUrl,
  exchangeCode,
  facebookConfig,
  isAllowed,
  profile,
  FacebookError,
} from "@/src/server/facebook";
import { GET as start } from "@/app/api/auth/facebook/start/route";
import { GET as callback } from "@/app/api/auth/facebook/callback/route";

const env = {
  FACEBOOK_APP_ID: "app-123",
  FACEBOOK_APP_SECRET: "secret-xyz",
  ADMIN_FACEBOOK_IDS: " 10001 , 10002 ",
  SITE_URL: "https://web.example.test",
  ADMIN_TOKEN: "admin-token-value",
};

function withEnv(overrides: Record<string, string | undefined> = {}) {
  for (const [k, v] of Object.entries({ ...env, ...overrides })) {
    if (v === undefined) delete process.env[k];
    else process.env[k] = v;
  }
}

beforeEach(() => withEnv());
afterEach(() => {
  for (const k of Object.keys(env)) delete process.env[k];
  vi.unstubAllGlobals();
});

describe("facebookConfig", () => {
  it("fails closed without credentials", () => {
    withEnv({ FACEBOOK_APP_ID: undefined, FACEBOOK_APP_SECRET: undefined });
    expect(facebookConfig()).toBeNull();
  });

  it("derives the redirect URI from SITE_URL and parses the allowlist", () => {
    const config = facebookConfig()!;
    expect(config.redirectUri).toBe("https://web.example.test/api/auth/facebook/callback");
    expect(config.allowedIds).toEqual(["10001", "10002"]);
  });

  it("treats an empty allowlist as nobody allowed", () => {
    withEnv({ ADMIN_FACEBOOK_IDS: "" });
    const config = facebookConfig()!;
    expect(config.allowedIds).toEqual([]);
    expect(isAllowed(config, "10001")).toBe(false);
  });
});

describe("authorizeUrl", () => {
  it("carries the app id, redirect, state and profile scope", () => {
    const url = new URL(authorizeUrl(facebookConfig()!, "state-abc"));
    expect(url.origin + url.pathname).toBe("https://www.facebook.com/dialog/oauth");
    expect(url.searchParams.get("client_id")).toBe("app-123");
    expect(url.searchParams.get("redirect_uri")).toBe("https://web.example.test/api/auth/facebook/callback");
    expect(url.searchParams.get("state")).toBe("state-abc");
    expect(url.searchParams.get("scope")).toBe("public_profile");
  });
});

describe("graph calls", () => {
  it("exchanges a code for a token", async () => {
    const fetchMock = vi.fn(async (url: RequestInfo | URL) => new Response(JSON.stringify({ access_token: "tok-1" }), { status: 200 }));
    await expect(exchangeCode(facebookConfig()!, "code-1", fetchMock)).resolves.toBe("tok-1");
    const called = String(fetchMock.mock.calls[0]![0]);
    expect(called).toContain("/oauth/access_token");
    expect(called).toContain("code=code-1");
    expect(called).toContain("client_secret=secret-xyz");
  });

  it("turns an error payload into a FacebookError", async () => {
    const fetchMock = vi.fn(async (_url: RequestInfo | URL) => new Response(JSON.stringify({ error: { message: "bad" } }), { status: 400 }));
    await expect(exchangeCode(facebookConfig()!, "code-1", fetchMock)).rejects.toBeInstanceOf(FacebookError);
  });

  it("reads the id and name", async () => {
    const fetchMock = vi.fn(async (_url: RequestInfo | URL) => new Response(JSON.stringify({ id: "10001", name: "Jack" }), { status: 200 }));
    await expect(profile("tok-1", fetchMock)).resolves.toEqual({ id: "10001", name: "Jack" });
  });

  it("rejects a profile without an id", async () => {
    const fetchMock = vi.fn(async (_url: RequestInfo | URL) => new Response(JSON.stringify({ name: "Nobody" }), { status: 200 }));
    await expect(profile("tok-1", fetchMock)).rejects.toBeInstanceOf(FacebookError);
  });
});

describe("start route", () => {
  it("returns 503 without credentials", async () => {
    withEnv({ FACEBOOK_APP_ID: undefined });
    const res = start();
    expect(res.status).toBe(503);
  });

  it("returns 503 when the allowlist is empty", async () => {
    withEnv({ ADMIN_FACEBOOK_IDS: "" });
    expect(start().status).toBe(503);
  });

  it("redirects to Facebook and binds the state to a cookie", () => {
    const res = start();
    expect(res.status).toBe(302);
    const location = new URL(res.headers.get("location")!);
    const cookie = res.headers.get("set-cookie")!;
    expect(location.searchParams.get("state")).toBeTruthy();
    expect(cookie).toContain(`ph_fb_state=${location.searchParams.get("state")}`);
    expect(cookie).toContain("HttpOnly");
  });
});

describe("callback route", () => {
  const call = (query: string, cookie?: string) =>
    callback(new Request(`https://web.example.test/api/auth/facebook/callback${query}`, { headers: cookie ? { cookie } : {} }));

  it("rejects a state that does not match the cookie", async () => {
    const res = await call("?code=c&state=one", "ph_fb_state=two");
    expect(res.status).toBe(400);
  });

  it("rejects a state with no cookie at all", async () => {
    expect((await call("?code=c&state=one")).status).toBe(400);
  });

  it("refuses an account outside the allowlist", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("oauth/access_token")) return new Response(JSON.stringify({ access_token: "tok" }), { status: 200 });
      return new Response(JSON.stringify({ id: "99999", name: "Stranger" }), { status: 200 });
    }));
    const res = await call("?code=c&state=same", "ph_fb_state=same");
    expect(res.status).toBe(403);
    expect(res.headers.get("set-cookie")).not.toContain("ph_admin_session");
  });

  it("opens a session for an allowlisted account", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("oauth/access_token")) return new Response(JSON.stringify({ access_token: "tok" }), { status: 200 });
      return new Response(JSON.stringify({ id: "10001", name: "Jack" }), { status: 200 });
    }));
    const res = await call("?code=c&state=same", "ph_fb_state=same");
    expect(res.status).toBe(303);
    expect(res.headers.get("location")).toBe("/admin");
    const cookie = res.headers.get("set-cookie")!;
    expect(cookie).toContain("ph_admin_session=");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("Secure");
  });

  it("surfaces a cancelled consent", async () => {
    expect((await call("?error=access_denied", "ph_fb_state=same")).status).toBe(400);
  });
});

describe("admin session cookie", () => {
  const req = (cookie: string) => new Request("https://x.test/admin", { headers: { cookie } });

  it("accepts a freshly issued session", () => {
    const header = issueAdminSession("admin-token-value", { secure: true });
    expect(isAdminSession(req(header.split(";")[0]), "admin-token-value")).toBe(true);
  });

  it("rejects a session signed with another token", () => {
    const header = issueAdminSession("other-token", { secure: true });
    expect(isAdminSession(req(header.split(";")[0]), "admin-token-value")).toBe(false);
  });

  it("rejects an expired session", () => {
    const past = String(Date.now() - 1000);
    const sig = require("node:crypto").createHmac("sha256", "admin-token-value").update(past).digest("base64url");
    expect(isAdminSession(req(`ph_admin_session=${past}.${sig}`), "admin-token-value")).toBe(false);
  });

  it("rejects everything when no token is configured", () => {
    const header = issueAdminSession("x", { secure: true });
    expect(isAdminSession(req(header.split(";")[0]), undefined)).toBe(false);
  });
});