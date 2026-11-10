import type { Metadata } from "next";
import { cookies } from "next/headers";
import { isAdminRequest } from "@/src/server/auth";
import { getThreadsStore } from "@/src/server/instance";
import { AdminPanel } from "./AdminPanel";

export const metadata: Metadata = { title: "Admin — Perpustakaan Hati", robots: { index: false, follow: false } };
export const dynamic = "force-dynamic";

/**
 * /admin — the site's admin door.
 * Sign in with Facebook (allowlisted ids only) or with the ADMIN_TOKEN password.
 * Nothing here is linked from the storefront.
 */
export default async function AdminPage() {
  const jar = await cookies();
  const request = new Request("http://local/admin", { headers: { cookie: jar.toString() } });
  const signedIn = isAdminRequest(request, process.env.ADMIN_TOKEN);

  if (!signedIn) {
    return (
      <main className="ph-daylight mx-auto flex min-h-screen max-w-reading flex-col justify-center gap-6 px-5 py-16">
        <p className="ph-kicker">Perpustakaan Hati</p>
        <h1 className="font-display text-3xl text-green-900">Masuk ke admin</h1>
        <p className="text-muted-grove">
          Hanya akaun Facebook yang disenaraikan boleh masuk. Akaun lain akan ditolak walaupun berjaya log masuk.
        </p>
        <a href="/api/auth/facebook/start" className="ph-cta min-h-cta-mobile items-center justify-center text-center">
          Masuk dengan Facebook
        </a>
        <p className="text-sm text-muted-grove">
          Kata laluan admin masih berfungsi sebagai sandaran: buka{" "}
          <a className="underline" href="/admin/subscribers">
            eksport pelanggan
          </a>{" "}
          dan masukkan token apabila pelayar bertanya.
        </p>
      </main>
    );
  }

  const token = getThreadsStore().get();
  const threads = token
    ? { connected: token.expiresAt > Date.now(), username: token.username, daysLeft: Math.max(0, Math.floor((token.expiresAt - Date.now()) / 86_400_000)) }
    : { connected: false };

  return (
    <main className="ph-daylight mx-auto flex min-h-screen max-w-reading flex-col gap-6 px-5 py-16">
      <p className="ph-kicker">Perpustakaan Hati</p>
      <h1 className="font-display text-3xl text-green-900">Admin</h1>
      <AdminPanel threads={threads} />
    </main>
  );
}