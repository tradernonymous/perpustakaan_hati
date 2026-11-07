export type SessionType = "clarity" | "couples" | "panel";

export const TIERS: SessionType[] = ["clarity", "couples", "panel"];

export function quoteForType(type: SessionType): number {
  if (type === "clarity") return 15000;
  if (type === "couples") return 35000;
  return 25000;
}

export type BriefInput = { name: string; quiz: string; books: string[]; intake: string };

export function createBrief(input: BriefInput): { summary: string } {
  const summary = `Pre-session brief for ${input.name}. Attachment quiz: ${input.quiz}. Purchased: ${input.books.join(", ")||"none"}. Intake: ${input.intake}`;
  return { summary };
}
