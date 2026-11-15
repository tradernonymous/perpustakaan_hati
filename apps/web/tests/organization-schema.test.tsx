import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { OrganizationSchema } from "@/components/OrganizationSchema";
import Home from "@/app/page";

/*
 * The homepage only shipped FAQPage JSON-LD. A publisher site needs the
 * Organization (who) and WebSite (what, plus the search action) so search
 * engines can tie the social handles to the brand.
 */
function jsonLd(html: string): Record<string, unknown>[] {
  const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map(
    (m) => JSON.parse(m[1].replace(/\\u003c/g, "<")) as Record<string, unknown>,
  );
  return blocks;
}

describe("organization structured data", () => {
  it("emits Organization and WebSite on the homepage", () => {
    const blocks = jsonLd(renderToStaticMarkup(<OrganizationSchema />));
    const types = blocks.map((b) => b["@type"]);
    expect(types).toContain("Organization");
    expect(types).toContain("WebSite");
  });

  it("names the author and links the confirmed Threads handle", () => {
    const html = renderToStaticMarkup(<OrganizationSchema />);
    expect(html).toContain("https://www.threads.net/@rahimam");
    const org = jsonLd(html).find((b) => b["@type"] === "Organization") as Record<string, unknown>;
    expect(org["name"]).toBe("Perpustakaan Hati");
    expect(org["author"]).toBeDefined();
  });

  it("gives WebSite an absolute url and a publisher link", () => {
    const site = jsonLd(renderToStaticMarkup(<OrganizationSchema />)).find(
      (b) => b["@type"] === "WebSite",
    ) as Record<string, unknown>;
    expect(String(site["url"])).toMatch(/^https?:\/\//);
    expect(site["publisher"]).toBeDefined();
  });

  it("does not claim a search action the site does not serve", () => {
    const site = jsonLd(renderToStaticMarkup(<OrganizationSchema />)).find(
      (b) => b["@type"] === "WebSite",
    ) as Record<string, unknown>;
    expect(site["potentialAction"]).toBeUndefined();
  });

  it("is rendered on the homepage", () => {
    const html = renderToStaticMarkup(<Home />);
    const types = jsonLd(html).map((b) => b["@type"]);
    expect(types).toContain("Organization");
    expect(types).toContain("WebSite");
    expect(types).toContain("FAQPage");
  });
});
