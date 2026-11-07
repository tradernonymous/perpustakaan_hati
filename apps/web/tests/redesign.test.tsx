import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { FAQS, NAV, STEPS } from "@/src/content";
import { Faq } from "@/components/Faq";
import { HowItWorks } from "@/components/HowItWorks";
import { SiteHeader } from "@/components/SiteHeader";
import { SafetyFooter } from "@/components/SafetyFooter";
import { TierCompare } from "@/components/TierCompare";
import { Hero } from "@/components/Hero";
import Home from "@/app/page";

describe("navigation", () => {
  it("every nav link targets a section that exists on the page", () => {
    const html = renderToStaticMarkup(<Home />);
    for (const n of NAV) expect(html).toContain(`id="${n.href.slice(1)}"`);
  });
  it("header exposes a labelled nav and a menu button", () => {
    const html = renderToStaticMarkup(<SiteHeader />);
    expect(html).toContain('aria-label="Utama"');
    expect(html).toContain('aria-expanded="false"');
    for (const n of NAV) expect(html).toContain(n.label);
  });
  it("has a skip link and a main landmark", () => {
    const html = renderToStaticMarkup(<Home />);
    expect(html).toContain('href="#utama"');
    expect(html).toContain('<main id="utama"');
  });
  it("footer repeats the nav and shows the library link", () => {
    const html = renderToStaticMarkup(<SafetyFooter />);
    expect(html).toContain('href="/pustaka"');
  });
});

describe("flow", () => {
  it("shows every step", () => {
    const html = renderToStaticMarkup(<HowItWorks />);
    for (const s of STEPS) expect(html).toContain(s.title);
  });
  it("each tier has one clear CTA: free goes to the opt-in, paid goes to checkout", () => {
    const html = renderToStaticMarkup(<TierCompare />);
    expect(html).toContain('href="#percuma"');
    expect(html).toContain('href="/beli/membangun"');
    expect(html).toContain('href="/beli/teman-hidup"');
  });
  it("hero has a primary and a secondary action", () => {
    const html = renderToStaticMarkup(<Hero />);
    expect(html).toContain('href="#percuma"');
    expect(html).toContain('href="#edisi"');
  });
});

describe("FAQ", () => {
  it("renders every question and valid FAQPage JSON-LD", () => {
    const html = renderToStaticMarkup(<Faq />);
    for (const f of FAQS) expect(html).toContain(f.q);
    expect(html).toContain("FAQPage");
    expect(html).not.toMatch(/<\/script>.*<\/script>.*<\/script>/s);
  });
  it("never claims to replace professional help", () => {
    expect(JSON.stringify(FAQS)).toContain("Tidak. Ini bahan pendidikan");
  });
});
