import type { Env } from "../env";
import { createHmac, timingSafeEqual } from "node:crypto";

export type BillplzConfig = { apiKey: string; collectionId: string; xSignatureKey: string; baseUrl: string };

export function billplzConfig(env: Env = process.env): BillplzConfig | null {
  const { BILLPLZ_API_KEY: apiKey, BILLPLZ_COLLECTION_ID: collectionId, BILLPLZ_X_SIGNATURE: xSignatureKey } = env;
  if (!apiKey || !collectionId || !xSignatureKey) return null;
  return { apiKey, collectionId, xSignatureKey, baseUrl: env.BILLPLZ_BASE_URL ?? "https://www.billplz.com" };
}

export type BillInput = {
  orderId: string; amountSen: number; email: string; phone: string | null;
  description: string; callbackUrl: string; redirectUrl: string;
};

type Fetch = typeof fetch;

/** Hosted Billplz page: shows FPX online banking and DuitNow QR (enable both on the collection). */
export async function createBill(cfg: BillplzConfig, i: BillInput, fetchFn: Fetch = fetch): Promise<{ ref: string; url: string }> {
  const body = new URLSearchParams({
    collection_id: cfg.collectionId,
    email: i.email,
    name: i.email.split("@")[0] || "Pembaca",
    amount: String(i.amountSen),
    description: i.description,
    callback_url: i.callbackUrl,
    redirect_url: i.redirectUrl,
    reference_1_label: "Order",
    reference_1: i.orderId,
  });
  if (i.phone) body.set("mobile", i.phone);
  const res = await fetchFn(`${cfg.baseUrl}/api/v3/bills`, {
    method: "POST",
    headers: {
      authorization: "Basic " + Buffer.from(`${cfg.apiKey}:`).toString("base64"),
      "content-type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });
  if (!res.ok) throw new Error(`Billplz bill failed (${res.status})`);
  const data = (await res.json()) as { id?: string; url?: string };
  if (!data.id || !data.url) throw new Error("Billplz bill response missing id/url");
  return { ref: data.id, url: data.url };
}

/** Billplz X-Signature: HMAC-SHA256 of the "key+value" pairs, sorted, joined with "|". */
export function verifyBillplzCallback(params: Record<string, string>, key: string): boolean {
  const sig = params.x_signature;
  if (!key || !sig) return false;
  const source = Object.entries(params)
    .filter(([k]) => k !== "x_signature")
    .map(([k, v]) => k + v)
    .sort()
    .join("|");
  const expected = createHmac("sha256", key).update(source).digest();
  const given = Buffer.from(sig, "hex");
  return given.length === expected.length && timingSafeEqual(given, expected);
}
