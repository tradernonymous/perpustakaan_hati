"use client";

import { useState, type FormEvent } from "react";

type Props = { product: "membangun" | "teman-hidup"; name: string; priceLabel: string; priceSen: number; bump: { label: string; priceSen: number } | null };

const rm = (sen: number) => `RM ${(sen / 100).toFixed(2)}`;

export function CheckoutForm({ product, name, priceLabel, priceSen, bump }: Props) {
  const [withBump, setWithBump] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [fieldError, setFieldError] = useState<{ email?: string; consent?: string }>({});
  const total = priceSen + (withBump && bump ? bump.priceSen : 0);

  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /** One message per field, spoken once: native bubbles are off via noValidate. */
  function validate(el: HTMLFormElement) {
    const email = el.elements.namedItem("email") as HTMLInputElement | null;
    const consent = el.elements.namedItem("consent") as HTMLInputElement | null;
    const next: { email?: string; consent?: string } = {};
    const value = email?.value.trim() ?? "";
    if (!value) next.email = "Masukkan e-mel kamu.";
    else if (!EMAIL_RE.test(value)) next.email = "E-mel tidak sah. Contoh: nama@contoh.com";
    if (consent && !consent.checked) next.consent = "Tandakan persetujuan PDPA untuk meneruskan.";
    return next;
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const el = e.currentTarget;
    const found = validate(el);
    if (found.email || found.consent) {
      setFieldError(found);
      (el.elements.namedItem(found.email ? "email" : "consent") as HTMLElement | null)?.focus();
      return;
    }
    setFieldError({});
    const f = new FormData(el);
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

  const field = "min-h-tap w-full rounded border border-line bg-surface-soft px-3 text-base text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-green-700";

  return (
    <form onSubmit={onSubmit} noValidate className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-4 sm:gap-5 md:p-8">
      <div className="flex flex-col gap-1 border-b border-line pb-4 sm:flex-row sm:items-baseline sm:justify-between sm:gap-4">
        <h2 className="font-display text-2xl text-fg">{name}</h2>
        <p className="text-sm text-fg-muted">Harga ditunjuk di laman: {priceLabel}</p>
      </div>

      {bump && (
        <label className="flex min-h-tap cursor-pointer items-start gap-3 rounded border border-gold-deep bg-surface-raised p-4 text-fg">
          <input type="checkbox" checked={withBump} onChange={(e) => setWithBump(e.target.checked)} className="mt-1 h-5 w-5 accent-green-500" />
          <span>
            <strong className="text-fg">Tambah Teman Hidup, hanya {rm(bump.priceSen)} lagi</strong>
            <span className="mt-1 block text-sm">{bump.label}</span>
          </span>
        </label>
      )}

      <div className="flex flex-col gap-1">
        <label htmlFor="co-email" className="text-sm font-semibold text-fg">E-mel (buku dihantar ke sini)</label>
        <input
          id="co-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          inputMode="email"
          placeholder="nama@contoh.com"
          className={field}
          aria-invalid={fieldError.email ? "true" : "false"}
          aria-describedby="co-email-error"
          onChange={() => setFieldError((prev) => ({ ...prev, email: undefined }))}
        />
        <p id="co-email-error" role="alert" className="text-sm text-danger">{fieldError.email}</p>
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="co-phone" className="text-sm font-semibold text-fg">Nombor WhatsApp (pilihan, untuk pautan segera)</label>
        <input id="co-phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" placeholder="012-345 6789" className={field} />
      </div>

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-semibold text-fg">Kaedah bayaran</legend>
        <label className="flex min-h-tap items-center gap-3 rounded border border-line px-3 text-fg">
          <input type="radio" name="method" value="fpx" defaultChecked className="h-5 w-5 accent-green-500" />
          FPX online banking atau DuitNow QR
        </label>
        <label className="flex min-h-tap items-center gap-3 rounded border border-line px-3 text-fg">
          <input type="radio" name="method" value="card" className="h-5 w-5 accent-green-500" />
          Kad kredit atau debit
        </label>
      </fieldset>

      <label className="flex min-h-tap items-start gap-3 text-sm text-fg">
        <input
          id="co-consent"
          type="checkbox"
          name="consent"
          required
          className="mt-1 h-5 w-5 accent-green-500"
          aria-invalid={fieldError.consent ? "true" : "false"}
          aria-describedby="co-consent-error"
          onChange={() => setFieldError((prev) => ({ ...prev, consent: undefined }))}
        />
        <span>
          Saya setuju e-mel/nombor saya digunakan untuk menghantar pesanan ini, mengikut notis privasi PDPA.
          <span id="co-consent-error" role="alert" className="mt-1 block text-danger">{fieldError.consent}</span>
        </span>
      </label>

      <div className="flex items-center justify-between border-t border-line pt-4">
        <span className="text-fg-muted">Jumlah</span>
        <strong className="font-display text-3xl text-fg">{rm(total)}</strong>
      </div>

      <button type="submit" disabled={busy} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">
        {busy ? "Membuka pembayaran..." : `Bayar ${rm(total)}`}
      </button>
      <p aria-live="polite" role="status" className="text-danger">{error}</p>
      <div className="space-y-1 rounded border border-line bg-surface-soft p-3 text-xs text-fg-muted">
        <p>Penghantaran segera ke e-mel kamu (dan WhatsApp jika diisi) sebaik pembayaran disahkan.</p>
        <p>Data diurus mengikut PDPA Malaysia dan tidak dikongsi dengan pihak ketiga. Selepas bayar, buku juga boleh dicapai melalui /pustaka.</p>
      </div>
    </form>
  );
}
