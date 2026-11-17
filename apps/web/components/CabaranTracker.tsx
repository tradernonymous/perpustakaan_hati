"use client";

import { useEffect, useState } from "react";
import type { CabaranDay } from "@/src/games/cabaran";

const STORAGE_KEY = "ph_cabaran_7_hari_v1";

export function CabaranTracker({ days }: { days: CabaranDay[] }) {
  const [completed, setCompleted] = useState<number[]>([]);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) setCompleted(parsed.filter((n) => typeof n === "number"));
      }
    } catch {
      // Ignore storage errors in private mode.
    }
  }, []);

  function toggleDay(day: number) {
    setCompleted((prev) => {
      const next = prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day].sort((a, b) => a - b);
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // Ignore storage errors in private mode.
      }
      return next;
    });
  }

  const pct = Math.round((completed.length / Math.max(1, days.length)) * 100);
  const threadsText = encodeURIComponent(
    `Hari ini aku sudah tanda ${completed.length}/${days.length} dalam 7 Hari Cabaran Pulih Hati. #CabaranPulihHati`,
  );

  return (
    <div className="mx-auto flex max-w-reading flex-col gap-4">
      <div className="ph-card flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="font-display text-lg text-fg">
            Kemajuan kamu: {completed.length} / {days.length} hari ({pct}%)
          </p>
          <p className="text-xs text-fg-muted">Disimpan dalam pelayar kamu secara peribadi.</p>
        </div>
        <a
          href={`https://www.threads.net/intent/post?text=${threadsText}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-ghost min-h-tap"
        >
          Kongsi di Threads
        </a>
      </div>

      <ol className="flex flex-col gap-3">
        {days.map((d) => {
          const checked = completed.includes(d.day);
          const inputId = `cabaran-day-${d.day}`;
          return (
            <li key={d.day} className={`ph-card p-4 transition ${checked ? "border-green-700 bg-surface-soft" : ""}`}>
              <div className="flex items-start gap-3">
                <input
                  id={inputId}
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleDay(d.day)}
                  className="mt-1 h-5 w-5 accent-green-700"
                />
                <label htmlFor={inputId} className="flex-1 cursor-pointer">
                  <p className="font-display text-fg">
                    Hari {d.day} {checked ? "(Selesai)" : ""}
                  </p>
                  <p className="text-fg">{d.prompt}</p>
                  <p className="mt-1 text-sm text-fg-muted">{d.action}</p>
                </label>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
