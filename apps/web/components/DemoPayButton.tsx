"use client";

import { useState } from "react";

export function DemoPayButton({ orderId }: { orderId: string }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function pay() {
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/demo/pay", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ order: orderId }),
      });
      if (!res.ok) {
        setError("Bayaran demo gagal. Cuba lagi sebentar.");
        setBusy(false);
        return;
      }
      window.location.assign(`/terima-kasih?order=${orderId}`);
    } catch {
      setError("Tiada sambungan internet. Cuba lagi sebentar.");
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <button type="button" onClick={pay} disabled={busy} className="ph-cta min-h-cta-mobile items-center justify-center disabled:opacity-60">
        {busy ? "Memproses..." : "Bayar (demo)"}
      </button>
      <p aria-live="polite" role="status" className="text-burgundy-light">{error}</p>
    </div>
  );
}
