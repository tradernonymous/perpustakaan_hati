"use client";

import { useState } from "react";
import { companionReply } from "@/src/games/teman-hati";

export function TemanHatiChat() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([{ role: "assistant", text: "Hi, aku Teman Hati. Aku di sini untuk dengar. Apa yang kau rasa sekarang?" }]);
  const [input, setInput] = useState("");

  function send() {
    if (!input.trim()) return;
    const reply = companionReply(input);
    setMessages([...messages, { role: "user", text: input }, { role: "assistant", text: reply }]);
    setInput("");
  }

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-3 p-5">
      <div className="flex flex-col gap-2">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "self-end rounded bg-[var(--green-600)] px-3 py-2 text-[var(--forest-night)]" : "self-start rounded border border-[var(--gold)] px-3 py-2 text-ink-grove"}>
            {m.text}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input className="min-h-tap flex-1 rounded border border-daylight-edge bg-sage px-3 text-ink-grove" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Tulis di sini..." />
        <button className="ph-cta min-h-tap" onClick={send}>Hantar</button>
      </div>
    </div>
  );
}
