import { FAQS } from "@/src/content";

export function Faq() {
  const ld = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQS.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })),
  };
  return (
    <div className="mx-auto flex max-w-reading flex-col gap-3">
      {FAQS.map((f) => (
        <details key={f.q} className="ph-lux ph-card group p-4">
          <summary className="flex min-h-tap cursor-pointer list-none items-center justify-between gap-4 font-display text-lg text-gold-light">
            {f.q}
            <span aria-hidden="true" className="text-green-400 transition-transform group-open:rotate-45">+</span>
          </summary>
          <p className="mt-2 text-on-dark">{f.a}</p>
        </details>
      ))}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld).replace(/</g, "\\u003c") }} />
    </div>
  );
}
