import { createRateLimiter } from "@/src/server/ratelimit";
import { getStore } from "@/src/server/instance";
import { validateSubscribe } from "@/src/server/validate";

export const runtime = "nodejs";

const MAX_BODY_BYTES = 4096;
const limiter = createRateLimiter(10, 60_000);

const json = (body: unknown, status: number) => Response.json(body, { status });

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  if (!limiter.hit(ip)) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar." }, 429);

  const text = await req.text();
  if (text.length > MAX_BODY_BYTES) return json({ error: "Permintaan terlalu besar." }, 413);

  let body: unknown;
  try {
    body = JSON.parse(text);
  } catch {
    return json({ error: "Permintaan tidak sah." }, 400);
  }

  const result = validateSubscribe(body);
  if (!result.ok) return json({ error: result.error }, 400);

  // Honeypot hit: look successful to the bot, store nothing.
  // Duplicates also return the same response so the form never reveals who is subscribed.
  if (!result.bot) getStore().add(result.value);
  return json({ ok: true }, 201);
}
