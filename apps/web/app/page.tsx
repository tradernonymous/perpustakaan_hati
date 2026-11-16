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
import { TierCompare } from "@/components/TierCompare";
import { TierLadder } from "@/components/TierLadder";
import { EcosystemHub } from "@/components/EcosystemHub";
import { PlateGallery } from "@/components/PlateGallery";
import { SectionOrnament } from "@/components/SectionOrnament";
import { StatsStrip } from "@/components/StatsStrip";
import { Ticker } from "@/components/Ticker";
import { LuxCursor } from "@/components/LuxCursor";
import { OrganizationSchema } from "@/components/OrganizationSchema";

import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

function Section({ id, index, title, intro, tone = "plain", children }: {
  id?: string; index?: string; title: string; intro?: string; tone?: "plain" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`ph-section-warm ${tone === "soft" ? "bg-sage" : "bg-daylight"} scroll-mt-14 overflow-x-clip px-5 py-14 md:py-20`}>
      <div className="mx-auto mb-8 max-w-reading text-center">
        {index && <span className="ph-sec-index">{index}</span>}
        <h2 className="ph-title ph-ink-in text-3xl text-green-900 md:text-4xl">{title}</h2>
        <SectionOrnament className="mt-4" />
        {intro && <p className="mt-3 text-muted-grove">{intro}</p>}
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
        <Section index="02" id="percuma" title="Edisi Poket, percuma" intro="Tinggalkan e-mel atau nombor WhatsApp. Kami hantar apabila bukunya sedia.">
          <OptInForm />
        </Section>
        <Section index="03" id="edisi" tone="soft" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
          <div className="flex flex-col gap-12">
            <TierLadder />
            <EbookDeck />
            <div>
              <h3 className="mb-6 text-center font-display text-2xl text-green-900">Bandingkan semua edisi</h3>
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
        <Section index="06" id="interaktif" title="Ruang interaktif dan komuniti" intro="Kuiz, kad refleksi, Teman Hati AI dan sesi bimbingan yang menyambung perjalanan bacaan kamu.">
          <EcosystemHub />
        </Section>
        <Section index="07" id="pembaca" tone="soft" title="Suara pembaca">
          <Testimonials />
        </Section>
        <Section index="08" id="soalan" title="Soalan lazim">
          <Faq />
        </Section>
      </main>
      <SafetyFooter />
      <StickyCta />
      <LuxCursor />
    </>
  );
}
