"use client";

import { useState, type FormEvent } from "react";

type Props = { product: "membangun" | "teman-hidup"; name: string; priceLabel: string; priceSen: number; bump: { label: string; priceSen: number } | null };

const rm = (sen: number) => `RM ${(sen / 100).toFixed(2)}`;

export function CheckoutForm({ product, name, priceLabel, priceSen, bump }: Props) {
  const [withBump, setWithBump] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const total = priceSen + (withBump && bump ? bump.priceSen : 0);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ product, bump: withBump, email: f.get("email"), phone: f.get("phone"), method: f.get("method"), consent: f.get("consent") === "on" }),
      });
      const data = (await res.json().catch(() => ({}))) as { url?: string; error?: string };
      if (res.ok && data.url) {
        window.location.assign(data.url);
        return;
      }
      setError(data.error ?? "Maaf, ada masalah. Cuba lagi sebentar.");
    } catch {
      setError("Tiada sambungan internet. Cuba lagi sebentar.");
    }
    setBusy(false);
  }

  const field = "min-h-tap w-full rounded border border-daylight-edge bg-sage px-3 text-base text-ink-grove placeholder:text-muted-grove focus:outline-none focus:ring-2 focus:ring-green-700";

  return (
    <form onSubmit={onSubmit} className="ph-card mx-auto flex max-w-reading flex-col gap-5 p-5 md:p-8">
      <div className="flex items-baseline justify-between gap-4 border-b border-daylight-edge pb-4">
        <h2 className="font-display text-2xl text-green-900">{name}</h2>
        <p className="text-sm text-muted-grove">Harga ditunjuk di laman: {priceLabel}</p>
      </div>

      {bump && (
        <label className="flex min-h-tap cursor-pointer items-start gap-3 rounded border border-gold-deep bg-daylight-raised p-4 text-ink-grove">
          <input type="checkbox" checked={withBump} onChange={(e) => setWithBump(e.target.checked)} className="mt-1 h-5 w-5 accent-green-500" />
          <span>
            <strong className="text-green-900">Tambah Teman Hidup, hanya {rm(bump.priceSen)} lagi</strong>
            <span className="mt-1 block text-sm">{bump.label}</span>
          </span>
        </label>
      )}

      <div className="flex flex-col gap-1">
        <label htmlFor="co-email" className="text-sm font-semibold text-green-900">E-mel (buku dihantar ke sini)</label>
        <input id="co-email" name="email" type="email" required autoComplete="email" inputMode="email" placeholder="nama@contoh.com" className={field} />
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="co-phone" className="text-sm font-semibold text-green-900">Nombor WhatsApp (pilihan, untuk pautan segera)</label>
        <input id="co-phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" placeholder="012-345 6789" className={field} />
      </div>

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-semibold text-green-900">Kaedah bayaran</legend>
        <label className="flex min-h-tap items-center gap-3 rounded border border-daylight-edge px-3 text-ink-grove">
          <input type="radio" name="method" value="fpx" defaultChecked className="h-5 w-5 accent-green-500" />
          FPX online banking atau DuitNow QR
        </label>
        <label className="flex min-h-tap items-center gap-3 rounded border border-daylight-edge px-3 text-ink-grove">
          <input type="radio" name="method" value="card" className="h-5 w-5 accent-green-500" />
          Kad kredit atau debit
        </label>
      </fieldset>

      <label className="flex min-h-tap items-start gap-3 text-sm text-ink-grove">
        <input type="checkbox" name="consent" required className="mt-1 h-5 w-5 accent-green-500" />
        <span>Saya setuju e-mel/nombor saya digunakan untuk menghantar pesanan ini, mengikut notis privasi PDPA.</span>
      </label>

      <div className="flex items-center justify-between border-t border-daylight-edge pt-4">
        <span className="text-muted-grove">Jumlah</span>
        <strong className="font-display text-3xl text-green-900">{rm(total)}</strong>
      </div>

      <button type="submit" disabled={busy} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">
        {busy ? "Membuka pembayaran..." : `Bayar ${rm(total)}`}
      </button>
      <p aria-live="polite" role="status" className="text-burgundy">{error}</p>
      <p className="text-xs text-muted-grove">Kami hantar pautan muat turun melalui e-mel (dan WhatsApp jika diisi) sebaik pembayaran berjaya.</p>
    </form>
  );
}
