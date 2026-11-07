import { PRODUCTS } from "../catalog";
import type { Env } from "../env";
import { downloadLinks } from "./fulfil";
import { loginEmailText } from "./messages";
import type { Orders } from "./orders";
import { signToken, verifyToken } from "./tokens";

const LOGIN_TTL = 30 * 60;
const LIB_LINK_TTL = 60 * 60;

type Deps = { orders: Orders; env: Env; fetchFn?: typeof fetch };

/** Returns true if a mail was sent. Callers must show the same message either way, so the form never reveals who has bought. */
export async function requestLoginLink(email: string, d: Deps): Promise<boolean> {
  const secret = d.env.DOWNLOAD_SECRET;
  const { RESEND_API_KEY, EMAIL_FROM } = d.env;
  if (!secret || !RESEND_API_KEY || !EMAIL_FROM) return false;
  const address = email.trim().toLowerCase();
  if (d.orders.listPaidByEmail(address).length === 0) return false;

  const base = (d.env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
  const url = `${base}/pustaka?t=${signToken({ k: "lib", e: address }, secret, LOGIN_TTL)}`;
  const res = await (d.fetchFn ?? fetch)("https://api.resend.com/emails", {
    method: "POST",
    headers: { authorization: `Bearer ${RESEND_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ from: EMAIL_FROM, to: [address], subject: "Pautan Pustaka Saya", text: loginEmailText(url) }),
  });
  return res.ok;
}

export type Library = { email: string; items: { name: string; url: string; orderRef: string }[] };

export function libraryFor(token: string, d: Pick<Deps, "orders" | "env">): Library | null {
  const secret = d.env.DOWNLOAD_SECRET;
  if (!secret) return null;
  const t = verifyToken(token, secret);
  if (!t || t.k !== "lib" || typeof t.e !== "string") return null;

  const items: Library["items"] = [];
  const seen = new Set<string>();
  for (const order of d.orders.listPaidByEmail(t.e)) {
    const links = downloadLinks(order, d.env, undefined, LIB_LINK_TTL);
    order.items.forEach((p, i) => {
      if (seen.has(p)) return;
      seen.add(p);
      items.push({ name: PRODUCTS[p].name, url: links[i].url, orderRef: order.id.slice(0, 8) });
    });
  }
  return { email: t.e, items };
}
