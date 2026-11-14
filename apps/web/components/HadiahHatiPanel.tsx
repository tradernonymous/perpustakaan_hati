"use client";

import Link from "next/link";
import { useId, useState, type FormEvent } from "react";
import { EMAIL } from "@/src/server/validate";

async function sha256HexPrefix(text: string): Promise<string> {
  const bytes = new TextEncoder().encode(text);
  const digest = await window.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
    .slice(0, 8);
}

export function HadiahHatiPanel({ voucherRm, freeCardUnlock }: { voucherRm: number; freeCardUnlock: boolean }) {
  const id = useId();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function onGenerate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const clean = email.trim().toLowerCase();
    if (!EMAIL.test(clean)) {
      setError("Sila masukkan alamat e-mel yang sah.");
      return;
    }
    setError("");
    const prefix = await sha256HexPrefix(clean);
    setCode(`HATI-${prefix}`);
    setCopied(false);
  }

  async function copyCode() {
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  const threadsText = encodeURIComponent(
    `Sertai Hadiah Hati Perpustakaan Hati untuk menang Teman Hidup atau sesi 1-on-1. Kod rujukan saya: ${code || "HATI"} #PerpustakaanHati`,
  );

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-5 p-6">
      <div className="rounded-lg border border-daylight-edge bg-sage/60 p-4 text-sm text-ink-grove">
        <p className="font-medium text-green-900">Cara kumpul penyertaan:</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Muat turun Edisi Poket percuma (1 penyertaan).</li>
          <li>Kongsi keputusan Cermin Pasangan atau Kad Jujur Hati di Threads (1 penyertaan).</li>
          <li>Jemput rakan guna kod rujukan peribadi kamu (1 penyertaan bagi setiap rakan).</li>
        </ul>
      </div>

      <form onSubmit={onGenerate} className="flex flex-col gap-3" noValidate>
        <label htmlFor={`${id}-email`} className="text-sm text-green-900">
          Jana kod rujukan dan voucher RM{voucherRm} kamu
        </label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            id={`${id}-email`}
            type="email"
            placeholder="nama@contoh.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="min-h-tap flex-1 rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
          />
          <button type="submit" className="ph-cta min-h-tap">
            Jana Kod
          </button>
        </div>
        {error && (
          <p role="alert" className="text-sm text-crimson-ink">
            {error}
          </p>
        )}
      </form>

      {code && (
        <div className="rounded-lg border border-gold bg-cream p-4" role="status" aria-live="polite">
          <p className="text-xs uppercase tracking-wider text-muted-grove">Kod Rujukan Kamu</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
            <span className="font-mono text-lg font-medium text-green-900">{code}</span>
            <button type="button" className="btn-ghost min-h-tap" onClick={copyCode}>
              {copied ? "Disalin" : "Salin Kod"}
            </button>
          </div>
          <p className="mt-2 text-xs text-muted-grove">
            Kad refleksi bonus dibuka: {freeCardUnlock ? "Ya" : "Tidak"} · Voucher: RM{voucherRm}
          </p>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <Link href="/kad-jujur-hati" className="ph-cta min-h-tap">
          Buka Kad Refleksi Bonus
        </Link>
        <a
          href={`https://www.threads.net/intent/post?text=${threadsText}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost min-h-tap"
        >
          Kongsi di Threads
        </a>
        <Link href="/beli/membangun" className="btn-ghost min-h-tap">
          Lihat Edisi Membangun
        </Link>
      </div>
    </div>
  );
}
