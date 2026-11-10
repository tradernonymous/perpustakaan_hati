import { createHash, timingSafeEqual } from "node:crypto";
import { issueAdminSession } from "@/src/server/auth";
import {
  clearedStateCookie,
  exchangeCode,
  facebookConfig,
  FACEBOOK_STATE_COOKIE,
  FacebookError,
  isAllowed,
  profile,
  readCookie,
  secureCookie,
  type FacebookConfig,
} from "@/src/server/facebook";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function sameState(a: string, b: string): boolean {
  const ha = createHash("sha256").update(a).digest();
  const hb = createHash("sha256").update(b).digest();
  return timingSafeEqual(ha, hb);
}

function page(config: FacebookConfig | null, status: number, title: string, body: string): Response {
  const headers = new Headers({
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
  });
  if (config) headers.append("Set-Cookie", clearedStateCookie(config));

  const html = `<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title} — Perpustakaan Hati</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f7f4ea;color:#12251b;font:16px/1.6 system-ui,sans-serif;padding:24px}
main{width:min(560px,100%);border:1px solid #d2c4a8;border-radius:16px;padding:32px;background:#fffdf6;box-shadow:0 24px 60px rgb(60 45 20/.18)}
h1{margin:0 0 12px;font:600 26px/1.25 Georgia,serif;color:#123d2a}p{margin:0 0 10px;color:#4f5f53}
code{color:#7a5a22}a{display:inline-block;margin-top:16px;padding:10px 18px;border-radius:999px;background:#3f9167;color:#f7f4ea;font-weight:600;text-decoration:none}
</style></head><body><main><h1>${title}</h1>${body}<a href="/admin">Ke halaman admin</a></main></body></html>`;
  return new Response(html, { status, headers });
}

/** GET /api/auth/facebook/callback — verifies state, checks the allowlist, opens a session. */
export async function GET(req: Request) {
  const config = facebookConfig();
  if (!config) return page(null, 503, "Facebook belum dikonfigurasi", "<p>Set <code>FACEBOOK_APP_ID</code> dan <code>FACEBOOK_APP_SECRET</code> dahulu.</p>");

  const url = new URL(req.url);
  if (url.searchParams.get("error")) {
    return page(config, 400, "Kebenaran dibatalkan", "<p>Tiada sesi dibuka. Cuba masuk semula bila sedia.</p>");
  }

  const state = url.searchParams.get("state") ?? "";
  const cookieState = readCookie(req.headers.get("cookie"), FACEBOOK_STATE_COOKIE);
  if (!state || !cookieState || !sameState(state, cookieState)) {
    return page(config, 400, "Sesi tidak sah", "<p>Pautan ini tamat tempoh atau dibuka dari pelayar lain. Mulakan semula dari halaman admin.</p>");
  }

  const code = url.searchParams.get("code") ?? "";
  if (!code) return page(config, 400, "Kod tiada", "<p>Facebook tidak memulangkan kod kebenaran.</p>");

  try {
    const accessToken = await exchangeCode(config, code);
    const me = await profile(accessToken);
    if (!isAllowed(config, me.id)) {
      // A successful Facebook login is not authorisation: only the allowlist opens the door.
      return page(config, 403, "Akaun ini bukan admin", "<p>Facebook mengenali akaun ini, tetapi ia tiada dalam senarai admin. Tiada sesi dibuka.</p>");
    }
    return new Response(null, {
      status: 303,
      headers: {
        Location: "/admin",
        "Set-Cookie": `${issueAdminSession(process.env.ADMIN_TOKEN ?? "", { secure: secureCookie(config.redirectUri) })}, ${clearedStateCookie(config)}`,
        "Cache-Control": "no-store",
      },
    });
  } catch (e) {
    const detail = e instanceof FacebookError ? e.message : "Ralat tidak dijangka.";
    return page(config, 502, "Sambungan gagal", `<p>${detail}</p><p>Tiada sesi dibuka. Cuba semula.</p>`);
  }
}