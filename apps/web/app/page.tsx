import { Faq } from "@/components/Faq";
import { HowItWorks } from "@/components/HowItWorks";
import { SiteHeader } from "@/components/SiteHeader";
import { ChapterPreview } from "@/components/ChapterPreview";
import { Hero } from "@/components/Hero";
import { OptInForm } from "@/components/OptInForm";
import { SafetyFooter } from "@/components/SafetyFooter";
import { StickyCta } from "@/components/StickyCta";
import { Reveal } from "@/components/Reveal";
import { Testimonials } from "@/components/Testimonials";
import { EbookDeck } from "@/components/EbookDeck";
import { SectionOrnament } from "@/components/SectionOrnament";
import { StatsStrip } from "@/components/StatsStrip";
import { Ticker } from "@/components/Ticker";
import { LuxCursor } from "@/components/LuxCursor";

import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

function Section({ id, title, intro, tone = "night", children }: {
  id?: string; title: string; intro?: string; tone?: "night" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`ph-section-warm ${tone === "soft" ? "bg-forest-soft" : "bg-forest-night"} scroll-mt-14 px-5 py-14 md:py-20`}>
      <div className="mx-auto mb-8 max-w-reading text-center">
        <h2 className="ph-title ph-ink-in text-3xl text-gold-light md:text-4xl">{title}</h2>
        <SectionOrnament className="mt-4" />
        {intro && <p className="mt-3 text-on-dark-muted">{intro}</p>}
      </div>
      <Reveal>{children}</Reveal>
    </section>
  );
}

export default function Home() {
  return (
    <>
      <a href="#utama" className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-toast focus:rounded focus:bg-cream focus:px-3 focus:py-2 focus:text-ink">Langkau ke kandungan</a>
      <SiteHeader />
      <main id="utama">
      <Hero />
      <StatsStrip />
      <Ticker />
      <Section id="cara" tone="soft" title="Bagaimana ia berfungsi" intro="Tiga langkah kecil. Kamu tentukan kelajuan sendiri.">
        <HowItWorks />
      </Section>
      <Section id="percuma" title="Edisi Poket, percuma" intro="Tinggalkan e-mel atau nombor WhatsApp. Kami hantar apabila bukunya sedia.">
        <OptInForm />
      </Section>
      <Section id="edisi" tone="soft" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
        <EbookDeck />
      </Section>
      <Section id="bab" title="Intai beberapa bab">
        <ChapterPreview />
      </Section>
      <Section id="pembaca" tone="soft" title="Suara pembaca">
        <Testimonials />
      </Section>
      <Section id="soalan" title="Soalan lazim">
        <Faq />
      </Section>
      </main>
      <SafetyFooter />
      <StickyCta />
      <LuxCursor />
    </>
  );
}
