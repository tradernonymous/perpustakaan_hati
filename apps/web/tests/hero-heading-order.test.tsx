import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { HeroBook } from "@/components/HeroBook";
import Home from "@/app/page";

/*
 * The hero jumped h1 -> h3 -> h2: the book panel title was an h3 with no h2
 * above it. Screen readers announce that as a skipped level. The book page
 * title is not a document section, so it is a paragraph now.
 */
const tokens = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");

describe("hero heading order", () => {
  it("does not skip a level between the hero h1 and the first section h2", () => {
    const html = renderToStaticMarkup(<Home />);
    const levels = [...html.matchAll(/<(h[1-6])[^>]*>/g)].map((m) => Number(m[1][1]));
    expect(levels[0]).toBe(1);
    expect(levels[1]).toBe(2);
  });

  it("renders the book page title as a paragraph", () => {
    const html = renderToStaticMarkup(<HeroBook name="Edisi Poket" />);
    expect(html).not.toContain("<h3");
    expect(html).toContain("Kad Refleksi");
  });

  it("keeps the book title styling on the demoted element", () => {
    expect(tokens).toContain(".ph-book-open .ph-book-page-title {");
    expect(tokens).not.toContain(".ph-book-open h3 {");
  });
});
