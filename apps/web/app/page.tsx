import { Faq } from "@/components/Faq";
import { HowItWorks } from "@/components/HowItWorks";
import { SiteHeader } from "@/components/SiteHeader";
import { ChapterPreview } from "@/components/ChapterPreview";
import { Hero } from "@/components/Hero";
import { ClosingCta } from "@/components/ClosingCta";
import { SafetyFooter } from "@/components/SafetyFooter";
import { StickyCta } from "@/components/StickyCta";
import { Reveal } from "@/components/Reveal";
import { TierCompare } from "@/components/TierCompare";
import { Testimonials } from "@/components/Testimonials";
import { EcosystemHub } from "@/components/EcosystemHub";
import { PlateGallery } from "@/components/PlateGallery";
import { StatsStrip } from "@/components/StatsStrip";
import { OrganizationSchema } from "@/components/OrganizationSchema";

import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

function Section({ id, index, title, intro, tone = "plain", children }: {
  id?: string; index?: string; title: string; intro?: string; tone?: "plain" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`ph-section-warm ${tone === "soft" ? "ph-dark-section-raised" : "ph-dark-section"} px-4 py-16 sm:px-5 md:overflow-x-clip md:py-32`}>
      <div className="mx-auto mb-10 max-w-reading text-center md:mb-16">
        {index && <span className="ph-sec-index mb-3 block text-sm tabular-nums text-fg-muted">{index}</span>}
        <h2 className="ph-title text-balance text-fg">{title}</h2>
        {intro && <p className="mt-4 text-lg text-fg-muted">{intro}</p>}
      </div>
      <Reveal className="ph-reveal">{children}</Reveal>
    </section>
  );
}

export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <OrganizationSchema />
      <main id="utama" tabIndex={-1}>
        <Hero />
        <StatsStrip />
        <Section index="01" id="cara" tone="soft" title="Bagaimana ia berfungsi" intro="Tiga langkah kecil. Kamu tentukan kelajuan sendiri.">
          <HowItWorks />
        </Section>
        <Section index="02" id="interaktif" title="Ruang interaktif dan komuniti" intro="Kuiz, kad refleksi, Teman Hati AI dan sesi bimbingan yang menyambung perjalanan bacaan kamu.">
          <EcosystemHub />
        </Section>
        <Section index="03" id="edisi" tone="soft" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
          <TierCompare />
        </Section>
        <Section index="04" id="bab" title="Intai beberapa bab" intro="Pratonton kulit edisi A4 terkini dan tujuh bab utama seperti mana ia ditulis.">
          <ChapterPreview />
        </Section>
        <Section index="05" id="plat" tone="soft" title="Enam plat Edisi Poket" intro="Ilustrasi dalam edisi percuma, satu untuk setiap bab yang kamu baca.">
          <PlateGallery />
        </Section>
        <Section id="suara-pembaca" title="Suara Pembaca" intro="Maklum balas komuniti tentang perkongsian kami di Threads.">
          <Testimonials />
        </Section>
        <Section index="07" id="soalan" tone="soft" title="Soalan lazim">
          <Faq />
        </Section>
        <ClosingCta />
      </main>
      <SafetyFooter />
      <StickyCta />
    </>
  );
}
