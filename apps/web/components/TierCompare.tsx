import { TIERS, type Tone } from "@/src/content";

const toneBorder: Record<Tone, string> = {
  green: "border-l-green-500",
  gold: "border-l-gold",
  burgundy: "border-l-burgundy-light",
};

export function TierCompare() {
  return (
    <div className="mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {TIERS.map((t) => (
        <article key={t.id} className={`ph-card flex flex-col gap-4 border-l-[3px] p-5 ${toneBorder[t.tone]}`}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={t.seal} alt="" width={72} height={72} className="h-[72px] w-[72px]" />
          <h3 className="font-display text-2xl text-gold-light">{t.name}</h3>
          <p className="font-display text-3xl text-cream">{t.price}</p>
          <p className="text-sm text-on-dark-muted">{t.size}</p>
          <p className="font-display italic text-on-dark">{t.subcopy}</p>
          <ul className="flex flex-col gap-2 text-sm text-on-dark">
            {t.includes.map((i) => (
              <li key={i} className="flex gap-2"><span aria-hidden="true" className="text-gold">◆</span><span>{i}</span></li>
            ))}
          </ul>
        </article>
      ))}
    </div>
  );
}
