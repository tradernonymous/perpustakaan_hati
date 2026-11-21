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
  it("puts the free opt-in after the hero, before the how-it-works band", () => {
    expect(pos("atas")).toBeGreaterThan(-1);
    expect(pos("percuma")).toBeGreaterThan(pos("atas"));
    expect(pos("percuma")).toBeLessThan(pos("cara"));
    expect(html.match(/id="percuma"/g)?.length).toBe(1);
    expect(html).toContain('id="lib-email"');
  });
  it("orders the funnel: sample, comparison, catalog, access, faq", () => {
    const order = ["bab", "edisi", "katalog", "filem", "cara", "soalan"].map(pos);
    expect(order.every((n) => n > -1)).toBe(true);
    expect([...order].sort((a, b) => a - b)).toEqual(order);
  });
  it("keeps interactive resources on the homepage", () => {
    expect(pos("interaktif")).toBeGreaterThan(pos("cara"));
    expect(pos("plat")).toBe(-1);
    expect(pos("pembaca")).toBe(-1);
  });
  it("ends with a closing call to action that points back to the opt-in", () => {
    const out = renderToStaticMarkup(<ClosingCta />);
    expect(out).toContain('href="#percuma"');
    expect(out).toMatch(/<h2/);
    expect(html.lastIndexOf('id="penutup"')).toBeGreaterThan(pos("soalan"));
  });
  it("preserves the primary and secondary compact hero links", () => {
    const hero = html.slice(pos("atas"), pos("percuma"));
    expect(hero).toMatch(/href="#percuma"[^>]*class="ph-cta /);
    expect(hero).toMatch(/href="#edisi"[^>]*class="btn-ghost /);
  });
  it("offers the launch film with controls and alternate formats", () => {
    expect(html).toMatch(/<video[^>]*controls=""[^>]*preload="none"/);
    for (const asset of ["poster.jpg", "editions-16x9.mp4", "editions-4x5.mp4", "editions-9x16.mp4"]) {
      expect(html).toContain(`/launch/${asset}`);
    }
  });
  it("uses no ivory-only classes", () => {
    expect(html).not.toMatch(/bg-daylight|text-green-900|text-ink-grove/);
  });
});
