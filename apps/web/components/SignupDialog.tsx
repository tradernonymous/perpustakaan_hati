"use client";

import { useRef, type ReactNode } from "react";

export function SignupDialog({ children }: { children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);

  return (
    <>
      <button type="button" className="ph-cta min-h-tap w-full justify-center" onClick={() => dialog.current?.showModal()}>
        Daftar &amp; dapatkan Edisi Poket
      </button>
      <dialog ref={dialog} aria-labelledby="reader-signup-title" className="m-auto max-h-[90dvh] w-11/12 max-w-md overflow-y-auto rounded-xl border border-line bg-surface-raised p-5 text-fg shadow-2xl backdrop:bg-black/75 sm:p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 id="reader-signup-title" className="font-display text-2xl">Buka Pustaka Saya</h3>
            <p className="mt-2 text-sm text-fg-muted">Daftar untuk koleksi PDF Edisi Poket percuma.</p>
          </div>
          <button type="button" aria-label="Tutup daftar" className="btn-ghost min-h-tap px-3" onClick={() => dialog.current?.close()}>×</button>
        </div>
        <div className="mt-4">{children}</div>
      </dialog>
    </>
  );
}
