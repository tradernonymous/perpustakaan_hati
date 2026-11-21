import { formatRM, priceSen } from "@/src/catalog";
import { EcosystemHub } from "@/components/EcosystemHub";
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
import publishedCatalog from "@/src/publication/catalog.json";
import { Catalog } from "@/components/Catalog";
import { SectionOrnament } from "@/components/SectionOrnament";
import { LuxCursor } from "@/components/LuxCursor";
import { OrganizationSchema } from "@/components/OrganizationSchema";

import type { Metadata } from "next";

export const metadata: Metadata = { alternates: { canonical: "/" } };

function Section({ id, index, title, intro, tone = "plain", children }: {
  id?: string; index?: string; title: string; intro?: string; tone?: "plain" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`ph-section-warm ${tone === "soft" ? "ph-dark-section-raised" : "ph-dark-section"} px-4 py-10 sm:px-5 md:overflow-x-clip md:py-24`}>
      <div className="mx-auto mb-6 max-w-reading text-center md:mb-10">
        {index && <span className="ph-sec-index hidden md:inline-block">{index}</span>}
        <h2 className="ph-title ph-ink-in text-balance text-3xl text-fg md:text-5xl">{title}</h2>
        <SectionOrnament className="mt-3 md:mt-4" />
        {intro && <p className="mt-3 text-fg-muted">{intro}</p>}
      </div>
      <Reveal className="ph-home-reveal">{children}</Reveal>
    </section>
  );
}

// Pass only the editorial fields used for rendering across the client boundary.
const publishedCards = publishedCatalog.map(({ tier, title, summary, artwork, sample }) => ({
  tier, title, summary, artwork, sample,
}));

export default function Home() {
  return (
    <>
      <SiteHeader />
      <OrganizationSchema />
      <main id="utama" tabIndex={-1}>
        <Hero />
        <Section index="01" id="bab" title="Intai beberapa bab" intro="Tujuh bab utama, dalam Bahasa Melayu yang dekat di hati.">
          <ChapterPreview />
        </Section>
        <Section index="02" id="edisi" tone="soft" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
          <TierCompare />
        </Section>
        <Section index="03" id="katalog" title="Katalog edisi dan buku">
          <Catalog publications={publishedCards} prices={{ poket: "Percuma", membangun: formatRM(priceSen("membangun")), "teman-hidup": formatRM(priceSen("teman-hidup")) }} />
        </Section>
        <Section id="filem" tone="soft" title="Filem pelancaran">
          <figure className="mx-auto max-w-reading">
            <video
              aria-label="Filem pelancaran Perpustakaan Hati"
              className="aspect-video w-full rounded border border-line bg-surface"
              width={1280}
              height={720}
              controls
              playsInline
              preload="none"
              poster="/launch/poster.jpg"
              src="/launch/editions-16x9.mp4"
            >
              <a href="/launch/editions-16x9.mp4">Muat turun filem pelancaran</a>
            </video>
            <figcaption className="mt-3 flex flex-wrap items-center gap-x-5 text-sm text-fg-muted">
              <span>25 saat · Tiga edisi</span>
              <a className="inline-flex min-h-tap items-center underline" href="/launch/editions-9x16.mp4">Versi 9:16</a>
              <a className="inline-flex min-h-tap items-center underline" href="/launch/editions-4x5.mp4">Versi 4:5</a>
            </figcaption>
          </figure>
        </Section>
        <Section index="04" id="cara" tone="soft" title="Bagaimana ia berfungsi" intro="Tiga langkah kecil. Kamu tentukan kelajuan sendiri.">
          <HowItWorks />
        </Section>
        <Section id="interaktif" tone="soft" title="Ruang interaktif dan komuniti">
          <EcosystemHub />
        </Section>
        <Section id="suara-pembaca" title="Suara Pembaca" intro="Maklum balas komuniti tentang perkongsian kami di Threads.">
          <Testimonials />
        </Section>
        <Section index="05" id="soalan" title="Soalan lazim">
          <Faq />
        </Section>
        <ClosingCta />
      </main>
      <SafetyFooter />
      <StickyCta />
      <LuxCursor />
    </>
  );
}
