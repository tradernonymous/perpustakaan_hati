import { PRODUCTS } from "../catalog";
import type { Env } from "../env";
import { emailSubject, emailText, whatsappLinkText, type Link } from "./messages";
import type { Order, Orders } from "./orders";
import { signToken } from "./tokens";

export const DOWNLOAD_TTL_SECONDS = 7 * 24 * 3600;
// Delivery has a 10 second promise to the buyer, so each channel gets 8 seconds at most.
const DEFAULT_TIMEOUT_MS = 8000;

export type DeliverDeps = { orders: Orders; env: Env; fetchFn?: typeof fetch; now?: () => number; timeoutMs?: number };
export type ChannelResult = "ok" | "error" | "skipped";
export type DeliverResult = { email: ChannelResult; whatsapp: ChannelResult };

export function downloadLinks(order: Order, env: Env, now = Math.floor(Date.now() / 1000), ttl = DOWNLOAD_TTL_SECONDS): Link[] {
  const secret = env.DOWNLOAD_SECRET;
  if (!secret) throw new Error("DOWNLOAD_SECRET is not set");
  const base = (env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
  return order.items.map((p) => ({
    name: PRODUCTS[p].name,
    url: `${base}/muat-turun/${signToken({ k: "dl", o: order.id, p }, secret, ttl, now)}`,
  }));
}

async function withTimeout(fetchFn: typeof fetch, url: string, init: RequestInit, ms: number): Promise<Response> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);
  try {
    return await fetchFn(url, { ...init, signal: ctl.signal });
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Sends the download links by e-mail (Resend) and WhatsApp (Cloud API) at the same time.
 * Never throws for a channel failure: the result is recorded so Jack can resend by hand.
 */
export async function deliverOrder(order: Order, d: DeliverDeps): Promise<DeliverResult> {
  const fetchFn = d.fetchFn ?? fetch;
  const now = d.now ? d.now() : Math.floor(Date.now() / 1000);
  const ms = d.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const links = downloadLinks(order, d.env, now);
  const base = (d.env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");

  const run = async (channel: "email" | "whatsapp", job: (() => Promise<Response>) | null): Promise<ChannelResult> => {
    if (!job) return "skipped";
    try {
      const res = await job();
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      d.orders.recordDelivery(order.id, channel, "ok");
      return "ok";
    } catch (e) {
      d.orders.recordDelivery(order.id, channel, "error", e instanceof Error ? e.message : "unknown");
      return "error";
    }
  };

  const { RESEND_API_KEY, EMAIL_FROM, WHATSAPP_TOKEN, WHATSAPP_PHONE_ID } = d.env;
  const email = RESEND_API_KEY && EMAIL_FROM
    ? () => withTimeout(fetchFn, "https://api.resend.com/emails", {
        method: "POST",
        headers: { authorization: `Bearer ${RESEND_API_KEY}`, "content-type": "application/json" },
        body: JSON.stringify({ from: EMAIL_FROM, to: [order.email], subject: emailSubject(), text: emailText(links, `${base}/pustaka`) }),
      }, ms)
    : null;
  const phone = order.phone;
  const whatsapp = WHATSAPP_TOKEN && WHATSAPP_PHONE_ID && phone
    ? () => withTimeout(fetchFn, `https://graph.facebook.com/v21.0/${WHATSAPP_PHONE_ID}/messages`, {
        method: "POST",
        headers: { authorization: `Bearer ${WHATSAPP_TOKEN}`, "content-type": "application/json" },
        // Business-initiated messages must use an approved template with one body variable.
        body: JSON.stringify({
          messaging_product: "whatsapp",
          to: phone.replace(/^\+/, ""),
          type: "template",
          template: {
            name: d.env.WHATSAPP_TEMPLATE ?? "pesanan_siap",
            language: { code: "ms" },
            components: [{ type: "body", parameters: [{ type: "text", text: whatsappLinkText(links).replace(/\n/g, " | ") }] }],
          },
        }),
      }, ms)
    : null;

  const [e, w] = await Promise.all([run("email", email), run("whatsapp", whatsapp)]);
  return { email: e, whatsapp: w };
}
