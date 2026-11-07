export type CardCategory = "red" | "green" | "luka";

export type Card = {
  id: string;
  category: CardCategory;
  title: string;
  prompt: string;
};

export const CARDS: Card[] = [
  { id: "red-1", category: "red", title: "Red Flag", prompt: "Apa corak berulang yang kau lihat, bukan satu insiden?" },
  { id: "red-2", category: "red", title: "Gaslighting", prompt: "Bila kau rasa kau disuruh meragui ingatan sendiri?" },
  { id: "red-3", category: "red", title: "Silent Treatment", prompt: "Bila diam digunakan sebagai hukuman, bukan untuk tenang?" },
  { id: "red-4", category: "red", title: "Intimidation", prompt: "Apa yang kau rasa bila kau takut bercakap?" },
  { id: "green-1", category: "green", title: "Green Flag", prompt: "Apa response yang buat kau rasa selamat?" },
  { id: "green-2", category: "green", title: "Repair", prompt: "Bagaimana kalian repair selepas bergaduh?" },
  { id: "green-3", category: "green", title: "Dengar", prompt: "Bila kau rasa benar-benar didengar?" },
  { id: "green-4", category: "green", title: "Boundary Sihat", prompt: "Boundary apa yang membuat kau rasa dihormati?" },
  { id: "luka-1", category: "luka", title: "Luka Hati", prompt: "Luka apa yang masih kau bawa, dan apa yang kau perlukan?" },
  { id: "luka-2", category: "luka", title: "Attach", prompt: "Corak attach apa yang paling jelas minggu ini?" },
  { id: "luka-3", category: "luka", title: "Kesunyian", prompt: "Bila kau rasa sendirian walaupun dia ada?" },
  { id: "luka-4", category: "luka", title: "Pulih", prompt: "Apa satu langkah kecil yang kau boleh ambil hari ini?" },
];

export function drawCard(index: number): Card {
  const i = ((index % CARDS.length) + CARDS.length) % CARDS.length;
  return CARDS[i];
}

export const isRed = (c: Card) => c.category === "red";
export const isGreen = (c: Card) => c.category === "green";
export const isLuka = (c: Card) => c.category === "luka";

export function bingoMarks(ids: string[]): string[] {
  return ids.filter((id) => CARDS.some((c) => c.id === id));
}

export function scoreBingo(marks: string[], row: string[]): number {
  const set = new Set(marks);
  return row.every((id) => set.has(id)) ? 1 : 0;
}
