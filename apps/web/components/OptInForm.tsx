"use client";

import { temanHatiEnabled } from "@/src/feature-flags";
import { useState, type FormEvent } from "react";

type Status = "idle" | "submitting" | "success" | "error";

type Errors = { email?: string; consent?: string };

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function OptInForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");
  const [errors, setErrors] = useState<Errors>({});

  /** Native constraints are off (noValidate) so one message per field is spoken, not two. */
  function validate(el: HTMLFormElement): Errors {
    const email = el.elements.namedItem("email") as HTMLInputElement | null;
    const consent = el.elements.namedItem("consent") as HTMLInputElement | null;
    const next: Errors = {};
    const value = email?.value.trim() ?? "";
    if (!value) next.email = "Masukkan e-mel kamu.";
    else if (!EMAIL_RE.test(value)) next.email = "E-mel tidak sah. Contoh: nama@contoh.com";
    if (consent && !consent.checked) next.consent = "Tandakan kotak persetujuan untuk meneruskan.";
    return next;
  }

  function clearError(field: keyof Errors) {
    setErrors((prev) => (prev[field] ? { ...prev, [field]: undefined } : prev));
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const el = e.currentTarget;
    const found = validate(el);
    if (found.email || found.consent) {
      setErrors(found);
      const target = found.email ? "optin-email" : "optin-consent";
      (el.elements.namedItem(target === "optin-email" ? "email" : "consent") as HTMLElement | null)?.focus();
      return;
    }
    setErrors({});
    const form = new FormData(el);
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
    "min-h-tap w-full rounded border border-line bg-surface-soft px-3 text-base text-fg placeholder:text-fg-muted focus:outline-none focus:ring-2 focus:ring-green-700";

  return (
    <form onSubmit={onSubmit} noValidate className="ph-beam ph-lux ph-card mx-auto flex max-w-reading flex-col gap-4 p-5 md:p-8">
      <div className="flex flex-col gap-1">
        <label htmlFor="optin-email" className="text-sm font-semibold text-fg">E-mel</label>
        <input
          id="optin-email"
          name="email"
          type="email"
          autoComplete="email"
          inputMode="email"
          placeholder="nama@contoh.com"
          className={field}
          aria-invalid={errors.email ? "true" : "false"}
          aria-describedby="optin-email-error"
          onChange={() => clearError("email")}
        />
        <p id="optin-email-error" role="alert" className="text-sm text-danger">{errors.email}</p>
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="optin-phone" className="text-sm font-semibold text-fg">Nombor WhatsApp (pilihan jika ada e-mel)</label>
        <input id="optin-phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" placeholder="012-345 6789" className={field} />
      </div>

      {/* Honeypot: invisible to people and assistive tech; bots fill it. */}
      <div aria-hidden="true" className="absolute left-[-9999px] h-0 w-0 overflow-hidden">
        <label htmlFor="optin-website">Laman web</label>
        <input id="optin-website" name="website" type="text" tabIndex={-1} autoComplete="off" />
      </div>

      <label className="flex min-h-tap cursor-pointer items-start gap-3 text-sm text-fg">
        <input
          id="optin-consent"
          type="checkbox"
          name="consent"
          required
          className="mt-1 h-5 w-5 accent-green-500"
          aria-invalid={errors.consent ? "true" : "false"}
          aria-describedby="optin-consent-error"
          onChange={() => clearError("consent")}
        />
        <span>
          Saya setuju e-mel/nombor saya disimpan untuk menghantar Edisi Poket dan kemas kini
          Perpustakaan Hati, mengikut notis privasi PDPA. Saya boleh berhenti bila-bila masa.
          <span id="optin-consent-error" role="alert" className="mt-1 block text-danger">{errors.consent}</span>
        </span>
      </label>

      <button type="submit" disabled={status === "submitting" || status === "success"} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">
        {status === "submitting" ? "Menghantar..." : status === "success" ? "Sudah didaftarkan" : "Dapatkan Edisi Poket"}
      </button>

      <p aria-live="polite" role="status" className={status === "error" ? "text-danger" : "font-medium text-fg-healing"}>
        {message}
      </p>

      {status === "success" && (
        <div className="rounded border border-line bg-surface-soft p-4 text-sm text-fg">
          <p className="font-semibold text-fg">Buka Pustaka Saya dan sahkan e-mel untuk memuat turun buku percuma:</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <a
              href="/pustaka"
              download="edisi-poket-perpustakaan-hati.pdf"
              className="ph-cta min-h-tap inline-flex items-center px-4 py-2 text-xs"
            >
              Buka Pustaka Saya
            </a>
            <a href="/kad-jujur-hati" className="btn-ghost min-h-tap px-4 py-2 text-xs">Kad Jujur Hati</a>
            <a href="/cermin-pasangan" className="btn-ghost min-h-tap px-4 py-2 text-xs">Cermin Pasangan</a>
            {temanHatiEnabled && (<a href="/teman-hati" className="btn-ghost min-h-tap px-4 py-2 text-xs">Teman Hati AI</a>)}
          </div>
        </div>
      )}
    </form>
  );
}
