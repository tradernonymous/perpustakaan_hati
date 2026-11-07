import { ChapterPreview } from "@/components/ChapterPreview";
import { Hero } from "@/components/Hero";
import { OptInForm } from "@/components/OptInForm";
import { SafetyFooter } from "@/components/SafetyFooter";
import { StickyCta } from "@/components/StickyCta";
import { Testimonials } from "@/components/Testimonials";
import { TierCompare } from "@/components/TierCompare";

function Section({ id, title, intro, tone = "night", children }: {
  id?: string; title: string; intro?: string; tone?: "night" | "soft"; children: React.ReactNode;
}) {
  return (
    <section id={id} className={`${tone === "soft" ? "bg-forest-soft" : "bg-forest-night"} scroll-mt-4 px-5 py-14 md:py-20`}>
      <div className="mx-auto mb-8 max-w-reading text-center">
        <h2 className="ph-title text-3xl text-gold-light md:text-4xl">{title}</h2>
        {intro && <p className="mt-3 text-on-dark-muted">{intro}</p>}
      </div>
      {children}
    </section>
  );
}

export default function Home() {
  return (
    <main>
      <Hero />
      <Section id="percuma" tone="soft" title="Edisi Poket, percuma" intro="Tinggalkan e-mel atau nombor WhatsApp. Kami hantar apabila bukunya sedia.">
        <OptInForm />
      </Section>
      <Section id="edisi" title="Tiga edisi, satu perjalanan" intro="Mulakan kecil. Naik bila kamu bersedia.">
        <TierCompare />
      </Section>
      <Section id="bab" tone="soft" title="Intai beberapa bab">
        <ChapterPreview />
      </Section>
      <Section id="pembaca" title="Suara pembaca">
        <Testimonials />
      </Section>
      <SafetyFooter />
      <StickyCta />
    </main>
  );
}
