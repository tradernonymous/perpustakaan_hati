import { TIERS } from "@/src/content";

/**
 * The Ladder of Light (Design System 3.5).
 *
 * The three tiers as a staircase: each step is one rung higher than the
 * last, in that tier's own colour, with that tier's own silhouette on top.
 * This is where "higher tier, more premium" is shown rather than claimed.
 *
 * Rules this component obeys:
 *  - colour never carries the tier alone: every step shows the tier's
 *    silhouette (circle / hexagon / arch) and its name;
 *  - the name always ships with the shape, so a colour-blind reader and a
 *    screen reader get the same three tiers;
 *  - the whole ladder is one list, so the order is read as an order.
 */
export function TierLadder() {
  return (
    <ol className="ph-ladder mx-auto max-w-grid list-none px-5" aria-label="Tiga edisi, dari yang paling ringkas ke yang paling lengkap">
      {TIERS.map((tier, i) => (
        <li key={tier.id} className="ph-ladder-step" data-tier={tier.id}>
          <span className="ph-caps text-[0.6rem] text-fg-muted">
            {String(i + 1).padStart(2, "0")}
          </span>
          <span className="ph-ladder-medal ph-tier-medal ph-tier-rise" aria-hidden="true" />
          <span className="ph-ladder-label text-base">{tier.name}</span>
          <span className="ph-ladder-note">{tier.price}</span>
          <span className="ph-ladder-note">{tier.size}</span>
          <span className="ph-ladder-rung" aria-hidden="true" />
        </li>
      ))}
    </ol>
  );
}
