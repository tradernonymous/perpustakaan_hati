import { describe, expect, it } from "vitest";
import { NextRequest } from "next/server";
import { buildCsp, CSP, SECURITY_HEADERS } from "@/src/server/security";
import { proxy } from "@/proxy";

describe("Content-Security-Policy", () => {
  it("locks down the dangerous defaults", () => {
    expect(CSP).toContain("default-src 'self'");
    expect(CSP).toContain("object-src 'none'");
    expect(CSP).toContain("base-uri 'self'");
    expect(CSP).toContain("frame-ancestors 'none'");
    expect(CSP).toContain("form-action 'self'");
  });
  it("allows no third-party origins", () => {
    expect(CSP).not.toMatch(/https?:\/\//);
    expect(CSP).not.toContain("*");
  });
  it("is shipped as a header together with the other protections", () => {
    const keys = SECURITY_HEADERS.map((h) => h.key);
    expect(keys).toEqual(expect.arrayContaining([
      "Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy", "Strict-Transport-Security",
    ]));
  });
  it("builds per-request nonce CSP without unsafe-inline in script-src", () => {
    const nonced = buildCsp("testNonce123");
    expect(nonced).toContain("script-src 'self' 'nonce-testNonce123' 'strict-dynamic'");
    expect(nonced).not.toContain("script-src 'self' 'unsafe-inline'");
  });
  it("proxy issues unique nonces and sets Content-Security-Policy per request", () => {
    const res1 = proxy(new NextRequest("http://localhost:3000/"));
    const res2 = proxy(new NextRequest("http://localhost:3000/"));
    const csp1 = res1.headers.get("Content-Security-Policy") ?? "";
    const csp2 = res2.headers.get("Content-Security-Policy") ?? "";
    expect(csp1).toContain("'nonce-");
    expect(csp1).not.toContain("script-src 'self' 'unsafe-inline'");
    expect(csp1).not.toBe(csp2);
  });
});
