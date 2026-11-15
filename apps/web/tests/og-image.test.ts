import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

/*
 * Social scrapers (Threads, WhatsApp, Facebook, X) ignore SVG OG images, so
 * the emblem alone was never previewed. These tests pin the PNG contract:
 * a real 1200x630 raster, a big twitter card, and metadata that points at it.
 */
const layout = readFileSync(path.join(import.meta.dirname, "../app/layout.tsx"), "utf8");
const ogPath = path.join(import.meta.dirname, "../public/brand/og-image.png");

describe("open graph image", () => {
  it("ships a real PNG at the social-card size", () => {
    const bytes = readFileSync(ogPath);
    // PNG magic number.
    expect(bytes.subarray(0, 8)).toEqual(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
    // IHDR width/height are big-endian uint32 at bytes 16..24.
    expect(bytes.readUInt32BE(16)).toBe(1200);
    expect(bytes.readUInt32BE(20)).toBe(630);
  });

  it("points openGraph and twitter at the PNG, not the SVG", () => {
    expect(layout).toContain('url: "/brand/og-image.png"');
    expect(layout).toContain('images: ["/brand/og-image.png"]');
    expect(layout).not.toContain("emblem-book-heart.svg\", width");
  });

  it("uses the large twitter card so the 1200x630 image is not cropped", () => {
    expect(layout).toContain('card: "summary_large_image"');
  });
});
