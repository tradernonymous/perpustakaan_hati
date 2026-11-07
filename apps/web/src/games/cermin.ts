export type Question = {
  id: string;
  text: string;
  options: { label: string; score: number }[];
};

export const QUESTIONS: Question[] = [
  {
    id: "q1",
    text: "Bila ada masalah, kau cenderung untuk...",
    options: [
      { label: "Bercakap segera", score: 2 },
      { label: "Fikir dulu", score: 1 },
      { label: "Diam dan elak", score: 0 },
    ],
  },
  {
    id: "q2",
    text: "Kau rasa paling selamat bila...",
    options: [
      { label: "Didengar tanpa dibetulkan", score: 2 },
      { label: "Dibantu cari jalan keluar", score: 1 },
      { label: "Dibiarkan sendiri", score: 0 },
    ],
  },
  {
    id: "q3",
    text: "Dalam bergaduh, kau paling kerap...",
    options: [
      { label: "Minta maaf dahulu", score: 2 },
      { label: "Terangkan dahulu", score: 1 },
      { label: "Menang dahulu", score: 0 },
    ],
  },
  {
    id: "q4",
    text: "Kau menunjukkan cinta melalui...",
    options: [
      { label: "Kata-kata", score: 2 },
      { label: "Tindakan", score: 1 },
      { label: "Masa", score: 0 },
    ],
  },
  {
    id: "q5",
    text: "Bila kau takut kehilangan, kau...",
    options: [
      { label: "Bercakap tentang ketakutan", score: 2 },
      { label: "Menjaga jarak", score: 1 },
      { label: "Melekat lebih kuat", score: 0 },
    ],
  },
];

export function scoreCermin(answers: number[]): number {
  return answers.reduce((sum, a) => sum + a, 0);
}

export type Verdict = "cermin-clear" | "warm-up" | "need-care";

export function verdictFor(score: number): Verdict {
  if (score >= 8) return "cermin-clear";
  if (score >= 4) return "warm-up";
  return "need-care";
}
