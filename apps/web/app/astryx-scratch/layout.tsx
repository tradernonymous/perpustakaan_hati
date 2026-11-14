import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Astryx Scratch | Perpustakaan Hati",
  robots: { index: false, follow: false },
};

export default function AstryxScratchLayout({ children }: { children: ReactNode }) {
  return children;
}
