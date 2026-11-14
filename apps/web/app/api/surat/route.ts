import { acceptsSurat, anonymize } from "@/src/games/surat";
import { getSuratStore } from "@/src/server/instance";
import { createRateLimiter } from "@/src/server/ratelimit";

export const runtime = "nodejs";

const MAX_BODY_BYTES = 8192;
const MAX_DILEMMA_CHARS = 3000;
const limiter = createRateLimiter(6, 60_000);

const json = (body: unknown, status: number) => Response.json(body, { status });

/** Accepts anonymous Surat Hati letters, strips the sender name, and saves to SQLite. */
export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  if (!limiter.hit(ip)) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar." }, 429);

  const text = await req.text();
  if (text.length > MAX_BODY_BYTES) return json({ error: "Surat terlalu panjang." }, 413);

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

  const name = typeof raw.name === "string" ? raw.name.trim().slice(0, 80) : "";
  const dilemma = typeof raw.dilemma === "string" ? raw.dilemma.trim() : "";

  if (!acceptsSurat({ dilemma })) {
    return json({ error: "Sila tulis luahan sekurang-kurangnya beberapa perkataan." }, 400);
  }
  if (dilemma.length > MAX_DILEMMA_CHARS) {
    return json({ error: "Luahan terlalu panjang. Had ialah 3000 aksara." }, 400);
  }

  const anonymizedDilemma = name ? anonymize(name, dilemma) : dilemma;
  const consentPublish = raw.consentPublish !== false;
  const saved = getSuratStore().add({
    alias: name || null,
    anonymizedDilemma,
    consentPublish,
  });

  return json({ ok: true, id: saved.id }, 201);
}
