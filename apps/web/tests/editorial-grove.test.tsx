import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Hero } from "@/components/Hero";
import { PlateGallery } from "@/components/PlateGallery";
import { ChapterPreview } from "@/components/ChapterPreview";
import { EcosystemHub } from "@/components/EcosystemHub";
import { ILLUSTRATIONS } from "@/src/illustrations";
import Home from "@/app/page";

/*
 * Design System 3.4 "Editorial Grove": the storefront reads like an
 * illustrated book instead of a stack of centred card rows. It needs
 * real photography (the six Edisi Poket plates), a bento hero, chapter
 * cards that carry art, and a plate gallery.
 *
 * The mobile guards matter as much as the look: the gold beam, the
 * floating glyphs and the blurred sticky header were the three most
 * expensive things the old page did on a phone, and none of them
 * carries meaning that a still frame cannot.
 */
const tokens = readFileSync(path.join(import.meta.dirname, "../styles/design-tokens.css"), "utf8");

describe("editorial grove hero", () => {
  it("puts a real illustration in the hero, not just type", () => {
    const html = renderToStaticMarkup(<Hero />).toLowerCase();
    expect(html).toContain("ph-art");
    expect(html).toContain("/illustrations/");
    // React keeps srcSet and fetchPriority in camelCase in the markup.
    // HTML attribute names are case-insensitive, so the browser reads
    // them fine, which is why the assertions look at the lowercased
    // markup.
    expect(html).toContain("srcset=");
    expect(html).toContain("image/webp");
  });

  it("loads the hero art eagerly, because it is the largest contentful paint", () => {
    const html = renderToStaticMarkup(<Hero />).toLowerCase();
    expect(html).toContain('loading="eager"');
    expect(html).toContain('fetchpriority="high"');
  });

  it("gives the hero art real alt text", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain(ILLUSTRATIONS[0].alt);
  });

  it("keeps the wordmark as live text in an h1", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toMatch(/<h1[^>]*>[\s\S]*Perpustakaan[\s\S]*HATI[\s\S]*<\/h1>/);
  });

  it("still offers the free edition and the edition list", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain('href="#percuma"');
    expect(html).toContain('href="#edisi"');
  });
});

describe("plate gallery", () => {
  it("renders the six plates in a labelled, focusable region", () => {
    const html = renderToStaticMarkup(<PlateGallery />);
    expect(html).toContain("ph-gallery");
    expect(html).toContain('aria-label="Enam ilustrasi Edisi Poket"');
    expect(html).toContain('tabindex="0"');
    expect(html.match(/<figure/g)?.length).toBe(ILLUSTRATIONS.length);
  });

  it("gives every plate a caption and alt text", () => {
    const html = renderToStaticMarkup(<PlateGallery />);
    for (const item of ILLUSTRATIONS) {
      expect(html).toContain(item.caption);
      expect(html).toContain(item.alt);
    }
  });

  it("is on the homepage", () => {
    expect(renderToStaticMarkup(<Home />)).toContain("ph-gallery");
  });
});

describe("chapter cards", () => {
  it("lays the chapters out as cards, not a plain list", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).toContain("ph-chapter-grid");
    expect(html).toContain("ph-chapter-card");
  });

  it("keeps the held-back chapters marked as pending", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).toContain("Bab 4");
    expect(html).toContain("Tajuk akan diumumkan");
    expect(html).not.toContain("Bicornak");
  });
});

describe("bento ecosystem", () => {
  it("uses a bento grid with one feature card", () => {
    const html = renderToStaticMarkup(<EcosystemHub />);
    expect(html).toContain("ph-bento");
    expect(html).toContain("ph-bento-feature");
  });

  it("keeps every interactive route reachable", () => {
    const html = renderToStaticMarkup(<EcosystemHub />);
    for (const href of [
      "/kad-jujur-hati",
      "/cermin-pasangan",
      "/teman-hati",
      "/cabaran-7-hari",
      "/hadiah-hati",
      "/surat-hati",
      "/booking",
      "/kelab",
    ]) {
      expect(html).toContain(`href="${href}"`);
    }
  });
});

describe("editorial grove layer", () => {
  it("ships the 3.4 layer", () => {
    expect(tokens).toContain("EDITORIAL GROVE");
    expect(tokens).toContain(".ph-art {");
    expect(tokens).toContain(".ph-gallery {");
    expect(tokens).toContain(".ph-bento {");
  });

  it("bumps the system version to 3.4.0", () => {
    expect(tokens).toContain("--ph-system-version: '3.4.0'");
  });

  it("stops the three expensive effects on a phone", () => {
    // The gold beam spins a conic gradient forever.
    expect(tokens).toMatch(/@media \(max-width: 767px\)[\s\S]{0,900}?\.ph-beam::before \{ animation: none; \}/);
    // The blurred sticky header repaints on every scroll.
    expect(tokens).toMatch(/@media \(max-width: 767px\)[\s\S]{0,900}?\.ph-header/);
  });
});
