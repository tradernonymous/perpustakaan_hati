import { activeReader } from "@/src/server/reader-session";
import { setTipsBookmark } from "@/src/server/reader-bookmark";
import { siteUrl } from "@/src/site";
import { TIPS_PATH, tipsPage } from "@/src/tips";

export async function POST(request: Request) {
  const origin = request.headers.get("origin");
  if (origin !== new URL(siteUrl()).origin) return new Response(null, { status: 403 });
  const email = await activeReader();
  if (!email) return new Response(null, { status: 401 });
  const form = await request.formData();
  const page = tipsPage(form.get("halaman"));
  const reset = form.get("action") === "reset";
  if (!page && !reset) return new Response(null, { status: 400 });
  setTipsBookmark(email, reset ? null : page);
  return new Response(null, { status: 303, headers: {
    location: reset ? "/pustaka" : `${TIPS_PATH}?halaman=${page}&disimpan=1`,
    "cache-control": "no-store",
  } });
}
