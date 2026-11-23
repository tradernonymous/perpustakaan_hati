import type { ReactNode } from "react";
import { PSYCHE, type PsycheId } from "@/src/psyche";

/**
 * Psychology & relationships icon set for Perpustakaan Hati.
 *
 * Ten healing-journey motifs, one per concept in `src/psyche.ts`. Each icon is
 * a single 24px line-art glyph drawn in `currentColor`, so it inherits the
 * tier ink or accent colour of whatever surface it sits on and needs no new
 * palette token. Icons are decorative where they ship without a label, so the
 * caller controls the accessible name (the copy next to the icon carries it).
 *
 * The brand copy rules forbid the em dash; none of the paths or labels here
 * touch copy, and the labels in `psyche.ts` use Malay sentence case only.
 */

const STROKE = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
} as const;

const PATHS: Record<PsycheId, ReactNode> = {
  // Kesedaran — an open eye: recognise the trigger before it runs you.
  awareness: (
    <>
      <path d="M2.5 12S6 5.75 12 5.75 21.5 12 21.5 12 18 18.25 12 18.25 2.5 12 2.5 12Z" {...STROKE} />
      <circle cx="12" cy="12" r="2.6" {...STROKE} />
    </>
  ),
  // Corak attach — two interlocking links: anxious, avoidant or secure.
  links: (
    <>
      <circle cx="9" cy="12" r="4.25" {...STROKE} />
      <circle cx="15" cy="12" r="4.25" {...STROKE} />
    </>
  ),
  // Red flag & green flag — two pennants on their poles.
  flags: (
    <>
      <path d="M5 3.5v17.5" {...STROKE} />
      <path d="M5 4 10.5 7 5 10Z" {...STROKE} />
      <path d="M16.5 3.5v17.5" {...STROKE} />
      <path d="M16.5 4 22 7 16.5 10Z" {...STROKE} />
    </>
  ),
  // Diam yang menghukum — a brick wall: silence becomes a structure.
  wall: (
    <>
      <rect x="3.5" y="3.5" width="17" height="17" rx="1.5" {...STROKE} />
      <path d="M3.5 9.25h17" {...STROKE} />
      <path d="M3.5 14.75h17" {...STROKE} />
      <path d="M9 3.5v5.75" {...STROKE} />
      <path d="M15 9.25v5.5" {...STROKE} />
    </>
  ),
  // Bercakap dengan jujur — a speech bubble holding a small heart.
  talk: (
    <>
      <path
        d="M4 5.25h13.5A2.25 2.25 0 0 1 19.75 7.5v7a2.25 2.25 0 0 1-2.25 2.25H9.5l-5 4.5v-4.5H4a2.25 2.25 0 0 1-2.25-2.25v-7A2.25 2.25 0 0 1 4 5.25Z"
        {...STROKE}
      />
      <path d="M10.6 14.35c-.5-.5-1.4-1-1.85-.4-.4.5 0 1.45 1.85 2.5 1.85-1.05 2.25-2 1.85-2.5-.45-.6-1.35-.1-1.85.4Z" {...STROKE} />
    </>
  ),
  // Sempadan — a picket fence: a boundary that guards both sides.
  fence: (
    <>
      <path d="M4 3.5v17" {...STROKE} />
      <path d="M9.3 3.5v17" {...STROKE} />
      <path d="M14.7 3.5v17" {...STROKE} />
      <path d="M20 3.5v17" {...STROKE} />
      <path d="M2 9h20" {...STROKE} />
      <path d="M2 14h20" {...STROKE} />
    </>
  ),
  // Pulih perlahan — a sprout: growing back, slowly.
  heal: (
    <>
      <path d="M12 21v-8.5" {...STROKE} />
      <path d="M12 12.5c0-3.3 2.2-5.7 5.5-5.7 0 3.3-2.2 5.7-5.5 5.7Z" {...STROKE} />
      <path d="M12 12.5c0-3.3-2.2-5.7-5.5-5.7 0 3.3 2.2 5.7 5.5 5.7Z" {...STROKE} />
    </>
  ),
  // Membangun — three ascending steps: building up, one step at a time.
  build: (
    <>
      <rect x="4" y="13.5" width="4" height="7" rx="1" {...STROKE} />
      <rect x="10" y="8.5" width="4" height="12" rx="1" {...STROKE} />
      <rect x="16" y="3.5" width="4" height="17" rx="1" {...STROKE} />
    </>
  ),
  // Teman hidup — a heart within a heart: two hearts, one journey.
  companion: (
    <>
      <path
        d="M12 20.25C8.4 17.35 3.75 13.75 3.75 9.6 3.75 6.9 5.7 5.25 8 5.25c1.45 0 2.7.75 3.4 1.9h1.2c.7-1.15 1.95-1.9 3.4-1.9 2.3 0 4.25 1.65 4.25 4.35 0 4.15-4.65 7.75-8.25 10.65Z"
        {...STROKE}
      />
      <path d="M12 14.75c-.5-.5-1.35-.95-1.75-.35-.35.5 0 1.35 1.75 2.3 1.75-.95 2.1-1.8 1.75-2.3-.4-.6-1.25-.15-1.75.35Z" {...STROKE} />
    </>
  ),
  // Suara sendiri — sound bars: hearing your own voice again.
  voice: (
    <>
      <path d="M6.5 9.25v5.5" {...STROKE} />
      <path d="M9.5 6.5v11" {...STROKE} />
      <path d="M12.5 4v16" {...STROKE} />
      <path d="M15.5 6.5v11" {...STROKE} />
      <path d="M18.5 9.25v5.5" {...STROKE} />
    </>
  ),
};

type IconProps = { id: PsycheId; className?: string; title?: string };

/** The bare glyph. Decorative unless a `title` is given. */
export function PsycheIcon({ id, className = "", title }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      aria-hidden={title ? undefined : true}
      focusable="false"
      role={title ? "img" : undefined}
    >
      {title && <title>{title}</title>}
      {PATHS[id]}
    </svg>
  );
}

type BadgeProps = {
  id: PsycheId;
  /** Optional tier the badge sits on, to tint its ring and light. */
  tier?: "poket" | "membangun" | "teman-hidup";
  className?: string;
};

/**
 * The medallion form: the glyph inside a gilt ring that turns and glows in
 * that concept's own tempo (see `styles/motion-psyche.css`). Decorative, so
 * the surrounding copy keeps the accessible name.
 */
export function PsycheBadge({ id, tier, className = "" }: BadgeProps) {
  const label = PSYCHE.find((p) => p.id === id)?.label ?? id;
  return (
    <span
      className={`ph-psyche ${className}`}
      data-psyche={id}
      data-tier={tier}
      role="img"
      aria-label={label}
    >
      <span className="ph-psyche-ring" aria-hidden="true" />
      <PsycheIcon id={id} className="ph-psyche-glyph" />
    </span>
  );
}