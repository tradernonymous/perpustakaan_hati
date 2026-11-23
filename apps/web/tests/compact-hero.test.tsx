import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Hero } from "@/components/Hero";

describe("compact hero", () => {
  const html = renderToStaticMarkup(<Hero />);
  const intro = html.split("</section>")[0];
  it("leads with the approved promise and working actions", () => {
    expect(intro).toMatch(/<h1[^>]*>[\s\S]*Bacaan kecil\.[\s\S]*Ruang untuk pulih\./);
    expect(intro).toMatch(/href="#percuma"[^>]*>Mulakan percuma/);
    expect(intro).toMatch(/href="#edisi"[^>]*>Lihat koleksi/);
  });
  it("keeps registration reachable outside the compact introduction", () => {
    expect(intro).not.toContain("<form");
    expect(html).toContain('id="percuma"');
    expect(html).toContain('id="lib-email"');
    expect(html.match(/<h1[\s>]/g)).toHaveLength(1);
  });
  it("Void Luxury 4.0 keeps the intro pure typography — no images or decorative layers", () => {
    const images = [...intro.matchAll(/<img[^>]*src="([^"]+)"/g)].map((match) => match[1]);
    expect(images).toEqual([]);
    expect(intro).not.toMatch(/<video|<canvas|ph-hero-plinth|ph-hero-fx|ph-art/);
  });
});
