"use client";

import Link from "next/link";
import { useId, useRef, useState, type FormEvent } from "react";
import { quoteForType, type SessionType } from "@/src/games/booking";
import { EMAIL, MY_MOBILE } from "@/src/server/validate";

const OPTIONS: { id: SessionType; label: string; duration: string; detail: string }[] = [
  { id: "clarity", label: "Kejelasan emosi 1-on-1", duration: "60 minit", detail: "Fokus pada corak emosi, sempadan sihat, dan keputusan tenang." },
  { id: "couples", label: "Pengantaraan pasangan", duration: "90 minit", detail: "Ruang selamat untuk kedua-dua pihak didengar tanpa menghukum." },
  { id: "panel", label: "Panel kaunselor", duration: "75 minit", detail: "Sesi berstruktur dengan kaunselor berdaftar di bawah Perpustakaan Hati." },
];

export function BookingForm() {
  const id = useId();
  const [sessionType, setSessionType] = useState<SessionType>("clarity");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [consent, setConsent] = useState(false);
  const [website, setWebsite] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState("");

  const nameRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const phoneRef = useRef<HTMLInputElement>(null);
  const consentRef = useRef<HTMLInputElement>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const cleanName = name.trim();
    const cleanEmail = email.trim().toLowerCase();
    const cleanPhone = phone.replace(/[\s-]/g, "");

    if (cleanName.length < 2) {
      setStatus("error");
      setError("Sila isi nama panggilan atau nama penuh.");
      nameRef.current?.focus();
      return;
    }
    if (!EMAIL.test(cleanEmail)) {
      setStatus("error");
      setError("Alamat e-mel tidak sah.");
      emailRef.current?.focus();
      return;
    }
    if (!MY_MOBILE.test(cleanPhone)) {
      setStatus("error");
      setError("Nombor WhatsApp mesti nombor mudah alih Malaysia, contoh 012-345 6789.");
      phoneRef.current?.focus();
      return;
    }
    if (!consent) {
      setStatus("error");
      setError("Sila setuju dengan notis privasi (PDPA) untuk teruskan.");
      consentRef.current?.focus();
      return;
    }

    setStatus("sending");
    setError("");
    try {
      const res = await fetch("/api/booking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: cleanName, email: cleanEmail, phone: cleanPhone, sessionType, notes, consent, website }),
      });
      const data = (await res.json().catch(() => ({}))) as { error?: string };
      if (!res.ok) {
        setStatus("error");
        setError(data.error ?? "Ada masalah menghantar permintaan. Cuba lagi sebentar.");
        return;
      }
      setStatus("sent");
    } catch {
      setStatus("error");
      setError("Sambungan terputus. Cuba lagi.");
    }
  }

  if (status === "sent") {
    const selected = OPTIONS.find((o) => o.id === sessionType) ?? OPTIONS[0];
    return (
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-6" role="status" aria-live="polite">
        <p className="font-display text-2xl text-green-900">Permintaan sesi diterima.</p>
        <p className="text-ink-grove">
          Terima kasih, {name}. Pasukan kami akan hubungi melalui WhatsApp atau e-mel untuk sahkan slot masa dan pautan pembayaran FPX / DuitNow bagi {selected.label} (RM{quoteForType(sessionType) / 100}).
        </p>
        <div className="flex flex-wrap gap-3">
          <Link href="/#edisi" className="ph-cta min-h-tap">
            Lihat edisi eBook
          </Link>
          <Link href="/cermin-pasangan" className="btn-ghost min-h-tap">
            Cuba Cermin Pasangan dahulu
          </Link>
        </div>
      </div>
    );
  }

  const errorId = error ? `${id}-err` : undefined;

  return (
    <form className="ph-card mx-auto flex max-w-reading flex-col gap-5 p-5" onSubmit={onSubmit} noValidate>
      <div className="absolute left-[-9999px] h-px w-px overflow-hidden" aria-hidden="true">
        <label htmlFor={`${id}-website`}>Laman web</label>
        <input
          id={`${id}-website`}
          type="text"
          name="website"
          tabIndex={-1}
          autoComplete="off"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
        />
      </div>

      <fieldset className="flex flex-col gap-2.5">
        <legend className="text-sm font-medium text-green-900">Pilih jenis sesi</legend>
        {OPTIONS.map((opt) => {
          const active = sessionType === opt.id;
          return (
            <label
              key={opt.id}
              className={
                active
                  ? "flex cursor-pointer items-start gap-3 rounded-lg border-2 border-green-700 bg-sage p-3.5"
                  : "flex cursor-pointer items-start gap-3 rounded-lg border border-daylight-edge bg-cream/60 p-3.5 hover:border-green-700/50"
              }
            >
              <input
                type="radio"
                name="sessionType"
                value={opt.id}
                checked={active}
                onChange={() => setSessionType(opt.id)}
                className="mt-1 h-4 w-4 accent-green-700"
              />
              <span className="flex-1">
                <span className="flex flex-wrap items-baseline justify-between gap-2 font-medium text-green-900">
                  <span>{opt.label}</span>
                  <span className="font-mono text-sm">
                    RM{quoteForType(opt.id) / 100} ({opt.duration})
                  </span>
                </span>
                <span className="mt-1 block text-xs text-muted-grove">{opt.detail}</span>
              </span>
            </label>
          );
        })}
      </fieldset>

      <div className="grid gap-4 sm:grid-cols-2">
        <label htmlFor={`${id}-name`} className="flex flex-col gap-1 text-sm text-green-900 sm:col-span-2">
          Nama panggilan atau nama penuh
          <input
            ref={nameRef}
            id={`${id}-name`}
            type="text"
            required
            className="min-h-tap rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
            placeholder="cth: Amirul atau Siti"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={100}
          />
        </label>

        <label htmlFor={`${id}-email`} className="flex flex-col gap-1 text-sm text-green-900">
          E-mel
          <input
            ref={emailRef}
            id={`${id}-email`}
            type="email"
            required
            className="min-h-tap rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
            placeholder="nama@contoh.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            maxLength={254}
          />
        </label>

        <label htmlFor={`${id}-phone`} className="flex flex-col gap-1 text-sm text-green-900">
          Nombor WhatsApp
          <input
            ref={phoneRef}
            id={`${id}-phone`}
            type="tel"
            required
            className="min-h-tap rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
            placeholder="012-345 6789"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            maxLength={20}
          />
        </label>
      </div>

      <label htmlFor={`${id}-notes`} className="flex flex-col gap-1 text-sm text-green-900">
        Konteks ringkas dan waktu pilihan (pilihan)
        <textarea
          id={`${id}-notes`}
          rows={3}
          className="rounded border border-daylight-edge bg-sage px-3 py-2 text-ink-grove"
          placeholder="cth: Malam hari bekerja selepas 8 malam, ingin bincang soal komunikasi pasangan"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={1500}
        />
      </label>

      <div className="flex items-start gap-2.5 text-sm text-green-900">
        <input
          ref={consentRef}
          id={`${id}-consent`}
          type="checkbox"
          className="mt-0.5 h-5 w-5 accent-green-700"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
        />
        <label htmlFor={`${id}-consent`} className="text-muted-grove">
          Saya setuju butiran ini digunakan untuk pengesahan slot kaunseling sahaja (patuh PDPA 2010).
        </label>
      </div>

      {status === "error" && (
        <p id={errorId} role="alert" className="text-sm text-crimson-ink">
          {error}
        </p>
      )}

      <p className="text-xs text-muted-grove">
        Bayaran melalui FPX / DuitNow hanya dibuat selepas jadual sesi disahkan. Peringatan automatik melalui WhatsApp dan Google Meet.
      </p>

      <button type="submit" className="ph-cta min-h-tap" disabled={status === "sending"}>
        {status === "sending" ? "Sedang menghantar..." : `Daftar minat sesi (RM${quoteForType(sessionType) / 100})`}
      </button>
    </form>
  );
}
