import type { Env } from "./env";
// Sellable products. The public site shows price ranges; the exact amount charged
// comes from env (in sen) so Jack can set it without a code change.
export type ProductId = "membangun" | "teman-hidup";

export type Product = { id: ProductId; name: string; envKey: string; defaultSen: number; file: string };

export const PRODUCTS: Record<ProductId, Product> = {
  membangun: { id: "membangun", name: "Edisi Membangun", envKey: "PRICE_MEMBANGUN_SEN", defaultSen: 2900, file: "edisi-membangun.pdf" },
  "teman-hidup": { id: "teman-hidup", name: "Teman Hidup", envKey: "PRICE_TEMAN_HIDUP_SEN", defaultSen: 7900, file: "teman-hidup.pdf" },
};

export function isProductId(v: unknown): v is ProductId {
  return typeof v === "string" && Object.prototype.hasOwnProperty.call(PRODUCTS, v);
}

function envSen(key: string, fallback: number, env: Env): number {
  const n = Number(env[key]);
  return Number.isInteger(n) && n >= 100 ? n : fallback;
}

export function priceSen(id: ProductId, env: Env = process.env): number {
  const p = PRODUCTS[id];
  return envSen(p.envKey, p.defaultSen, env);
}

/** One-click add-on shown on the Edisi Membangun checkout: adds Teman Hidup. */
export function bumpPriceSen(env: Env = process.env): number {
  return envSen("BUMP_TEMAN_HIDUP_SEN", 5000, env);
}

export type Cart = { product: ProductId; bump: boolean };

export function cartItems(c: Cart): ProductId[] {
  return c.bump && c.product === "membangun" ? ["membangun", "teman-hidup"] : [c.product];
}

export function cartTotalSen(c: Cart, env: Env = process.env): number {
  const base = priceSen(c.product, env);
  return c.bump && c.product === "membangun" ? base + bumpPriceSen(env) : base;
}

export function formatRM(sen: number): string {
  return `RM ${(sen / 100).toFixed(2)}`;
}
