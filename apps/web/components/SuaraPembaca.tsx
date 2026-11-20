"use client";

import { useEffect, useState } from "react";

export function SuaraPembaca() {
  const [status, setStatus] = useState<string | null>(null);
  useEffect(() => setStatus(new URLSearchParams(window.location.search).get("suara")), []);
  return (
    <section id="pembaca" aria-labelledby="suara-heading" className="scroll-mt-24 border-y border-line px-5 py-12">
      <div className="mx-auto grid max-w-reading gap-5">
        <div>
          <h2 id="suara-heading" className="font-display text-3xl">Suara Pembaca</h2>
          <p className="mt-2 text-fg-muted">Adakah tulisan Rahimam di Threads atau dalam buku membantu kamu rasa lebih difahami, lebih bersemangat, atau lebih bersedia menghadapi konflik?</p>
        </div>
        {status === "sent" && <p role="status" className="text-fg-healing">Terima kasih. Perkongsian kamu telah diterima secara peribadi.</p>}
        {status === "invalid" && <p role="alert" className="text-danger">Semak mesej, alamat e-mel jika diisi, dan persetujuan sebelum menghantar.</p>}
        <details className="ph-card p-4 sm:p-6">
          <summary className="cursor-pointer font-semibold text-fg-healing">Kongsi pengalaman kamu</summary>
          <form method="post" action="/api/suara-pembaca" className="mt-5 grid gap-4">
            <label className="grid gap-1 text-sm">Bacaan yang membantu
              <select name="source" className="min-h-tap rounded border border-line bg-surface-soft p-2">
                <option value="threads">Perkongsian Rahimam di Threads</option>
                <option value="ebook">Ebook Perpustakaan Hati</option>
                <option value="lain">Perkongsian lain oleh Rahimam</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm">Pengalaman kamu
              <textarea name="message" rows={4} required minLength={12} maxLength={800} className="rounded border border-line bg-surface-soft p-3" />
              <span className="text-fg-muted">Fokus pada apa yang membantu. Elakkan maklumat yang boleh mengenal pasti orang lain.</span>
            </label>
            <label className="grid gap-1 text-sm">Nama pilihan (pilihan)
              <input name="name" maxLength={80} className="min-h-tap rounded border border-line bg-surface-soft p-2" />
            </label>
            <label className="grid gap-1 text-sm">E-mel untuk dihubungi (pilihan)
              <input type="email" name="email" autoComplete="email" maxLength={254} className="min-h-tap rounded border border-line bg-surface-soft p-2" />
            </label>
            <div hidden><label>Laman web<input name="website" tabIndex={-1} autoComplete="off" /></label></div>
            <label className="flex items-start gap-2 text-sm">
              <input type="checkbox" name="permission" className="mt-1" required />
              <span>Saya setuju pasukan menyemak maklum balas ini secara peribadi. Sebarang petikan awam memerlukan izin berasingan.</span>
            </label>
            <button type="submit" className="ph-cta min-h-tap justify-center">Hantar secara peribadi</button>
          </form>
        </details>
      </div>
    </section>
  );
}
