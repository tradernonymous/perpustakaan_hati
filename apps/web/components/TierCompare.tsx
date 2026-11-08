import { TIERS, type Tone } from "@/src/content";
import { ProductCover } from "./ProductCover";

const toneBorder: Record<Tone, string> = {
  green: "border-l-green-500",
  gold: "border-l-gold",
  burgundy: "border-l-burgundy-light",
};

export function TierCompare() {
  return (
    <div className="mx-auto grid max-w-grid gap-5 md:grid-cols-3">
      {TIERS.map((t) => {
        const free = t.id === "poket";
        return (
          <article key={t.id} className={`ph-card relative flex flex-col gap-4 border-l-[3px] p-5 ${toneBorder[t.tone]} ${t.id === "membangun" ? "ring-1 ring-gold-deep" : ""}`}>
            {t.id === "membangun" && (
              <span className="absolute right-4 top-4 rounded-pill bg-green-700 px-3 py-1 text-xs font-semibold text-cream">
                Langkah seterusnya
              </span>
            )}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={t.seal} alt="" width={72} height={72} className="h-[72px] w-[72px]" />
            <ProductCover name={t.name} src={t.cover} className="max-w-[180px]" />
            <h3 className="font-display text-2xl text-green-900">{t.name}</h3>
            <p className="font-display text-3xl text-green-900">{t.price}</p>
            <p className="text-sm text-muted-grove">{t.size}</p>
            <p className="font-display italic text-ink-grove">{t.subcopy}</p>
            <ul className="flex flex-1 flex-col gap-2 text-sm text-ink-grove">
              {t.includes.map((i) => (
                <li key={i} className="flex gap-2"><span aria-hidden="true" className="text-gold">◆</span><span>{i}</span></li>
              ))}
            </ul>
            <a href={free ? "#percuma" : `/beli/${t.id}`} className={free ? "ph-cta min-h-cta-mobile justify-center" : "btn-ghost min-h-cta-mobile justify-center"}>
              {free ? "Dapatkan percuma" : `Beli ${t.name}`}
            </a>
          </article>
        );
      })}
    </div>
  );
}
