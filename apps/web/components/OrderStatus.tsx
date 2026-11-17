"use client";

import { useEffect, useState } from "react";

export function OrderStatus({ orderId }: { orderId: string }) {
  const [status, setStatus] = useState<"pending" | "paid" | "missing">("pending");

  useEffect(() => {
    let stop = false;
    let tries = 0;
    async function poll() {
      try {
        const res = await fetch(`/api/orders/${orderId}/status`, { cache: "no-store" });
        if (res.status === 404) return !stop && setStatus("missing");
        const data = (await res.json()) as { status: "pending" | "paid" };
        if (!stop) setStatus(data.status);
        if (data.status === "paid") return;
      } catch { /* retry */ }
      if (!stop && ++tries < 40) setTimeout(poll, 3000);
    }
    poll();
    return () => { stop = true; };
  }, [orderId]);

  return (
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-4 p-6 text-center" aria-live="polite">
      {status === "paid" && (
        <>
          <p className="font-display text-2xl text-fg">Pembayaran diterima. Terima kasih.</p>
          <p className="text-fg">Pautan muat turun sudah dihantar ke e-mel kamu (dan WhatsApp jika diisi). Semak juga folder spam.</p>
          <div className="flex flex-wrap justify-center gap-3">
            <a href="/pustaka" className="ph-cta min-h-tap">Buka Pustaka Saya</a>
            <a href="/#edisi" className="btn-ghost min-h-tap">Kembali ke laman utama</a>
          </div>
        </>
      )}
      {status === "pending" && (
        <>
          <p className="font-display text-2xl text-fg">Menunggu pengesahan bank...</p>
          <p className="text-fg">Biasanya dalam beberapa saat. Jangan tutup halaman ini.</p>
          <div className="mx-auto h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-surface-soft" aria-hidden="true">
            <div className="animate-heal-travel h-full w-1/3 rounded-full bg-green-700" />
          </div>
          <p className="text-xs text-fg-muted">
            Jika sudah selesai membayar tetapi belum dikemas kini selepas 1 minit, semak <a href="/pustaka" className="underline">Pustaka Saya</a> menggunakan e-mel pesanan kamu.
          </p>
        </>
      )}
      {status === "missing" && (
        <>
          <p className="text-fg">Pesanan tidak dijumpai. Jika kamu sudah membayar, semak <a href="/pustaka" className="underline">Pustaka Saya</a> atau e-mel kami dengan nombor rujukan bank.</p>
        </>
      )}
    </div>
  );
}
