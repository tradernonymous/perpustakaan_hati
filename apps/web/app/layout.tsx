import type { Metadata, Viewport } from "next";
import { headers } from "next/headers";
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
    images: [
      { url: "/brand/og-image.png", width: 1200, height: 630, alt: "Perpustakaan Hati oleh @rahimam" },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: ["/brand/og-image.png"],
  },
  icons: { icon: "/brand/monogram-stamp.svg" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f7f4ea",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Reading x-nonce subscribes the shell to per-request CSP nonces from proxy.ts
  // so Next.js attaches the nonce to hydration scripts instead of relying on 'unsafe-inline'.
  await headers();
  return (
    <html lang="ms">
      <body className="ph-daylight">{children}</body>
    </html>
  );
}
