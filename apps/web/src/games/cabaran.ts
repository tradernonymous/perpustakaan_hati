export type CabaranDay = { day: number; prompt: string; action: string };

export const CABARAN_TITLE = "7 Hari Cabaran Pulih Hati";

export const CABARAN_DAYS: CabaranDay[] = [
  { day: 1, prompt: "Kenapa kau buka buku ini, hari ini, bukan semalam?", action: "Tulis satu ayat." },
  { day: 2, prompt: "Apa corak berulang yang kau lihat dalam hubungan kau?", action: "Tulis satu contoh kecil." },
  { day: 3, prompt: "Apa yang kau rasa bila dia belum balas?", action: "Tulis rasa, kemudian fakta, jangan campurkan." },
  { day: 4, prompt: "Satu boundary yang kau tahu kau perlukan.", action: "Tulis dalam bentuk 'Aku tidak boleh...'." },
  { day: 5, prompt: "Kata yang paling sukar untuk kau kata, tetapi sebenarnya kau perlu kata.", action: "Tulis apa adanya." },
  { day: 6, prompt: "Satu perkara kecil yang kau hargai hari ini.", action: "Tulis tiga perkara kecil." },
  { day: 7, prompt: "Apa yang kau bawa ke hadapan dari minggu ini?", action: "Tulis satu ayat yang akan kau baca semula bila pagi terasa berat." },
];

export function cabaranPrompt(day: number): CabaranDay {
  const i = Math.min(Math.max(1, day), CABARAN_DAYS.length);
  return CABARAN_DAYS[i - 1];
}
