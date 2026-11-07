import { describe, expect, it } from "vitest";
import { CSP, SECURITY_HEADERS } from "@/src/server/security";

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
});
