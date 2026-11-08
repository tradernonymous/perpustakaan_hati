import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { HeroBook } from "@/components/HeroBook";
import { HeroGlyphs } from "@/components/HeroGlyphs";
import { ReadingProgress } from "@/components/ReadingProgress";
import { TiltCard } from "@/components/TiltCard";
import { EbookDeck } from "@/components/EbookDeck";
import { Hero } from "@/components/Hero";
import Home from "@/app/page";

describe("premium interactive experience", () => {
  it("uses a 3D book with live tilt, foil depth and page controls", () => {
    const html = renderToStaticMarkup(<HeroBook name="Edisi Poket" />);
    expect(html).toContain("ph-book-3d");
    expect(html).toContain("ph-book-spine");
    expect(html).toContain("ph-book-pages");
    expect(html).toContain("ph-book-sheen");
    expect(html).toContain("aria-label");
    expect(html).toContain("Buka muka surat seterusnya");
  });

  it("hero composes book, progress and educational chapters", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("ph-book-3d");
    expect(html).toContain("ph-progress");
    expect(html).toContain("Kad Refleksi");
    expect(html).toContain("7 Hari Reset");
    expect(html).toContain("Baca 60 saat sehari");
  });

  it("deck uses a coverflow with the active edition raised and readable", () => {
    const html = renderToStaticMarkup(<EbookDeck />);
    expect(html).toContain("ph-coverflow");
    expect(html).toContain("ph-coverflow-card");
    expect(html).toContain("data-active");
    expect(html).toContain("Edisi Membangun");
  });

  it("homepage has warm scroll rhythm, liquid glass and numbered reading journey", () => {
    const html = renderToStaticMarkup(<Home />);
    expect(html).toContain("ph-section-warm");
    expect(html).toContain("ph-glass");
    expect(html).toContain("ph-journey");
    expect(html).toContain("7 Hari Reset");
  });

  it("tilt cards expose a learnable focus and reduced-motion-safe surface", () => {
    const html = renderToStaticMarkup(
      <TiltCard>
        <p>Nota</p>
      </TiltCard>
    );
    expect(html).toContain("ph-tilt-card");
    expect(html).toContain("tabindex");
    expect(html).toContain("Nota");
  });

  it("reading progress is labelled and stops motion when the user prefers it", () => {
    const html = renderToStaticMarkup(<ReadingProgress />);
    expect(html).toContain("ph-progress");
    expect(html).toContain("Kemajuan bacaan");
    expect(html).toContain("aria-label");
  });

  it("hero has movable glyphs that drift with pointer hover", () => {
    const html = renderToStaticMarkup(<HeroGlyphs />);
    expect(html).toContain("ph-glyphs");
    expect(html).toContain("ph-glyph");
    expect(html).toContain('aria-hidden="true"');
  });

  it("hero embeds the glyph field behind the book", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("ph-glyphs");
  });

  it("hero is mobile-first: stacked actions and scaled book on small screens", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain("min-h-cta-mobile");
    expect(html).toContain("grid");
  });
});
