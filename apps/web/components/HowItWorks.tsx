import { STEPS } from "@/src/content";

export function HowItWorks() {
  return (
    <ol className="mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {STEPS.map((s) => (
        <li key={s.no} className="ph-card flex gap-4 p-5">
          <span aria-hidden="true" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-pill bg-green-700 font-display text-lg text-cream">
            {s.no}
          </span>
          <div>
            <h3 className="font-display text-xl text-gold-light">{s.title}</h3>
            <p className="mt-1 text-sm text-on-dark">{s.text}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
