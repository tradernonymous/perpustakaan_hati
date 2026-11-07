import type { Metadata, Viewport } from "next";
import "./globals.css";

const title = "Perpustakaan Hati | Karya untuk jiwa yang pernah terluka";
const description =
  "Bahan bacaan psikologi hubungan dalam Bahasa Melayu oleh Rahimam. Mulakan dengan Edisi Poket, percuma.";

export const metadata: Metadata = {
  title,
  description,
  openGraph: { title, description, locale: "ms_MY", type: "website", siteName: "Perpustakaan Hati" },
  icons: { icon: "/brand/monogram-stamp.svg" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#07140d",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ms">
      <body>{children}</body>
    </html>
  );
}
