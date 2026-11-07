import { describe, expect, it } from "vitest";
import { isAdmin } from "@/src/server/auth";

const basic = (pw: string) => "Basic " + Buffer.from(`admin:${pw}`).toString("base64");

describe("isAdmin", () => {
  it("rejects everything when no token is configured", () => {
    expect(isAdmin(new Request("http://x", { headers: { authorization: "Bearer " } }), undefined)).toBe(false);
    expect(isAdmin(new Request("http://x", { headers: { authorization: basic("") } }), "")).toBe(false);
  });
  it("accepts a matching Bearer token", () => {
    const r = new Request("http://x", { headers: { authorization: "Bearer s3cret-token-value" } });
    expect(isAdmin(r, "s3cret-token-value")).toBe(true);
  });
  it("accepts a matching Basic password with any user name", () => {
    const r = new Request("http://x", { headers: { authorization: basic("s3cret-token-value") } });
    expect(isAdmin(r, "s3cret-token-value")).toBe(true);
  });
  it("rejects a wrong or missing credential", () => {
    expect(isAdmin(new Request("http://x"), "s3cret-token-value")).toBe(false);
    expect(isAdmin(new Request("http://x", { headers: { authorization: "Bearer nope" } }), "s3cret-token-value")).toBe(false);
    expect(isAdmin(new Request("http://x", { headers: { authorization: basic("nope") } }), "s3cret-token-value")).toBe(false);
  });
  it("never accepts the token from the URL", () => {
    expect(isAdmin(new Request("http://x?key=s3cret-token-value"), "s3cret-token-value")).toBe(false);
  });
});
