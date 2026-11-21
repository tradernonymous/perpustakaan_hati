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
        <details key={f.q} className="ph-lux ph-card ph-faq">
          <summary className="flex min-h-tap cursor-pointer list-none items-center justify-between gap-4 px-4 py-3.5 font-display text-lg text-fg sm:px-5">
            {f.q}
            <span aria-hidden="true" className="ph-faq-mark text-fg-healing">+</span>
          </summary>
          <div className="ph-faq-body">
            <div className="ph-faq-inner">
              <p className="px-4 pb-4 text-fg sm:px-5">{f.a}</p>
            </div>
          </div>
        </details>
      ))}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld).replace(/</g, "\\u003c") }} />
    </div>
  );
}
