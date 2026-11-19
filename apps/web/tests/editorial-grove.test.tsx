import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Hero } from "@/components/Hero";
import { PlateGallery } from "@/components/PlateGallery";
import { ChapterPreview } from "@/components/ChapterPreview";
import { TierCompare } from "@/components/TierCompare";
import { EcosystemHub } from "@/components/EcosystemHub";
import { ILLUSTRATIONS } from "@/src/illustrations";
import { EBOOK_COVERS } from "@/src/ebook-covers";
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

  it("still offers the free edition and the edition list", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain('id="percuma"');
    expect(html).toContain('id="optin-email"');
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

  it("renders confirmed titles for Bab 4 and 5 with plates", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).toContain("Bab 4");
    expect(html).toContain("Bila pertengkaran menjadi diam");
    expect(html).toContain("Bercakap dengan jujur");
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

  it("bumps the system version to the current release", () => {
    expect(tokens).toContain("--ph-system-version: '3.8.0'");
  });

  it("stops the three expensive effects on a phone", () => {
    // The gold beam spins a conic gradient forever.
    expect(tokens).toMatch(/@media \(max-width: 767px\)[\s\S]{0,900}?\.ph-beam::before \{ animation: none; \}/);
    // The blurred sticky header repaints on every scroll.
    expect(tokens).toMatch(/@media \(max-width: 767px\)[\s\S]{0,900}?\.ph-header/);
  });
});

describe("refinements: A4 covers, comparison table, and hero plinth", () => {
  it("renders all five real A4 ebook covers inside #bab with A4 dimensions", () => {
    const html = renderToStaticMarkup(<ChapterPreview />);
    expect(html).toContain("ph-ebook-shelf");
    expect(html).toContain("ph-a4-cover");
    expect(html).toContain('width="560"');
    expect(html).toContain('height="792"');
    for (const cover of EBOOK_COVERS) {
      expect(html).toContain(cover.webp);
      expect(html).toContain(cover.title);
    }
    expect(tokens).toMatch(/\.ph-a4-cover\s*\{[\s\S]*aspect-ratio:\s*210\s*\/\s*297/);
    expect(tokens).toMatch(/\.ph-chapter-art\s*\{[\s\S]*aspect-ratio:\s*210\s*\/\s*297/);
  });

  it("renders TierCompare as a comparison table with tick and blank markers", () => {
    const html = renderToStaticMarkup(<TierCompare />);
    expect(html).toContain("<table");
    expect(html).toContain("ph-compare-table");
    expect(html).toContain("ph-tick");
    expect(html).toContain("✓");
    expect(html).toContain("Tidak termasuk dalam Edisi Poket");
  });

});
