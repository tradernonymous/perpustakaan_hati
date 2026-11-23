/**
 * Psychology & relationships icon layer (Design System 4.1).
 *
 * Every product on the storefront carries one healing-journey motif: the
 * three editions and the four A4 pocket editions each resolve to a psyche id,
 * and every id has a rendered glyph plus a per-concept motion pose. These
 * tests pin the vocabulary so a product can never ship without its mark.
 */
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";

import { TIERS, CHAPTERS } from "@/src/content";
import { EBOOK_COVERS } from "@/src/ebook-covers";
import {
  PSYCHE,
  TIER_PSYCHE,
  CHAPTER_PSYCHE,
  EBOOK_PSYCHE,
  psycheLabel,
  type PsycheId,
} from "@/src/psyche";
import { PsycheIcon, PsycheBadge } from "@/components/PsycheIcon";

const css = readFileSync(path.join(import.meta.dirname, "../styles/motion-psyche.css"), "utf8");

const ALL_IDS = PSYCHE.map((p) => p.id);

describe("psyche vocabulary", () => {
  it("has ten distinct concepts, each with a label and a concept line", () => {
    expect(ALL_IDS).toHaveLength(10);
    expect(new Set(ALL_IDS).size).toBe(10);
    for (const p of PSYCHE) {
      expect(p.label.trim()).not.toBe("");
      expect(p.concept.trim()).not.toBe("");
    }
  });

  it("maps every tier, chapter and ebook to a known psyche id", () => {
    for (const tier of TIERS) {
      expect(ALL_IDS).toContain(TIER_PSYCHE[tier.id]);
    }
    for (const c of CHAPTERS) {
      expect(ALL_IDS).toContain(CHAPTER_PSYCHE[c.no]);
    }
    for (const ebook of EBOOK_COVERS) {
      expect(ALL_IDS).toContain(EBOOK_PSYCHE[ebook.slug]);
    }
  });

  it("resolves labels through the shared lookup", () => {
    for (const id of ALL_IDS) {
      expect(psycheLabel(id)).not.toBe(id);
    }
  });
});

describe("psyche icons", () => {
  it("renders every glyph as an svg with no empty path", () => {
    for (const id of ALL_IDS) {
      const html = renderToStaticMarkup(<PsycheIcon id={id} />);
      expect(html).toContain("<svg");
      // Beyond the svg tag there must be at least one drawn shape.
      expect(html).toMatch(/<(path|circle|rect)\s/);
    }
  });

  it("stamps a medallion with the concept and tier, and carries an accessible name", () => {
    const html = renderToStaticMarkup(<PsycheBadge id="companion" tier="teman-hidup" />);
    expect(html).toContain('data-psyche="companion"');
    expect(html).toContain('data-tier="teman-hidup"');
    expect(html).toContain("Teman hidup");
  });

  it("gives every concept a distinct motion pose in the stylesheet", () => {
    const keyframes = css.match(/@keyframes (ph-psyche-[a-z]+) /g) ?? [];
    const names = new Set(keyframes.map((k) => k.replace("@keyframes ", "").trim()));
    // Ten concept poses plus the shared ring spin.
    expect(names.size).toBe(11);
    expect(names.has("ph-psyche-spin")).toBe(true);
    for (const id of ALL_IDS) {
      expect(css).toContain(`.ph-psyche[data-psyche="${id}"] {`);
    }
  });
});