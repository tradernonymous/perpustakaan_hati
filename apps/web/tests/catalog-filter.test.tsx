// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it } from "vitest";
import { Catalog } from "@/components/Catalog";
import { TIERS } from "@/src/content";
import { EBOOK_COVERS } from "@/src/ebook-covers";

afterEach(() => {
  cleanup();
  window.history.replaceState(null, "", "/");
});

const chips = () => screen.getByRole("navigation", { name: /tapis edisi/i });

describe("catalog contents", () => {
  it("renders every edition and every A4 cover before any filter is applied", () => {
    const html = renderToStaticMarkup(<Catalog />);
    for (const tier of TIERS) {
      expect(html).toContain(tier.name);
      expect(html).toContain(`data-tier="${tier.id}"`);
    }
    for (const cover of EBOOK_COVERS) {
      expect(html).toContain(cover.title);
      expect(html).toContain(cover.webp);
    }
    expect(html).toContain("ph-ebook-shelf");
    expect(html).toContain('width="560"');
    expect(html).toContain('height="792"');
  });

  it("exposes a search box and one chip per edition plus Semua", () => {
    const html = renderToStaticMarkup(<Catalog />);
    expect(html).toContain('type="search"');
    expect(html).toContain("Semua");
    for (const tier of TIERS) expect(html).toContain(`href="?edisi=${tier.id}"`);
  });
});

describe("catalog URL state", () => {
  it("reads q and edisi from the URL on load", () => {
    window.history.replaceState(null, "", "/?q=ruang&edisi=poket");
    render(<Catalog />);
    expect((screen.getByRole("searchbox") as HTMLInputElement).value).toBe("ruang");
    const html = document.body.innerHTML;
    expect(html).toContain("Ruang atau Hukuman");
    expect(html).not.toContain("Cuma Kawan Pejabat");
    expect(document.querySelector('[data-tier="membangun"]')).toBeNull();
    expect(within(chips()).getByRole("link", { name: "Edisi Poket" }).getAttribute("aria-current")).toBe("true");
  });

  it("writes the search term into the URL without navigating away", () => {
    window.history.replaceState(null, "", "/#katalog");
    render(<Catalog />);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "kawan" } });
    expect(new URLSearchParams(window.location.search).get("q")).toBe("kawan");
    expect(window.location.hash).toBe("#katalog");
    const html = document.body.innerHTML;
    expect(html).toContain("Cuma Kawan Pejabat");
    expect(html).not.toContain("Ruang atau Hukuman");
  });

  it("filters by edition and marks the active chip in the URL", () => {
    window.history.replaceState(null, "", "/");
    render(<Catalog />);
    fireEvent.click(within(chips()).getByRole("link", { name: "Edisi Membangun" }));
    expect(new URLSearchParams(window.location.search).get("edisi")).toBe("membangun");
    const html = document.body.innerHTML;
    expect(document.querySelector('[data-tier="membangun"]')).not.toBeNull();
    expect(html).not.toContain("Ruang atau Hukuman");
    expect(within(chips()).getByRole("link", { name: "Edisi Membangun" }).getAttribute("aria-current")).toBe("true");
  });

  it("clears a filter with the Semua chip", () => {
    window.history.replaceState(null, "", "/?edisi=teman-hidup");
    render(<Catalog />);
    expect(document.body.innerHTML).not.toContain("Ruang atau Hukuman");
    fireEvent.click(within(chips()).getByRole("link", { name: "Semua" }));
    expect(window.location.search).toBe("");
    expect(document.body.innerHTML).toContain("Ruang atau Hukuman");
  });

  it("follows browser back and forward without losing the form state", () => {
    render(<Catalog />);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "diam" } });
    expect((screen.getByRole("searchbox") as HTMLInputElement).value).toBe("diam");
    window.history.replaceState(null, "", "/?q=suara");
    fireEvent(window, new PopStateEvent("popstate"));
    expect((screen.getByRole("searchbox") as HTMLInputElement).value).toBe("suara");
  });

  it("reports no results and offers a reset", () => {
    window.history.replaceState(null, "", "/?q=zzzz");
    render(<Catalog />);
    expect(screen.getByRole("status").textContent).toMatch(/0/);
    expect(screen.getByText(/tiada hasil/i)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /padam tapis/i }));
    expect(window.location.search).toBe("");
    expect(document.body.innerHTML).toContain("Ruang atau Hukuman");
  });
});
