import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { OptInForm } from "@/components/OptInForm";

describe("OptInForm markup", () => {
  const html = renderToStaticMarkup(<OptInForm />);
  it("has a required PDPA consent checkbox", () => {
    const tag = html.match(/<input[^>]*name="consent"[^>]*>/)?.[0] ?? "";
    expect(tag).toContain('type="checkbox"');
    expect(tag).toContain("required");
    expect(html).toContain("PDPA");
  });
  it("labels every field", () => {
    expect(html).toMatch(/<label[^>]*for="optin-email"/);
    expect(html).toMatch(/<label[^>]*for="optin-phone"/);
  });
  it("has a honeypot hidden from people and assistive tech", () => {
    expect(html).toMatch(/name="website"/);
    expect(html).toMatch(/aria-hidden="true"/);
    expect(html).toMatch(/tabindex="-1"/);
  });
  it("announces status changes politely", () => {
    expect(html).toContain('aria-live="polite"');
  });
});
