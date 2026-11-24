import { existsSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { HeroOrbit3D, EMBLEM_SRC } from "@/components/HeroOrbit3D";

describe("HeroOrbit3D", () => {
  it("renders the poster emblem as SSR fallback", () => {
    const html = renderToStaticMarkup(<HeroOrbit3D />);
    expect(html).toContain(EMBLEM_SRC);
    expect(html).toContain("Edisi Poket");
    expect(html).toContain("Edisi Membangun");
    expect(html).toContain("Teman Hati");
  });

  it("points every orbiting book at a cover file in public/", () => {
    const covers = [
      "/ebooks/cover-poket.png",
      "/ebooks/cover-membangun.png",
      "/ebooks/cover-teman-hidup.png",
    ];
    for (const cover of covers) {
      expect(existsSync(path.join(process.cwd(), "public", cover))).toBe(true);
    }
  });
});
