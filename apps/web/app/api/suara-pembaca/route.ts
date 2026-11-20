import { createRateLimiter } from "@/src/server/ratelimit";
import { saveReaderFeedback } from "@/src/server/reader-feedback";
import { EMAIL } from "@/src/server/validate";
import { siteUrl } from "@/src/site";

const limiter = createRateLimiter(5, 60_000);
const sources = new Set(["threads", "ebook", "lain"]);

export async function POST(request: Request) {
  if (request.headers.get("origin") !== new URL(siteUrl()).origin) {
    return new Response(null, { status: 403 });
  }
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  if (!limiter.hit(ip)) return new Response("Terlalu banyak cubaan. Cuba lagi nanti.", { status: 429 });
  if (!request.headers.get("content-type")?.startsWith("application/x-www-form-urlencoded")) {
    return new Response(null, { status: 415 });
  }
  const body = await request.text();
  if (body.length > 6000) return new Response(null, { status: 413 });
  const form = new URLSearchParams(body);
  const name = form.get("name")?.trim() ?? "";
  const email = form.get("email")?.trim().toLowerCase() ?? "";
  const source = form.get("source") ?? "";
  const message = form.get("message")?.trim() ?? "";
  const redirect = (status: "sent" | "invalid") => new Response(null, {
    status: 303, headers: { location: `/?suara=${status}#pembaca`, "cache-control": "no-store" },
  });
  if (form.get("website")) return redirect("sent");
  if (name.length > 80 || email.length > 254 || (email && !EMAIL.test(email)) ||
      !sources.has(source) || message.length < 12 || message.length > 800 || form.get("permission") !== "on") {
    return redirect("invalid");
  }
  saveReaderFeedback({ name, email, source, message });
  return redirect("sent");
}
