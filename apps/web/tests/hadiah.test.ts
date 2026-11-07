import { describe, expect, it } from "vitest";
import { makeReferralCode, entriesFor, VOUCHER_SEN, FREE_CARD_UNLOCK } from "@/src/games/hadiah";

describe("Hadiah Hati", () => {
  it("makeReferralCode is deterministic for a given email", () => {
    expect(makeReferralCode("aina@example.com")).toBe(makeReferralCode("aina@example.com"));
  });
  it("makeReferralCode differs for different emails", () => {
    expect(makeReferralCode("a@b.co")).not.toBe(makeReferralCode("c@d.co"));
  });
  it("entriesFor counts download + share + referral", () => {
    expect(entriesFor({ downloaded: true, shared: true, invited: 3 })).toBe(5);
  });
  it("entriesFor floors at zero", () => {
    expect(entriesFor({ downloaded: false, shared: false, invited: 0 })).toBe(0);
  });
  it("VOUCHER_SEN is RM15-20 range", () => {
    expect(VOUCHER_SEN).toBeGreaterThanOrEqual(1500);
    expect(VOUCHER_SEN).toBeLessThanOrEqual(2000);
  });
  it("FREE_CARD_UNLOCK is true for everyone", () => {
    expect(FREE_CARD_UNLOCK).toBe(true);
  });
});
