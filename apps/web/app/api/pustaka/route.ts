import { EMAIL } from "@/src/server/validate";
import { getOrders } from "@/src/server/instance";
import { requestLoginLink } from "@/src/server/library";
import { createRateLimiter } from "@/src/server/ratelimit";

export const runtime = "nodejs";

const byIp = createRateLimiter(5, 60_000);
const byEmail = createRateLimiter(3, 10 * 60_000);
const SAME_ANSWER = { ok: true, message: "Jika e-mel itu ada pesanan, kami sudah hantar pautan ke peti masuk kamu." };

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  if (!byIp.hit(ip)) return Response.json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar." }, { status: 429 });

  const text = await req.text();
  let email = "";
  try {
    const b = JSON.parse(text.length > 2048 ? "{}" : text) as { email?: unknown };
    email = typeof b.email === "string" ? b.email.trim().toLowerCase() : "";
  } catch {
    /* fall through to the invalid-address answer */
  }
  if (!email || email.length > 254 || !EMAIL.test(email)) return Response.json({ error: "Sila isi alamat e-mel yang sah." }, { status: 400 });

  if (byEmail.hit(email)) {
    await requestLoginLink(email, { orders: getOrders(), env: process.env }).catch(() => false);
  }
  return Response.json(SAME_ANSWER, { status: 200 });
}
