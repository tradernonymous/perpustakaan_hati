import { notFound } from "next/navigation";
import { temanHatiEnabled } from "@/src/feature-flags";
import type { Metadata } from "next";
import { TemanHatiChat } from "@/components/TemanHatiChat";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = { title: "Teman Hati | Perpustakaan Hati" };

export default function Page() {
  if (!temanHatiEnabled) notFound();
  return (
    <PageShell title="Teman Hati" intro="Rakan AI 24/7 dalam Bahasa Melayu dan English. Jika kamu dalam krisis, sila hubungi Talian HEAL 15555.">
      <TemanHatiChat />
    </PageShell>
  );
}
