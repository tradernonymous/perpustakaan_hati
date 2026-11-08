"use client";

import { useState, type FormEvent } from "react";

type Status = "idle" | "submitting" | "success" | "error";

export function OptInForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    setStatus("submitting");
    setMessage("");
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          email: form.get("email"),
          phone: form.get("phone"),
          consent: form.get("consent") === "on",
          website: form.get("website"),
        }),
      });
      if (res.ok) {
        setStatus("success");
        setMessage("Terima kasih. Kami akan hubungi kamu apabila Edisi Poket sedia.");
        return;
      }
      const data = (await res.json().catch(() => ({}))) as { error?: string };
      setStatus("error");
      setMessage(data.error ?? "Maaf, ada masalah. Cuba lagi sebentar.");
    } catch {
      setStatus("error");
      setMessage("Tiada sambungan internet. Cuba lagi sebentar.");
    }
  }

  const field =
    "min-h-tap w-full rounded border border-forest-edge bg-forest-soft px-3 text-base text-on-dark placeholder:text-on-dark-muted focus:outline-none focus:ring-2 focus:ring-green-400";

  return (
    <form onSubmit={onSubmit} className="ph-beam ph-lux ph-card mx-auto flex max-w-reading flex-col gap-4 p-5 md:p-8" noValidate={false}>
      <div className="flex flex-col gap-1">
        <label htmlFor="optin-email" className="text-sm font-semibold text-gold-light">E-mel</label>
        <input id="optin-email" name="email" type="email" autoComplete="email" inputMode="email" placeholder="nama@contoh.com" className={field} />
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="optin-phone" className="text-sm font-semibold text-gold-light">Nombor WhatsApp (pilihan jika ada e-mel)</label>
        <input id="optin-phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" placeholder="012-345 6789" className={field} />
      </div>

      {/* Honeypot: invisible to people and assistive tech; bots fill it. */}
      <div aria-hidden="true" className="absolute left-[-9999px] h-0 w-0 overflow-hidden">
        <label htmlFor="optin-website">Laman web</label>
        <input id="optin-website" name="website" type="text" tabIndex={-1} autoComplete="off" />
      </div>

      <label className="flex min-h-tap items-start gap-3 text-sm text-on-dark">
        <input type="checkbox" name="consent" required className="mt-1 h-5 w-5 accent-green-500" />
        <span>
          Saya setuju e-mel/nombor saya disimpan untuk menghantar Edisi Poket dan kemas kini
          Perpustakaan Hati, mengikut notis privasi PDPA. Saya boleh berhenti bila-bila masa.
        </span>
      </label>

      <button type="submit" disabled={status === "submitting" || status === "success"} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">
        {status === "submitting" ? "Menghantar..." : "Dapatkan Edisi Poket"}
      </button>

      <p aria-live="polite" role="status" className={status === "error" ? "text-burgundy-light" : "text-green-300"}>
        {message}
      </p>
    </form>
  );
}
