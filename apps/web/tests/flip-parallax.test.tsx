import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { FlipCard } from "@/components/FlipCard";
import { PointerParallax } from "@/components/PointerParallax";

describe("FlipCard", () => {
  it("renders both faces and a toggle button for touch users", () => {
    const html = renderToStaticMarkup(
      <FlipCard front={<span>Depan</span>} back={<span>Belakang</span>} />,
    );
    expect(html).toContain("Depan");
    expect(html).toContain("Belakang");
    expect(html).toContain("ph-flip__toggle");
    expect(html).toContain('data-flipped="false"');
  });
});

describe("PointerParallax", () => {
  it("wraps its children in the parallax container", () => {
    const html = renderToStaticMarkup(
      <PointerParallax className="extra">
        <p>Teks</p>
      </PointerParallax>,
    );
    expect(html).toContain("ph-parallax-3d");
    expect(html).toContain("extra");
    expect(html).toContain("Teks");
  });
});
