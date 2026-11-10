"use client";

import { useState, type FormEvent } from "react";
import { companionReply } from "@/src/games/teman-hati";

type Message = { role: "user" | "assistant"; text: string };

const OPENER: Message = { role: "assistant", text: "Hi, aku Teman Hati. Aku di sini untuk dengar. Apa yang kau rasa sekarang?" };

export function TemanHatiChat() {
  const [messages, setMessages] = useState<Message[]>([OPENER]);
  const [input, setInput] = useState("");

  function send(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: "user", text }, { role: "assistant", text: companionReply(text) }]);
    setInput("");
  }

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-3 p-5">
      {/* role=log + aria-live: screen readers hear each new reply without re-reading the transcript. */}
      <div role="log" aria-live="polite" aria-label="Perbualan Teman Hati" className="flex flex-col gap-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "self-end rounded bg-[var(--green-600)] px-3 py-2 text-[var(--forest-night)]"
                : "self-start rounded border border-[var(--gold)] px-3 py-2 text-ink-grove"
            }
          >
            <span className="sr-only">{m.role === "user" ? "Kamu: " : "Teman Hati: "}</span>
            {m.text}
          </div>
        ))}
      </div>

      <form onSubmit={send} className="flex gap-2">
        <label htmlFor="teman-input" className="sr-only">
          Tulis mesej
        </label>
        <input
          id="teman-input"
          className="min-h-tap flex-1 rounded border border-daylight-edge bg-sage px-3 text-ink-grove"
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