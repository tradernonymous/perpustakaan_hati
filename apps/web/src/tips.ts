export const TIPS_PATH = "/baca/tips-psikologi-suami-isteri";
export const TIPS_PAGE_COUNT = 10;

export function tipsPage(value: unknown): number | null {
  if (typeof value !== "string" && typeof value !== "number") return null;
  const page = Number(value);
  return Number.isInteger(page) && page >= 1 && page <= TIPS_PAGE_COUNT ? page : null;
}
