import { createHash } from "node:crypto";

export const VOUCHER_SEN = 1500;
export const FREE_CARD_UNLOCK = true;

export function makeReferralCode(email: string): string {
  const normalized = email.trim().toLowerCase();
  const hash = createHash("sha256").update(normalized).digest("hex").slice(0, 8);
  return `HATI-${hash}`;
}

export type EntryInput = { downloaded: boolean; shared: boolean; invited: number };

export function entriesFor(input: EntryInput): number {
  const n = (input.downloaded ? 1 : 0) + (input.shared ? 1 : 0) + Math.max(0, input.invited);
  return Math.max(0, n);
}
