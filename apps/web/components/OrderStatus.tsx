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
    <div className="ph-card mx-auto flex max-w-reading flex-col gap-3 p-6 text-center" aria-live="polite">
      {status === "paid" && (
        <>
          <p className="font-display text-2xl text-gold-light">Pembayaran diterima. Terima kasih.</p>
          <p>Pautan muat turun sudah dihantar ke e-mel kamu (dan WhatsApp jika diisi). Semak juga folder spam.</p>
          <a href="/pustaka" className="btn-ghost mx-auto min-h-tap">Buka Pustaka Saya</a>
        </>
      )}
      {status === "pending" && (
        <>
          <p className="font-display text-2xl text-gold-light">Menunggu pengesahan bank...</p>
          <p>Biasanya dalam beberapa saat. Jangan tutup halaman ini.</p>
        </>
      )}
      {status === "missing" && <p>Pesanan tidak dijumpai. Jika kamu sudah membayar, e-mel kami dan sertakan nombor rujukan bank.</p>}
    </div>
  );
}
