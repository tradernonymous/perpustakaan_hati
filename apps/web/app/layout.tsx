import type { Metadata, Viewport } from "next";
import "./globals.css";
import { siteUrl } from "@/src/site";

const title = "Perpustakaan Hati | Karya untuk jiwa yang pernah terluka";
const description =
  "Bahan bacaan psikologi hubungan dalam Bahasa Melayu oleh Rahimam. Mulakan dengan Edisi Poket, percuma.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title,
  description,
  openGraph: {
    title,
    description,
    locale: "ms_MY",
    type: "website",
    siteName: "Perpustakaan Hati",
    images: [{ url: "/brand/emblem-book-heart.svg", width: 600, height: 420, alt: "Perpustakaan Hati oleh @rahimam" }],
  },
  twitter: {
    card: "summary",
    title,
    description,
    images: ["/brand/emblem-book-heart.svg"],
  },
  icons: { icon: "/brand/monogram-stamp.svg" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f7f4ea",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ms">
      <body className="ph-daylight">{children}</body>
    </html>
  );
}
