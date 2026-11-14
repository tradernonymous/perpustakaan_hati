import { TIERS, quoteForType, type SessionType } from "@/src/games/booking";
import { getBookingStore } from "@/src/server/instance";
import { createRateLimiter } from "@/src/server/ratelimit";
import { EMAIL, MY_MOBILE } from "@/src/server/validate";

export const runtime = "nodejs";

const MAX_BODY_BYTES = 8192;
const limiter = createRateLimiter(6, 60_000);

const json = (body: unknown, status: number) => Response.json(body, { status });

/** Accepts counselling session booking requests and persists them on the DATA_DIR volume. */
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

  if (typeof body !== "object" || body === null) return json({ error: "Permintaan tidak sah." }, 400);
  const raw = body as Record<string, unknown>;

  if (typeof raw.website === "string" && raw.website.length > 0) {
    return json({ ok: true, id: 0 }, 201);
  }

  const name = typeof raw.name === "string" ? raw.name.trim() : "";
  const email = typeof raw.email === "string" ? raw.email.trim().toLowerCase() : "";
  const rawPhone = typeof raw.phone === "string" ? raw.phone.replace(/[\s-]/g, "") : "";
  const sessionType = typeof raw.sessionType === "string" ? (raw.sessionType as SessionType) : null;
  const notes = typeof raw.notes === "string" ? raw.notes.trim().slice(0, 1500) : "";

  if (name.length < 2 || name.length > 100) {
    return json({ error: "Sila isi nama panggilan atau nama penuh." }, 400);
  }
  if (!email || email.length > 254 || !EMAIL.test(email)) {
    return json({ error: "Alamat e-mel tidak sah." }, 400);
  }
  const phoneMatch = MY_MOBILE.exec(rawPhone);
  if (!phoneMatch) {
    return json({ error: "Nombor WhatsApp mesti nombor mudah alih Malaysia, contoh 012-345 6789." }, 400);
  }
  if (!sessionType || !TIERS.includes(sessionType)) {
    return json({ error: "Sila pilih jenis sesi yang sah." }, 400);
  }
  if (raw.consent !== true) {
    return json({ error: "Sila setuju dengan notis privasi (PDPA) untuk teruskan." }, 400);
  }

  const quoteSen = quoteForType(sessionType);
  const saved = getBookingStore().add({
    name,
    email,
    phone: `+60${phoneMatch[1]}`,
    sessionType,
    quoteSen,
    notes: notes || null,
  });

  return json({ ok: true, id: saved.id, quoteSen }, 201);
}
