"use client";

import { useState, type FormEvent } from "react";
import { companionReply, guardrails, isCrisis, needsCounsellor } from "@/src/games/teman-hati";

type Message = { role: "user" | "assistant"; text: string };

const OPENER: Message = {
  role: "assistant",
  text: "Hi, aku Teman Hati. Aku di sini untuk dengar. Apa yang kau rasa sekarang?",
};

const QUICK_PROMPTS = [
  "Aku penat bila pasangan buat silent treatment",
  "Macam mana nak tahu ini red flag atau aku sensitif?",
  "Aku rasa tak cukup dan takut ditinggalkan",
];

export function TemanHatiChat() {
  const [messages, setMessages] = useState<Message[]>([OPENER]);
  const [input, setInput] = useState("");
  const [showGuardrails, setShowGuardrails] = useState(false);

  function submitMessage(rawText: string) {
    const text = rawText.trim();
    if (!text) return;
    if (isCrisis(text) || needsCounsellor(text)) {
      setShowGuardrails(true);
    }
    setMessages((prev) => [...prev, { role: "user", text }, { role: "assistant", text: companionReply(text) }]);
    setInput("");
  }

  function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    submitMessage(input);
  }

  return (
    <div className="ph-nightlight ph-companion mx-auto flex max-w-reading flex-col gap-4 rounded-xl p-5 shadow-lift">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gold/25 pb-3">
        <span className="ph-kicker text-xs uppercase tracking-widest">Mod Cahaya Malam · Perbualan Selamat</span>
        <span className="text-xs text-muted-cream/80">{guardrails[0]}</span>
      </div>

      {/* role=log + aria-live: screen readers hear each new reply without re-reading the transcript. */}
      <div role="log" aria-live="polite" aria-label="Perbualan Teman Hati" className="flex flex-col gap-2.5">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "bubble-user self-end rounded-xl px-3.5 py-2.5 text-sm leading-relaxed"
                : "bubble-assistant self-start rounded-xl px-3.5 py-2.5 text-sm leading-relaxed text-cream"
            }
          >
            <span className="sr-only">{m.role === "user" ? "Kamu: " : "Teman Hati: "}</span>
            {m.text}
          </div>
        ))}
      </div>

      {showGuardrails && (
        <div className="rounded-lg border border-gold bg-forest-raised p-3 text-xs text-cream" role="region" aria-label="Bantuan segera">
          <p className="font-medium">Jika kamu memerlukan bantuan segera:</p>
          <div className="mt-2 flex flex-wrap gap-3">
            <a href="tel:15555" className="underline underline-offset-4">
              Hubungi Talian HEAL 15555
            </a>
            <a href="tel:0376272929" className="underline underline-offset-4">
              Befrienders KL: 03-7627 2929
            </a>
            <a href="tel:999" className="underline underline-offset-4">
              Kecemasan: 999
            </a>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2" aria-label="Cadangan pemula perbualan">
        {QUICK_PROMPTS.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => submitMessage(q)}
            className="min-h-tap rounded-full border border-gold/30 bg-forest-raised px-3 py-1.5 text-left text-xs text-cream transition hover:border-gold"
          >
            {q}
          </button>
        ))}
      </div>

      <form onSubmit={send} className="flex gap-2">
        <label htmlFor="teman-input" className="sr-only">
          Tulis mesej
        </label>
        <input
          id="teman-input"
          className="min-h-tap flex-1 rounded border border-gold/35 bg-forest-raised px-3 text-cream placeholder:text-cream/60"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Tulis di sini..."
        />
        <button type="submit" className="ph-cta min-h-tap">
          Hantar
        </button>
      </form>
    </div>
  );
}
