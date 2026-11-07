import { describe, expect, it } from "vitest";
import { bumpPriceSen, cartItems, cartTotalSen, formatRM, isProductId, priceSen } from "@/src/catalog";

describe("catalog", () => {
  it("uses safe defaults inside the public price ranges", () => {
    expect(priceSen("membangun", {})).toBe(2900);
    expect(priceSen("teman-hidup", {})).toBe(7900);
  });
  it("reads prices from env in sen and ignores junk", () => {
    expect(priceSen("membangun", { PRICE_MEMBANGUN_SEN: "3900" })).toBe(3900);
    expect(priceSen("membangun", { PRICE_MEMBANGUN_SEN: "abc" })).toBe(2900);
    expect(priceSen("membangun", { PRICE_MEMBANGUN_SEN: "-5" })).toBe(2900);
    expect(priceSen("membangun", { PRICE_MEMBANGUN_SEN: "12.5" })).toBe(2900);
  });
  it("order bump adds Teman Hidup only on Edisi Membangun", () => {
    expect(cartItems({ product: "membangun", bump: true })).toEqual(["membangun", "teman-hidup"]);
    expect(cartItems({ product: "teman-hidup", bump: true })).toEqual(["teman-hidup"]);
    expect(cartTotalSen({ product: "membangun", bump: true }, {})).toBe(2900 + bumpPriceSen({}));
    expect(cartTotalSen({ product: "teman-hidup", bump: true }, {})).toBe(7900);
    expect(cartTotalSen({ product: "membangun", bump: false }, {})).toBe(2900);
  });
  it("validates ids and formats money", () => {
    expect(isProductId("membangun")).toBe(true);
    expect(isProductId("poket")).toBe(false);
    expect(isProductId("__proto__")).toBe(false);
    expect(formatRM(2900)).toBe("RM 29.00");
  });
});
