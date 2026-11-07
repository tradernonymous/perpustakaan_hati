"use client";

import { useState, type FormEvent } from "react";

export function LibraryLogin() {
  const [msg, setMsg] = useState("");
  const [ok, setOk] = useState(false);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const email = new FormData(e.currentTarget).get("email");
    setBusy(true);
    try {
      const res = await fetch("/api/pustaka", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email }) });
      const data = (await res.json().catch(() => ({}))) as { message?: string; error?: string };
      setOk(res.ok);
      setMsg(data.message ?? data.error ?? "Maaf, ada masalah. Cuba lagi sebentar.");
    } catch {
      setOk(false);
      setMsg("Tiada sambungan internet. Cuba lagi sebentar.");
    }
    setBusy(false);
  }

  return (
    <form onSubmit={onSubmit} className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5 md:p-8">
      <label htmlFor="lib-email" className="text-sm font-semibold text-gold-light">E-mel yang kamu guna semasa membeli</label>
      <input id="lib-email" name="email" type="email" required autoComplete="email" inputMode="email" placeholder="nama@contoh.com"
        className="min-h-tap w-full rounded border border-forest-edge bg-forest-soft px-3 text-base text-on-dark placeholder:text-on-dark-muted focus:outline-none focus:ring-2 focus:ring-green-400" />
      <button type="submit" disabled={busy} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">{busy ? "Menghantar..." : "Hantar pautan ke e-mel"}</button>
      <p aria-live="polite" role="status" className={ok ? "text-green-300" : "text-burgundy-light"}>{msg}</p>
    </form>
  );
}
