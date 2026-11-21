"use client";

import { useRef, useState } from "react";

export function ShowcaseControls() {
  const dialog = useRef<HTMLDialogElement>(null);
  const [tab, setTab] = useState("Semua");
  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap gap-2" aria-label="Penapis contoh">
        {["Semua", "Edisi Poket", "Teman Hidup"].map((label) => (
          <button key={label} type="button" aria-pressed={label === tab}
            className={label === tab ? "ph-cta" : "btn-ghost"} onClick={() => setTab(label)}>
            {label}
          </button>
        ))}
      </div>
      <p role="status" className="text-sm text-fg-muted">Penapis aktif: {tab}</p>
      <div>
        <button type="button" className="btn-ghost" onClick={() => dialog.current?.showModal()}>Buka dialog</button>
      </div>
      <dialog ref={dialog} aria-labelledby="showcase-dialog-title"
        className="ph-card m-auto w-[calc(100%-2rem)] max-w-sm p-6 backdrop:bg-black/70">
        <h3 id="showcase-dialog-title" className="ph-title text-2xl">Simpan pilihan bacaan?</h3>
        <p className="my-4 text-fg-muted">Contoh dialog interaktif untuk semakan komponen.</p>
        <form method="dialog" className="flex flex-wrap gap-2">
          <button className="btn-ghost" value="batal">Batal</button>
          <button className="ph-cta" value="simpan">Simpan</button>
        </form>
      </dialog>
    </div>
  );
}
