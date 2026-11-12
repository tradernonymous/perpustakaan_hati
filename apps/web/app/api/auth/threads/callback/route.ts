import { createHash, timingSafeEqual } from "node:crypto";
import { getThreadsStore } from "@/src/server/instance";
import {
  clearedStateCookie,
  exchangeCode,
  readCookie,
  threadsConfig,
  threadsProfile,
  THREADS_STATE_COOKIE,
  ThreadsError,
  type ThreadsConfig,
} from "@/src/server/threads";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function sameState(a: string, b: string): boolean {
  const ha = createHash("sha256").update(a).digest();
  const hb = createHash("sha256").update(b).digest();
  return timingSafeEqual(ha, hb);
}

function page(config: ThreadsConfig | null, status: number, title: string, body: string): Response {
  const headers = new Headers({
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
  });
  if (config) headers.append("Set-Cookie", clearedStateCookie(config));

  const html = `<!doctype html><html lang="ms"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title}, Perpustakaan Hati</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#07140d;color:#e6e2da;font:16px/1.6 system-ui,sans-serif;padding:24px}
main{width:min(560px,100%);border:1px solid rgb(201 168 106/.45);border-radius:16px;padding:32px;background:#0d2117;box-shadow:0 24px 60px rgb(0 0 0/.5)}
h1{margin:0 0 12px;font:600 26px/1.25 Georgia,serif;color:#fdfee6}p{margin:0 0 10px;color:#a7d3b6}
code{color:#e9cea2}a{display:inline-block;margin-top:16px;padding:10px 18px;border-radius:999px;background:#3f9167;color:#07140d;font-weight:600;text-decoration:none}
</style></head><body><main><h1>${title}</h1>${body}<a href="/">Kembali ke Perpustakaan Hati</a></main></body></html>`;
  return new Response(html, { status, headers });
}

/** GET /api/auth/threads/callback: verifies the state cookie, swaps the code, stores the long-lived token. */
export async function GET(req: Request) {
  const config = threadsConfig();
  if (!config) return page(null, 503, "Threads belum dikonfigurasi", "<p>Set <code>THREADS_APP_ID</code> dan <code>THREADS_APP_SECRET</code> dahulu.</p>");

  const url = new URL(req.url);
  if (url.searchParams.get("error")) {
    return page(config, 400, "Kebenaran dibatalkan", "<p>Tiada token disimpan. Cuba sambung semula bila sedia.</p>");
  }

  const state = url.searchParams.get("state") ?? "";
  const cookieState = readCookie(req.headers.get("cookie"), THREADS_STATE_COOKIE);
  if (!state || !cookieState || !sameState(state, cookieState)) {
    return page(config, 400, "Sesi tidak sah", "<p>Pautan ini tamat tempoh atau dibuka dari pelayar lain. Mulakan semula dari <code>/api/auth/threads/start</code>.</p>");
  }

  const code = url.searchParams.get("code") ?? "";
  if (!code) return page(config, 400, "Kod tiada", "<p>Threads tidak memulangkan kod kebenaran.</p>");

  try {
    const token = await exchangeCode(config, code);
    const profile = await threadsProfile(token.accessToken);
    getThreadsStore().save({
      accessToken: token.accessToken,
      userId: profile.id,
      username: profile.username,
      scopes: config.scopes,
      expiresAt: Date.now() + token.expiresIn * 1000,
    });
    const until = new Date(Date.now() + token.expiresIn * 1000).toISOString().slice(0, 10);
    return page(
      config,
      200,
      "Threads disambungkan",
      `<p>Akaun <code>@${profile.username}</code> kini disambungkan.</p><p>Token sah sehingga <code>${until}</code>. Segarkan sebelum tamat melalui <code>POST /api/auth/threads/refresh</code>.</p>`,
    );
  } catch (e) {
    const detail = e instanceof ThreadsError ? e.message : "Ralat tidak dijangka.";
    return page(config, 502, "Sambungan gagal", `<p>${detail}</p><p>Token tidak disimpan. Cuba semula.</p>`);
  }
}
