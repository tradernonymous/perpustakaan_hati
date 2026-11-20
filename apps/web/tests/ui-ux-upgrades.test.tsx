// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { CerminPasangan } from "@/components/CerminPasangan";
import { EbookDeck } from "@/components/EbookDeck";
import { EcosystemHub } from "@/components/EcosystemHub";
import { HeroExcerptPreview } from "@/components/HeroExcerptPreview";
import { QUESTIONS } from "@/src/games/cermin";
import { siteUrl } from "@/src/site";

afterEach(() => {
  cleanup();
  delete process.env.SITE_URL;
  delete process.env.RAILWAY_PUBLIC_DOMAIN;
});

describe("siteUrl()", () => {
  it("prefers SITE_URL over RAILWAY_PUBLIC_DOMAIN and localhost", () => {
    process.env.SITE_URL = "https://perpustakaanhati.my/";
    process.env.RAILWAY_PUBLIC_DOMAIN = "web-production-0cfb9.up.railway.app";
    expect(siteUrl()).toBe("https://perpustakaanhati.my");
  });

  it("falls back to RAILWAY_PUBLIC_DOMAIN when SITE_URL is unset", () => {
    delete process.env.SITE_URL;
    process.env.RAILWAY_PUBLIC_DOMAIN = "web-production-0cfb9.up.railway.app";
    expect(siteUrl()).toBe("https://web-production-0cfb9.up.railway.app");
  });

  it("falls back to localhost when neither env var is set", () => {
    delete process.env.SITE_URL;
    delete process.env.RAILWAY_PUBLIC_DOMAIN;
    expect(siteUrl()).toBe("http://localhost:3000");
  });
});

describe("EbookDeck", () => {
  it("scopes arrow-key navigation to the carousel region instead of window", () => {
    const { container } = render(<EbookDeck />);
    const carousel = screen.getByRole("group", { name: "Edisi Perpustakaan Hati" });
    const slides = () => Array.from(container.querySelectorAll(".ph-coverflow-card"));

    expect(slides()[0].getAttribute("data-active")).toBe("true");
    expect(slides()[1].getAttribute("data-active")).toBe("false");

    fireEvent.keyDown(window, { key: "ArrowRight" });
    expect(slides()[0].getAttribute("data-active")).toBe("true");

    fireEvent.keyDown(carousel, { key: "ArrowRight" });
    expect(slides()[1].getAttribute("data-active")).toBe("true");

    const inactiveCta = slides()[0].querySelector("a.ph-cta");
    expect(inactiveCta?.getAttribute("tabindex")).toBe("-1");
  });
});

describe("CerminPasangan", () => {
  it("completes smoothly after answering all 5 questions without a blank screen", () => {
    render(<CerminPasangan />);
    for (let i = 0; i < QUESTIONS.length; i++) {
      const q = QUESTIONS[i];
      expect(screen.getByText(q.text)).toBeTruthy();
      fireEvent.click(screen.getByRole("button", { name: q.options[0].label }));
    }
    expect(screen.getByText("Peta Hubungan kamu")).toBeTruthy();
    expect(screen.getByText(/Skor: 10 \/ 10/)).toBeTruthy();
    expect(screen.getByRole("link", { name: /threads/i }).getAttribute("href")).toContain("https://www.threads.net/intent/post");
  });
});

describe("EcosystemHub", () => {
  it("links the enabled interactive and community routes", () => {
    render(<EcosystemHub />);
    const expectedHrefs = [
      "/kad-jujur-hati",
      "/cermin-pasangan",
      "/cabaran-7-hari",
      "/hadiah-hati",
      "/surat-hati",
      "/booking",
      "/kelab",
    ];
    const links = screen.getAllByRole("link").map((el) => el.getAttribute("href"));
    for (const href of expectedHrefs) {
      expect(links).toContain(href);
    }
  });
});

describe("HeroExcerptPreview", () => {
  it("switches live 60-second excerpts when a tab is clicked", () => {
    render(<HeroExcerptPreview />);
    fireEvent.click(screen.getByRole("tab", { name: "Perkara Kecil" }));
    expect(screen.getByText(/Kasih sayang jarang jatuh dari langit/i)).toBeTruthy();
    fireEvent.click(screen.getByRole("tab", { name: "Pulang Kepada Diri" }));
    expect(screen.getByText(/Suara sendiri tidak hilang/i)).toBeTruthy();
  });
});
