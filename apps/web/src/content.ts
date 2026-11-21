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
  /** Cover image path, or null while the real cover is not ready. */
  cover: string | null;
};

export const TIERS: Tier[] = [
  {
    id: "poket",
    name: "Edisi Poket",
    price: "Percuma",
    size: "Bacaan ringkas dan kad refleksi",
    tone: "green",
    subcopy: "Ringkas, menyentuh, mudah dibawa.",
    includes: [
      "Kad Refleksi: Red Flag, Green Flag, Luka Hati, Corak Attach",
      "Ceklis Pencetus Attach (10 soalan)",
      "7 Hari Reset, 60 saat sehari",
      "3 skrip untuk perbualan yang paling sukar minggu ini",
    ],
    seal: "/brand/seal-edisi-poket.svg",
    cover: "/ebooks/cover-poket.png",
  },
  {
    id: "membangun",
    name: "Edisi Membangun",
    price: "RM 29–49",
    size: "Panduan dan 30 soalan refleksi",
    tone: "gold",
    subcopy: "Panduan yang paling jujur dan paling mudah diikuti.",
    includes: [
      "7 bab panduan dengan situasi sebenar rakyat Malaysia",
      "Kit Refleksi: 30 soalan, satu soalan setiap muka surat",
      "5 contoh skrip untuk bercakap dengan jujur",
    ],
    seal: "/brand/seal-edisi-membangun.svg",
    cover: "/ebooks/cover-membangun.png",
  },
  {
    id: "teman-hidup",
    name: "Teman Hidup",
    price: "RM 79–149",
    size: "Buku, buku kerja, skrip dan suara",
    tone: "burgundy",
    subcopy: "Bacaan, kerja, dan skrip, teman hidup.",
    includes: [
      "Semua dalam Edisi Membangun",
      "Buku Kerja 30 Hari",
      "Skrip Bincang Hati ke Hati",
      "Nota Suara Rahimam: Audio Terapi Hati",
      "12 Kad Refleksi untuk dicetak",
    ],
    seal: "/brand/seal-teman-hidup.svg",
    cover: "/ebooks/cover-teman-hidup.png",
  },
];

// All seven chapters carry confirmed titles aligned with Edisi Membangun.
export type Chapter = { no: number; title: string; note: string; pending: boolean };

export const CHAPTERS: Chapter[] = [
  { no: 1, title: "Kenapa hubungan sakit", note: "Kenapa kita bertindak balas sebelum sempat berfikir, dan cara menenangkan diri dahulu.", pending: false },
  { no: 2, title: "Kenali corak attach kamu", note: "Cemas, mengelak atau selamat, dilihat melalui situasi rumah tangga Malaysia.", pending: false },
  { no: 3, title: "Red flag & green flag", note: "Bahasa yang sama untuk menamakan apa yang kamu rasa, lengkap dengan ceklis green flag.", pending: false },
  { no: 4, title: "Bila pertengkaran menjadi diam", note: "Empat tanda amaran Gottman dalam pertengkaran, dan cara keluar daripada kitaran diam.", pending: false },
  { no: 5, title: "Bercakap dengan jujur", note: "Cara meluahkan keperluan hati tanpa menyalahkan atau menyerang pasangan.", pending: false },
  { no: 6, title: "Bila dia tidak berubah", note: "Sempadan, menjaga diri, dan cara pergi dengan baik.", pending: false },
  { no: 7, title: "Pulih dengan perlahan", note: "Patah hati dan duka, dalam perjalanan 30 hari.", pending: false },
];

// Approved excerpts from public Threads replies to Perpustakaan Hati posts.
export const TESTIMONIALS = [
  {
    who: "@amuizrosli_",
    quote: "Kadang-kadang kita terlalu sibuk menjadi ibu bapa dan mengurus rumah tangga sampai terlupa untuk menjadi pasangan. Tanggungjawab memang penting, tapi emotional connection pun perlu dijaga.",
    url: "https://www.threads.com/@amuizrosli_/post/DfpA7_PmFAA",
  },
  {
    who: "@by_kiraaid",
    quote: '"Anak belajar menyimpan kegembiraan sendiri" tu tusuk sangat. Sbg ayah, saya pun selalu terlepas cakap "sekejap". Terima kasih atas peringatan ni 🙏',
    url: "https://www.threads.com/@by_kiraaid/post/DfqlNq_n6cs",
  },
  {
    who: "@allisse_khalisya",
    quote: "sebenarnya itu lah tujuan untuk komunikasi, berbincang cuba selesai, dengar pendapat yang boleh diambil yang boleh diletak tepi..",
    url: "https://www.threads.com/@allisse_khalisya/post/Df0c0zFnxPd",
  },
  {
    who: "@mentari_nuraura",
    quote: "MasyaALLAH..tq sharingnya Tuan..penuh makna Tuan..",
    url: "https://www.threads.com/@mentari_nuraura/post/Df6iLnDkoJw",
  },
  {
    who: "@ir_effy",
    quote: "silent treatmt is to control dan punish bukan mendidik",
    url: "https://www.threads.com/@ir_effy/post/DfuQ4xxoIpn",
  },
  {
    who: "@ema_nageeb",
    quote: "Yes u r right.. Speak a good word or remain silent.. Inn shaa Allah selamat dlm byk sudut..",
    url: "https://www.threads.com/@ema_nageeb/post/DfvYOOSkjGL",
  },
  {
    who: "@itsamoijoann",
    quote: "Benar tuan, Provokasi ni makanan nya emosi. When involve emosi akn merancakkan provokasi.",
    url: "https://www.threads.com/@itsamoijoann/post/Dfuzoo0E2by",
  },
  {
    who: "@idlinsardi",
    quote: "Kehidupan yang penuh dengan complaint dan ketidak puashatian terhadap manusia,bukanlah kehidupan seorang Muslim yang bahagia",
    url: "https://www.threads.com/@idlinsardi/post/DfrVfMXCaCg",
  },
] as const;

export const NAV = [
  { href: "#percuma", label: "Percuma" },
  { href: "#bab", label: "Bab" },
  { href: "#edisi", label: "Edisi" },
  { href: "#katalog", label: "Katalog" },
  { href: "#cara", label: "Cara" },
  { href: "#soalan", label: "Soalan" },
] as const;

export const STEPS = [
  { no: 1, title: "Ambil Edisi Poket", text: "Percuma. Tinggalkan e-mel atau nombor WhatsApp, kami hantar bila sedia." },
  { no: 2, title: "Baca 60 saat sehari", text: "Kad refleksi dan 7 Hari Reset yang muat dalam masa menunggu bas atau train." },
  { no: 3, title: "Naik bila bersedia", text: "Edisi Membangun dan Teman Hidup ada bila kamu mahu pergi lebih dalam." },
] as const;

export const FAQS = [
  { q: "Betul ke Edisi Poket percuma?", a: "Ya, percuma. Kami cuma perlukan e-mel atau nombor WhatsApp supaya boleh hantar bukunya kepada kamu." },
  { q: "Bila saya terima Edisi Poket?", a: "Kami hantar melalui e-mel atau WhatsApp sebaik sahaja bukunya sedia. Kamu tidak perlu buat apa-apa lagi." },
  { q: "Bagaimana saya bayar dan bila saya terima buku?", a: "Bayar dengan FPX, DuitNow QR atau kad. Sebaik sahaja pembayaran berjaya, pautan muat turun dihantar ke e-mel (dan WhatsApp jika diisi) dalam beberapa saat. Kamu juga boleh muat turun semula di Pustaka Saya." },
  { q: "Adakah buku ini pengganti kaunseling?", a: "Tidak. Ini bahan pendidikan dan renungan diri. Jika kamu perlu bercakap dengan seseorang sekarang, hubungi Talian HEAL 15555 atau Befrienders." },
  { q: "Bagaimana data saya dijaga?", a: "E-mel dan nombor WhatsApp disimpan di bawah PDPA Malaysia, tidak dikongsi dengan pihak lain, dan boleh dipadam atas permintaan." },
  { q: "Apa beza tiga edisi?", a: "Poket ialah permulaan yang ringkas. Membangun ialah panduan penuh dengan situasi sebenar. Teman Hidup menambah buku kerja, skrip dan nota suara." },
] as const;
