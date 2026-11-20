import { headers } from "next/headers";
import { notFound } from "next/navigation";
import { isAdminRequest } from "@/src/server/auth";
import { recentReaderFeedback } from "@/src/server/reader-feedback";

export const dynamic = "force-dynamic";
export const metadata = { title: "Suara Pembaca · Admin", robots: { index: false, follow: false } };

export default async function ReaderFeedbackAdmin() {
  const request = new Request("http://local/admin/suara-pembaca", { headers: await headers() });
  if (!isAdminRequest(request, process.env.ADMIN_TOKEN)) notFound();
  const feedback = recentReaderFeedback();
  return (
    <main className="mx-auto grid max-w-reading gap-4 p-6">
      <a href="/admin" className="text-fg-healing underline">Kembali ke admin</a>
      <h1 className="font-display text-3xl">Suara Pembaca</h1>
      <p className="text-fg-muted">Maklum balas peribadi. Dapatkan izin untuk petikan dan nama yang tepat sebelum menerbitkan.</p>
      {feedback.length === 0 && <p>Belum ada maklum balas.</p>}
      {feedback.map((item) => (
        <article className="ph-card grid gap-2 p-4" key={item.id}>
          <h2 className="font-semibold">{item.name || "Tanpa nama"}</h2>
          <p className="text-sm text-fg-muted">{item.source} · {item.created_at}</p>
          <blockquote className="whitespace-pre-wrap break-words">{item.message}</blockquote>
          <p className="text-sm">{item.email || "Tiada e-mel diberikan"}</p>
        </article>
      ))}
    </main>
  );
}
