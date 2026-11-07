import { startCheckout, validateCheckout } from "@/src/server/checkout";
import { getOrders } from "@/src/server/instance";
import { createRateLimiter } from "@/src/server/ratelimit";
import { siteUrl } from "@/src/site";

export const runtime = "nodejs";

const limiter = createRateLimiter(10, 60_000);
const json = (body: unknown, status: number) => Response.json(body, { status });

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  if (!limiter.hit(ip)) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar." }, 429);

  const text = await req.text();
  if (text.length > 4096) return json({ error: "Permintaan terlalu besar." }, 413);
  let body: unknown;
  try {
    body = JSON.parse(text);
  } catch {
    return json({ error: "Permintaan tidak sah." }, 400);
  }

  const v = validateCheckout(body);
  if (!v.ok) return json({ error: v.error }, 400);

  const r = await startCheckout(v.value, { orders: getOrders(), env: process.env, baseUrl: siteUrl() });
  return r.ok ? json({ url: r.url }, 201) : json({ error: r.error }, r.status);
}
