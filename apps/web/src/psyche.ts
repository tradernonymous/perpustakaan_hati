// Psychology & relationships icon vocabulary for Perpustakaan Hati.
//
// One icon per healing-journey concept. The three tiers and the four pocket
// edition ebooks all resolve to one of these, so every product carries a
// relationship-psychology mark of its own. Icons are decorative (aria-hidden
// where they ship without a label) and draw in currentColor, so they inherit
// the tier ink or accent colour of whatever surface they sit on.
//
// Rendered by components/PsycheIcon.tsx. Canonical English copy is here; the
// labels speak Malay sentence case, per the brand copy rules.

export type PsycheId =
  | "awareness"
  | "links"
  | "flags"
  | "wall"
  | "talk"
  | "fence"
  | "heal"
  | "build"
  | "companion"
  | "voice";

export type Psyche = { id: PsycheId; label: string; concept: string };

export const PSYCHE: Psyche[] = [
  { id: "awareness", label: "Kesedaran", concept: "Kenali pemicu sebelum ia mengawal kamu." },
  { id: "links", label: "Corak attach", concept: "Cemas, mengelak atau selamat." },
  { id: "flags", label: "Red flag & green flag", concept: "Bahasa yang sama untuk menamakan rasa." },
  { id: "wall", label: "Diam yang menghukum", concept: "Bila diam berubah menjadi hukuman." },
  { id: "talk", label: "Bercakap dengan jujur", concept: "Luahkan keperluan tanpa menyerang." },
  { id: "fence", label: "Sempadan", concept: "Sempadan yang menjaga dua-dua belah." },
  { id: "heal", label: "Pulih perlahan", concept: "Tumbuh semula, perlahan-lahan." },
  { id: "build", label: "Membangun", concept: "Membina, langkah demi langkah." },
  { id: "companion", label: "Teman hidup", concept: "Dua hati, satu perjalanan." },
  { id: "voice", label: "Suara sendiri", concept: "Dengar suara sendiri semula." },
];

/** Each tier carries one journey motif: aware -> build -> live with. */
export const TIER_PSYCHE: Record<"poket" | "membangun" | "teman-hidup", PsycheId> = {
  poket: "awareness",
  membangun: "build",
  "teman-hidup": "companion",
};

/** The seven chapter headlines map onto the same psychology vocabulary. */
export const CHAPTER_PSYCHE: Record<number, PsycheId> = {
  1: "awareness",
  2: "links",
  3: "flags",
  4: "wall",
  5: "talk",
  6: "fence",
  7: "heal",
};

/** The four A4 pocket editions carry their own relationship concept. */
export const EBOOK_PSYCHE: Record<string, PsycheId> = {
  "ruang-atau-hukuman": "wall",
  "perkara-kecil-hati-kenyang": "heal",
  "pulang-kepada-suara-sendiri": "voice",
  "cuma-kawan-pejabat": "fence",
};

export function psycheLabel(id: PsycheId): string {
  return PSYCHE.find((p) => p.id === id)?.label ?? id;
}