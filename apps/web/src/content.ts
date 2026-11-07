// Copy source of truth: docs/brand/tier-naming.md, content/ebooks/*/*.md.
// Locked strings (names, prices, subcopy) are asserted in tests/content.test.tsx.

export type Tone = "green" | "gold" | "burgundy";

export type Tier = {
  id: "poket" | "membangun" | "teman-hidup";
  name: string;
  price: string;
  size: string;
  tone: Tone;
  subcopy: string;
  includes: string[];
  seal: string;
};

export const TIERS: Tier[] = [
  {
    id: "poket",
    name: "Edisi Poket",
    price: "Percuma",
    size: "15 hingga 25 muka surat",
    tone: "green",
    subcopy: "Ringkas, menyentuh, mudah dibawa.",
    includes: [
      "Kad Refleksi: Red Flag, Green Flag, Luka Hati, Corak Attach",
      "Ceklis Pencetus Attach (10 soalan)",
      "7 Hari Reset, 60 saat sehari",
      "3 skrip untuk perbualan yang paling sukar minggu ini",
    ],
    seal: "/brand/seal-edisi-poket.svg",
  },
  {
    id: "membangun",
    name: "Edisi Membangun",
    price: "RM 29–49",
    size: "60 hingga 90 muka surat",
    tone: "gold",
    subcopy: "Panduan yang paling jujur dan paling mudah diikuti.",
    includes: [
      "7 bab panduan dengan situasi sebenar rakyat Malaysia",
      "Kit Refleksi: 30 soalan, satu soalan setiap muka surat",
      "5 contoh skrip untuk bercakap dengan jujur",
    ],
    seal: "/brand/seal-edisi-membangun.svg",
  },
  {
    id: "teman-hidup",
    name: "Teman Hidup",
    price: "RM 79–149",
    size: "Buku, buku kerja, skrip dan suara",
    tone: "burgundy",
    subcopy: "Bacaan, kerja, dan skrip — teman hidup.",
    includes: [
      "Semua dalam Edisi Membangun",
      "Buku Kerja 30 Hari",
      "Skrip Bincang Hati ke Hati",
      "Nota Suara Rahimam: Audio Terapi Hati",
      "12 Kad Refleksi untuk dicetak",
    ],
    seal: "/brand/seal-teman-hidup.svg",
  },
];

// Only titles confirmed correct. Bab 4 and Bab 5 are held back until the
// manuscript titles are confirmed (the source spelling looks like a typo).
export const CHAPTERS = [
  { no: 1, title: "Kenapa hubungan sakit", note: "Kenapa kita bertindak balas sebelum sempat berfikir, dan cara menenangkan diri dahulu." },
  { no: 2, title: "Kenali corak attach kamu", note: "Cemas, mengelak atau selamat, dilihat melalui situasi rumah tangga Malaysia." },
  { no: 3, title: "Red flag & green flag", note: "Bahasa yang sama untuk menamakan apa yang kamu rasa, lengkap dengan ceklis green flag." },
  { no: 6, title: "Bila dia tidak berubah", note: "Sempadan, menjaga diri, dan cara pergi dengan baik." },
  { no: 7, title: "Pulih dengan perlahan", note: "Patah hati dan duka, dalam perjalanan 30 hari." },
] as const;

// PLACEHOLDERS: no real reader quotes exist yet. Replace with real, anonymised
// quotes (with permission) before launch, then set placeholder to false.
export const TESTIMONIALS = [
  { quote: "[CONTOH] Ayat pendek tentang apa yang pembaca rasa selepas membaca Edisi Poket.", who: "Pembaca (contoh)", placeholder: true },
  { quote: "[CONTOH] Ayat pendek tentang satu skrip yang membantu mereka bercakap dengan pasangan.", who: "Pembaca (contoh)", placeholder: true },
  { quote: "[CONTOH] Ayat pendek tentang rasa ditemani ketika sukar tidur malam.", who: "Pembaca (contoh)", placeholder: true },
] as const;
