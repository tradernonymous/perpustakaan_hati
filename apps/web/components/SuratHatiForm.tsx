"use client";

import Link from "next/link";
import { useId, useRef, useState, type FormEvent } from "react";
import { acceptsSurat } from "@/src/games/surat";

export function SuratHatiForm() {
  const id = useId();
  const [name, setName] = useState("");
  const [dilemma, setDilemma] = useState("");
  const [consentPublish, setConsentPublish] = useState(true);
  const [website, setWebsite] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState("");
  const dilemmaRef = useRef<HTMLTextAreaElement>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!acceptsSurat({ dilemma })) {
      setStatus("error");
      setError("Sila tulis luahan sekurang-kurangnya beberapa perkataan.");
      dilemmaRef.current?.focus();
      return;
    }

    setStatus("sending");
    setError("");
    try {
      const res = await fetch("/api/surat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, dilemma, consentPublish, website }),
      });
      const data = (await res.json().catch(() => ({}))) as { error?: string };
      if (!res.ok) {
        setStatus("error");
        setError(data.error ?? "Ada masalah menghantar surat. Cuba lagi sebentar.");
        return;
      }
      setStatus("sent");
    } catch {
      setStatus("error");
      setError("Sambungan terputus. Cuba lagi.");
    }
  }

  if (status === "sent") {
    return (
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-6" role="status" aria-live="polite">
        <p className="font-display text-2xl text-green-900">Surat kamu sudah diterima.</p>
        <p className="text-ink-grove">
          Terima kasih kerana sudi berkongsi. Nama samaran kamu sudah disembunyikan secara automatik daripada teks luahan sebelum disimpan.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="btn-ghost min-h-tap"
            onClick={() => {
              setName("");
              setDilemma("");
              setStatus("idle");
            }}
          >
            Hantar surat lain
          </button>
          <Link href="/teman-hati" className="ph-cta min-h-tap">
            Cuba Teman Hati sekarang
          </Link>
        </div>
      </div>
    );
  }

  const dilemmaErrorId = error ? `${id}-dilemma-err` : undefined;

  return (
    <form className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5" onSubmit={onSubmit} noValidate>
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

      <label htmlFor={`${id}-name`} className="flex flex-col gap-1 text-sm text-green-900">
        Nama samaran (pilihan)
        <input
          id={`${id}-name`}
          name="name"
          className="min-h-tap rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
          placeholder="cth: Aina"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={80}
        />
      </label>

      <label htmlFor={`${id}-dilemma`} className="flex flex-col gap-1 text-sm text-green-900">
        Luahan kamu
        <textarea
          ref={dilemmaRef}
          id={`${id}-dilemma`}
          name="dilemma"
          rows={6}
          required
          aria-invalid={status === "error" || undefined}
          aria-describedby={dilemmaErrorId}
          className="rounded border border-daylight-edge bg-sage px-3 py-2 text-ink-grove"
          placeholder="Tulis di sini, nama kamu akan disembunyikan..."
          value={dilemma}
          onChange={(e) => {
            setDilemma(e.target.value);
            if (status === "error") setStatus("idle");
          }}
          maxLength={3000}
        />
      </label>

      <div className="flex items-start gap-2.5 text-sm text-green-900">
        <input
          id={`${id}-publish`}
          type="checkbox"
          className="mt-0.5 h-5 w-5 accent-green-700"
          checked={consentPublish}
          onChange={(e) => setConsentPublish(e.target.checked)}
        />
        <label htmlFor={`${id}-publish`} className="text-muted-grove">
          Benarkan luahan anonim ini dijadikan inspirasi breakdown psikologi (tanpa identiti) di Threads atau eBook.
        </label>
      </div>

      {status === "error" && (
        <p id={dilemmaErrorId} role="alert" className="text-sm text-crimson-ink">
          {error}
        </p>
      )}

      <button type="submit" className="ph-cta min-h-tap" disabled={status === "sending"}>
        {status === "sending" ? "Sedang menghantar..." : "Hantar Surat"}
      </button>
      <p className="text-xs text-muted-grove">
        Surat anonim disimpan untuk terbitan dan siri Threads. Tiada perkongsian dengan pihak ketiga.
      </p>
    </form>
  );
}
