"use client";

import { useState } from "react";
import { QUESTIONS, scoreCermin, verdictFor } from "@/src/games/cermin";

export function CerminPasangan() {
  const [answers, setAnswers] = useState<number[]>([]);
  const [done, setDone] = useState(false);
  const score = scoreCermin(answers);
  const verdict = verdictFor(score);

  if (done) {
    return (
      <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
        <h3 className="font-display text-xl text-green-900">Peta Hubungan kamu</h3>
        <p>Skor: {score} / {QUESTIONS.length * 2}</p>
        <p>Verdict: {verdict === "cermin-clear" ? "Cermin jelas — teruskan perbualan yang jujur." : verdict === "warm-up" ? "Pemanasan — ada ruang untuk lebih dengar." : "Perlu perhatian lembut — cuba satu skrip hari ini."}</p>
        <p className="text-sm text-muted-grove">Screenshot kad ini dan kongsi di Threads dengan #CerminPasangan</p>
      </div>
    );
  }

  const q = QUESTIONS[answers.length];
  if (!q) return null;

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-5">
      <p className="text-sm text-green-900">Cermin Pasangan — Soalan {answers.length + 1} / {QUESTIONS.length}</p>
      <p className="text-ink-grove">{q.text}</p>
      <div className="flex flex-col gap-2">
        {q.options.map((o) => (
          <button key={o.label} className="ph-cta min-h-tap justify-start" onClick={() => setAnswers([...answers, o.score])}>
            {o.label}
          </button>
        ))}
      </div>
      {answers.length === QUESTIONS.length && (
        <button className="ph-cta min-h-tap" onClick={() => setDone(true)}>Lihat Peta Hubungan</button>
      )}
    </div>
  );
}
