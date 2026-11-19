import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import Home from "@/app/page";
import { ClosingCta } from "@/components/ClosingCta";

const html = renderToStaticMarkup(<Home />);
const pos = (id: string) => html.indexOf(`id="${id}"`);

describe("dark home funnel", () => {
  it("renders exactly one h1", () => {
    expect(html.match(/<h1[\s>]/g)?.length).toBe(1);
  });
  it("puts the free opt-in inside the hero, before the how-it-works band", () => {
    expect(pos("atas")).toBeGreaterThan(-1);
    expect(pos("percuma")).toBeGreaterThan(pos("atas"));
    expect(pos("percuma")).toBeLessThan(pos("cara"));
    expect(html.match(/id="percuma"/g)?.length).toBe(1);
    expect(html).toContain('id="optin-email"');
  });
  it("orders the funnel: how it works, features, tiers, chapters, plates, readers, faq", () => {
    const order = ["cara", "interaktif", "edisi", "bab", "plat", "pembaca", "soalan"].map(pos);
    expect(order.every((n) => n > -1)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
  });
  it("ends with a closing call to action that points back to the opt-in", () => {
    const out = renderToStaticMarkup(<ClosingCta />);
    expect(out).toContain('href="#percuma"');
    expect(out).toMatch(/<h2/);
    expect(html.lastIndexOf('id="penutup"')).toBeGreaterThan(pos("soalan"));
  });
  it("keeps one primary call to action in the hero", () => {
    const hero = html.slice(pos("atas"), html.indexOf("</section>", pos("atas")));
    expect(hero.match(/class="[^"]*ph-cta[^"]*"/g)?.length ?? 0).toBeLessThanOrEqual(1);
  });
  it("uses no ivory-only classes", () => {
    expect(html).not.toMatch(/bg-daylight|text-green-900|text-ink-grove/);
  });
});
