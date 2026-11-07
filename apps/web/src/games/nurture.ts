export type NurtureDay = { day: number; subject: string; body: string };

export const NURTURE_DAYS: NurtureDay[] = [
  {
    day: 1,
    subject: "Selamat datang ke Perpustakaan Hati",
    body: "Terima kasih kerana memuat turun Edisi Poket. Baca satu kad refleksi hari ini, dan perasan apa yang berubah.",
  },
  {
    day: 2,
    subject: "Kad Refleksi hari ini",
    body: "Hari ini, tulis satu perkataan yang menggambarkan keadaan kamu minggu ini. Satu perkataan sahaja.",
  },
  {
    day: 3,
    subject: "Ceklis Pencetus Attach",
    body: "Cuba ceklis 10 soalan. Jawap dengan jujur, dan lihat corak mana yang paling jelas.",
  },
  {
    day: 4,
    subject: "7 Hari Reset — Hari 1",
    body: "Hari pertama reset: tulis satu perkara kecil yang boleh kamu buat hari ini untuk diri sendiri.",
  },
  {
    day: 5,
    subject: "Skrip untuk perbualan yang sukar",
    body: "Cuba satu skrip dari Edisi Poket. Jangan tunggu sempurna. Cuba saja, dan perasan apa yang berlaku.",
  },
  {
    day: 6,
    subject: "Adakah kamu bersedia untuk lebih?",
    body: "Edisi Membangun ada untuk kamu yang mahu faham dengan lebih mendalam. Lihat halaman edisi di laman kami bila kamu bersedia.",
  },
  {
    day: 7,
    subject: "Teman Hidup — pemium bundle",
    body: "Teman Hidup ialah continuity: buku kerja 30 hari, skrip, nota suara, dan kad refleksi. Untuk kamu yang mahu ditemani setiap hari.",
  },
];

export function nurtureMessage(day: number): NurtureDay {
  const i = Math.min(Math.max(1, day), NURTURE_DAYS.length);
  return NURTURE_DAYS[i - 1];
}
