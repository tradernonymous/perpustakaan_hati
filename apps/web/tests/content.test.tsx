import { formatRM, priceSen } from "@/src/catalog";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { TIERS, CHAPTERS, TESTIMONIALS } from "@/src/content";
import { TierCompare } from "@/components/TierCompare";
import { ChapterPreview } from "@/components/ChapterPreview";
import { Testimonials } from "@/components/Testimonials";
import { SafetyFooter } from "@/components/SafetyFooter";
import { Hero } from "@/components/Hero";
import { StickyCta } from "@/components/StickyCta";

describe("tier ladder matches docs/brand/tier-naming.md", () => {
  it("has the three locked names in order", () => {
    expect(TIERS.map((t) => t.name)).toEqual(["Edisi Poket", "Edisi Membangun", "Teman Hidup"]);
  });
  it("has the locked prices", () => {
    expect(TIERS.map((t) => t.price)).toEqual(["Percuma", "RM 29–49", "RM 79–149"]);
  });
  it("uses the locked subcopy", () => {
    expect(TIERS[0].subcopy).toBe("Ringkas, menyentuh, mudah dibawa.");
    expect(TIERS[1].subcopy).toBe("Panduan yang paling jujur dan paling mudah diikuti.");
    expect(TIERS[2].subcopy).toBe("Bacaan, kerja, dan skrip, teman hidup.");
  });
  it("never uses retired tier names", () => {
    const all = JSON.stringify(TIERS);
    expect(all).not.toMatch(/Edisi Dompet|Edisi Pulih/);
  });
  it("renders every tier name and price", () => {
    const html = renderToStaticMarkup(<TierCompare />);
    for (const t of TIERS) {
      expect(html).toContain(t.name);
      expect(html).toContain(t.id === "poket" ? "Percuma" : formatRM(priceSen(t.id)));
    }
  });
});

describe("chapter previews", () => {
  it("shows all seven confirmed chapter titles without draft typos", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).not.toContain("Bicornak");
    expect(html).not.toContain("pertapaan");
    expect(html).toContain("Bila pertengkaran menjadi diam");
    expect(html).toContain("Bercakap dengan jujur");
    expect(CHAPTERS.length).toBe(7);
    for (const c of CHAPTERS) expect(html).toContain(c.title.replace(/&/g, "&amp;"));
  });
});

describe("testimonials are honest placeholders", () => {
  it("every placeholder quote is flagged and visibly labelled", () => {
    const html = renderToStaticMarkup(<Testimonials />);
    for (const t of TESTIMONIALS) {
      if (t.quote.startsWith("[CONTOH]")) expect(t.placeholder).toBe(true);
    }
    expect(TESTIMONIALS.some((t) => t.placeholder)).toBe(true);
    expect(html).toContain("CONTOH");
  });
});

describe("safety footer", () => {
  it("shows Talian HEAL 15555, Befrienders and the PDPA note", () => {
    const html = renderToStaticMarkup(<SafetyFooter />);
    expect(html).toContain("15555");
    expect(html).toContain("Befrienders");
    expect(html).toContain("PDPA");
  });
});

describe("hero and sticky CTA", () => {
  it("hero carries the tagline and a CTA to the opt-in", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("Ruang untuk pulih.");
    expect(html).toContain('id="percuma"');
    expect(html).toContain('id="lib-email"');
  });
  it("sticky CTA links to the opt-in", () => {
    expect(renderToStaticMarkup(<StickyCta />)).toContain('href="#percuma"');
  });
});
