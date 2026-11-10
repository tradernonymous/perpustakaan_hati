"use client";

/*
 * The signed-in admin surface. Astryx lives here and only here: /admin is
 * noindex, low-traffic and never on the storefront path, so the 271 kB Astryx
 * CSS chunk costs nothing a customer would feel.
 */
import { AstryxScope } from "@/src/astryx/AstryxScope";
import { Banner } from "@astryxdesign/core/Banner";
import { Button } from "@astryxdesign/core/Button";
import { Card } from "@astryxdesign/core/Card";

export type ThreadsState = { connected: boolean; username?: string; daysLeft?: number };

export function AdminPanel({ threads }: { threads: ThreadsState }) {
  return (
    <AstryxScope>
      <div style={{ display: "grid", gap: 20, maxWidth: 640 }}>
        {threads.connected ? (
          <Banner
            status="success"
            title={`Threads disambungkan: @${threads.username ?? "rahimam"}`}
            description={`Token sah untuk ${threads.daysLeft ?? 0} hari lagi. Segarkan sebelum tamat.`}
          />
        ) : (
          <Banner
            status="warning"
            title="Threads belum disambungkan"
            description="Sambung akaun Rahimam untuk membuka research dan penerbitan Threads."
          />
        )}

        <Card padding={4}>
          <h2 style={{ margin: "0 0 12px", font: "600 20px/1.3 Georgia, serif" }}>Tindakan</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <Button label="Eksport pelanggan (CSV)" href="/admin/subscribers" />
            <Button
              label={threads.connected ? "Sambung semula Threads" : "Sambung Threads"}
              variant="secondary"
              href="/api/auth/threads/start"
            />
          </div>
        </Card>

        <p style={{ margin: 0, fontSize: 14, color: "var(--muted-grove)" }}>
          Sesi ini tamat dalam 8 jam. Tutup pelayar untuk keluar lebih awal.
        </p>
      </div>
    </AstryxScope>
  );
}