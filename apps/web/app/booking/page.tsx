import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { BookingForm } from "@/components/BookingForm";

export const metadata: Metadata = { title: "Booking Kaunseling | Perpustakaan Hati" };

export default function Page() {
  return (
    <PageShell title="Booking Kaunseling" intro="Sesi 1-on-1 dan pasangan dengan kaunselor berlesen di bawah Perpustakaan Hati. RM150–350+ per sesi.">
      <BookingForm />
    </PageShell>
  );
}
