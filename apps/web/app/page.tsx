import { Faq } from "@/components/Faq";
import { HowItWorks } from "@/components/HowItWorks";
import { SiteHeader } from "@/components/SiteHeader";
import { ChapterPreview } from "@/components/ChapterPreview";
import { Hero } from "@/components/Hero";
import { ClosingCta } from "@/components/ClosingCta";
import { SafetyFooter } from "@/components/SafetyFooter";
import { StickyCta } from "@/components/StickyCta";
import { Reveal } from "@/components/Reveal";
import { Testimonials } from "@/components/Testimonials";
import { EbookDeck } from "@/components/EbookDeck";
import { TierCompare } from "@/components/TierCompare";
import { TierLadder } from "@/components/TierLadder";
import { EcosystemHub } from "@/components/EcosystemHub";
import { PlateGallery } from "@/components/PlateGallery";
import { SectionOrnament } from "@/components/SectionOrnament";
import { StatsStrip } from "@/components/StatsStrip";
import { Ticker } from "@/components/Ticker";
import { LuxCursor } from "@/components/LuxCursor";
import { CommandPalette } from "@/components/CommandPalette";
import { OrganizationSchema } from "@/components/OrganizationSchema";

import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

function Section({ id, index, title, intro, tone = "plain", children }: {
  id?: string; index?: string; title: string; intro?: string; tone?: "plain" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`ph-section-warm ${tone === "soft" ? "ph-dark-section-raised" : "ph-dark-section"} scroll-mt-14 overflow-x-clip px-5 py-14 md:py-24`}>
      <div className="mx-auto mb-10 max-w-reading text-center">
        {index && <span className="ph-sec-index">{index}</span>}
        <h2 className="ph-title ph-ink-in text-3xl text-fg md:text-5xl">{title}</h2>
        <SectionOrnament className="mt-4" />
        {intro && <p className="mt-3 text-fg-muted">{intro}</p>}
      </div>
      <Reveal>{children}</Reveal>
    </section>
  );
}

export default function Home() {
  return (
    <>
      <SiteHeader />
      <OrganizationSchema />
      <main id="utama">
        <Hero />
        <StatsStrip />
        <Ticker />
        <Section index="01" id="cara" tone="soft" title="Bagaimana ia berfungsi" intro="Tiga langkah kecil. Kamu tentukan kelajuan sendiri.">
          <HowItWorks />
        </Section>
        <Section index="02" id="interaktif" title="Ruang interaktif dan komuniti" intro="Kuiz, kad refleksi, Teman Hati AI dan sesi bimbingan yang menyambung perjalanan bacaan kamu.">
          <EcosystemHub />
        </Section>
        <Section index="03" id="edisi" tone="soft" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
          <div className="flex flex-col gap-12">
            <TierLadder />
            <EbookDeck />
            <div>
              <h3 className="mb-6 text-center font-display text-2xl text-fg">Bandingkan semua edisi</h3>
              <TierCompare />
            </div>
          </div>
        </Section>
        <Section index="04" id="bab" title="Intai beberapa bab" intro="Pratonton kulit edisi A4 terkini dan tujuh bab utama seperti mana ia ditulis.">
          <ChapterPreview />
        </Section>
        <Section index="05" id="plat" tone="soft" title="Enam plat Edisi Poket" intro="Ilustrasi dalam edisi percuma, satu untuk setiap bab yang kamu baca.">
          <PlateGallery />
        </Section>
        <Section index="06" id="pembaca" title="Suara pembaca">
          <Testimonials />
        </Section>
        <Section index="07" id="soalan" tone="soft" title="Soalan lazim">
          <Faq />
        </Section>
        <ClosingCta />
      </main>
      <SafetyFooter />
      <StickyCta />
      <LuxCursor />
      <CommandPalette />
    </>
  );
}
