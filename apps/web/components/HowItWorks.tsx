import { STEPS } from "@/src/content";
import { TiltCard } from "./TiltCard";

/**
 * Imported by app/page.tsx. No API or data schema change — drops the same
 * three locked steps into glass tilt cards inside a ph-journey rail.
 */
export function HowItWorks() {
  return (
    <ol className="ph-journey mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {STEPS.map((s) => (
        <li key={s.no}>
          <TiltCard className="ph-card ph-glass flex h-full gap-4 p-5">
            <span aria-hidden="true" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-pill bg-green-700 font-display text-lg text-cream">
              {s.no}
            </span>
            <div>
              <h3 className="font-display text-xl text-green-900">{s.title}</h3>
              <p className="mt-1 text-sm text-ink-grove">{s.text}</p>
            </div>
          </TiltCard>
        </li>
      ))}
    </ol>
  );
}
