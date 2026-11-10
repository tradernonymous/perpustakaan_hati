"use client";

/*
 * Astryx spike — throwaway route. Not linked from anywhere.
 * Proves: precompiled CSS import, Theme provider, and five components render
 * under Next 16 + Turbopack without a StyleX compiler.
 */
import { useState } from "react";
import { AstryxScope } from "@/src/astryx/AstryxScope";
import { Button } from "@astryxdesign/core/Button";
import { Collapsible } from "@astryxdesign/core/Collapsible";
import { Dialog } from "@astryxdesign/core/Dialog";
import { ProgressBar } from "@astryxdesign/core/ProgressBar";
import { Tab, TabList } from "@astryxdesign/core/TabList";
import { Tooltip } from "@astryxdesign/core/Tooltip";

export default function AstryxScratch() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState("satu");

  return (
    <AstryxScope>
      <main style={{ padding: 32, display: "grid", gap: 24, maxWidth: 720 }}>
        <h1 style={{ font: "600 28px/1.2 Georgia, serif" }}>Astryx spike</h1>

        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <Button label="Buka dialog" onClick={() => setOpen(true)} />
          <Tooltip content="Petua ringkas">
            <Button label="Hover saya" variant="secondary" />
          </Tooltip>
        </div>

        <TabList value={tab} onChange={setTab} aria-label="Contoh tab">
          <Tab value="satu" label="Satu" />
          <Tab value="dua" label="Dua" />
        </TabList>
        <p>Tab dipilih: {tab}</p>

        <Collapsible trigger="Soalan lazim">
          <p>Jawapan ringkas untuk menguji buka dan tutup.</p>
        </Collapsible>

        <ProgressBar value={42} max={100} label="Kemajuan bacaan" hasValueLabel />

        <Dialog isOpen={open} onOpenChange={setOpen} purpose="info">
          <h2 style={{ margin: 0, font: "600 20px/1.3 Georgia, serif" }}>Dialog Astryx</h2>
          <p style={{ margin: "8px 0 0" }}>Escape menutup, fokus kembali ke butang.</p>
        </Dialog>
      </main>
    </AstryxScope>
  );
}
