"use client";

import Link from "next/link";
import { useState } from "react";
import { QUESTIONS, scoreCermin, verdictFor } from "@/src/games/cermin";

const VERDICT_COPY = {
  "cermin-clear": {
    badge: "Cermin Jelas",
    headline: "Komunikasi kamu stabil dan terbuka.",
    detail: "Kamu cenderung mendengar dahulu dan meluahkan rasa tanpa menghukum. Teruskan perbualan jujur dengan pasangan.",
    nextHref: "/#edisi",
    nextLabel: "Lihat Edisi Teman Hidup",
  },
  "warm-up": {
    badge: "Dalam Pemanasan",
    headline: "Ada asas baik, namun masih ada ruang untuk lebih tenang.",
    detail: "Sesetengah situasi buat kamu berhati-hati atau menahan rasa. Skrip ayat pertama dalam eBook boleh bantu mula bercakap.",
    nextHref: "/#edisi",
    nextLabel: "Teroka Edisi Membangun",
  },
  "need-care": {
    badge: "Perlu Perhatian Lembut",
    headline: "Kamu mungkin sedang memikul banyak perkara sendirian.",
    detail: "Cuba satu langkah kecil hari ini: pilih satu ayat lembut atau pertimbang sesi 1-on-1 untuk ruang selamat.",
    nextHref: "/booking",
    nextLabel: "Lihat Sesi Kaunseling 1-on-1",
  },
} as const;

export function CerminPasangan() {
  const [answers, setAnswers] = useState<number[]>([]);
  const [done, setDone] = useState(false);
  const [copied, setCopied] = useState(false);

  const score = scoreCermin(answers);
  const maxScore = QUESTIONS.length * 2;
  const verdict = verdictFor(score);

  function choose(optionScore: number) {
    const next = [...answers, optionScore];
    setAnswers(next);
    if (next.length >= QUESTIONS.length) {
      setDone(true);
    }
  }

  function reset() {
    setAnswers([]);
    setDone(false);
    setCopied(false);
  }

  async function copyChallengeLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  const q = QUESTIONS[answers.length];
  if (done || !q) {
    const copy = VERDICT_COPY[verdict];
    const threadsText = encodeURIComponent(
      `Baru cuba Cermin Pasangan di Perpustakaan Hati: ${copy.badge} (${score}/${maxScore}). Cuba dengan pasangan di https://web-production-0cfb9.up.railway.app/cermin-pasangan #CerminPasangan`,
    );

    return (
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-6" role="status" aria-live="polite">
        <span className="inline-block w-fit rounded-full bg-sage px-3 py-1 text-xs font-medium uppercase tracking-wider text-green-900">
          {copy.badge}
        </span>
        <h3 className="font-display text-2xl text-green-900">Peta Hubungan kamu</h3>
        <p className="font-mono text-sm text-green-900">
          Skor: {score} / {maxScore}
        </p>
        <p className="font-medium text-ink-grove">{copy.headline}</p>
        <p className="text-sm text-muted-grove">{copy.detail}</p>

        <div className="flex flex-wrap gap-3 pt-2">
          <a
            href={`https://www.threads.net/intent/post?text=${threadsText}`}
            target="_blank"
            rel="noopener noreferrer"
            className="ph-cta min-h-tap"
          >
            Kongsi di Threads (#CerminPasangan)
          </a>
          <button type="button" className="btn-ghost min-h-tap" onClick={copyChallengeLink}>
            {copied ? "Pautan disalin" : "Salin pautan untuk pasangan"}
          </button>
          <Link href={copy.nextHref} className="btn-ghost min-h-tap">
            {copy.nextLabel}
          </Link>
          <button type="button" className="btn-ghost min-h-tap" onClick={reset}>
            Ulang semula
          </button>
        </div>
      </div>
    );
  }

  const progressPct = Math.round(((answers.length + 1) / QUESTIONS.length) * 100);

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-6">
      <div className="flex items-center justify-between gap-2 text-sm text-green-900">
        <span>
          Cermin Pasangan, soalan {answers.length + 1} / {QUESTIONS.length}
        </span>
        <span className="font-mono text-xs text-muted-grove">{progressPct}%</span>
      </div>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-sage" aria-hidden="true">
        <div
          className="h-full rounded-full bg-green-700 transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <p className="font-display text-lg text-ink-grove">{q.text}</p>

      <div className="flex flex-col gap-2.5">
        {q.options.map((o) => (
          <button
            key={o.label}
            type="button"
            className="btn-ghost min-h-tap w-full justify-start text-left"
            onClick={() => choose(o.score)}
          >
            {o.label}
          </button>
        ))}
      </div>

      {answers.length > 0 && (
        <div className="flex justify-between pt-2">
          <button
            type="button"
            className="text-sm text-green-800 underline underline-offset-4 hover:text-green-900"
            onClick={() => setAnswers((prev) => prev.slice(0, -1))}
          >
            Undur ke soalan sebelum
          </button>
        </div>
      )}
    </div>
  );
}
