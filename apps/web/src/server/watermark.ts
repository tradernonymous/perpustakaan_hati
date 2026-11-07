import { PDFDocument, StandardFonts, degrees, rgb } from "pdf-lib";

// Standard PDF fonts only cover Latin-1, so anything else becomes "?" rather than crashing.
const latin1 = (s: string) => s.replace(/[^\x20-\x7e\xa0-\xff]/g, "?");

/** Stamps the buyer on every page: a faint diagonal mark plus a footer line. Deters casual sharing. */
export async function watermarkPdf(bytes: Uint8Array, text: string): Promise<Uint8Array> {
  const doc = await PDFDocument.load(bytes);
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const label = latin1(text);
  for (const page of doc.getPages()) {
    const { width, height } = page.getSize();
    page.drawText(label, { x: width * 0.12, y: height * 0.3, size: Math.max(14, width / 28), font, color: rgb(0.45, 0.45, 0.45), opacity: 0.16, rotate: degrees(35) });
    page.drawText(label, { x: 24, y: 14, size: 7, font, color: rgb(0.4, 0.4, 0.4), opacity: 0.7 });
  }
  return doc.save();
}

/**
 * Builds a clearly-marked stand-in PDF for a product whose real file is not
 * ready yet. It is stamped like a real download, so the buyer sees the same
 * thing they would get from the real book.
 */
export async function placeholderPdf(productName: string): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  const font = await doc.embedFont(StandardFonts.Helvetica);
  const bold = await doc.embedFont(StandardFonts.HelveticaBold);
  const page = doc.addPage([595, 842]);
  const { width, height } = page.getSize();

  page.drawRectangle({ x: 0, y: height - 120, width, height: 120, color: rgb(0.06, 0.15, 0.11) });
  page.drawText(latin1(productName), { x: 48, y: height - 70, size: 26, font: bold, color: rgb(0.85, 0.7, 0.3) });
  page.drawText("Perpustakaan Hati", { x: 48, y: height - 96, size: 12, font, color: rgb(0.85, 0.85, 0.8) });

  const lines = [
    "This is a placeholder file.",
    "The final book is still being prepared.",
    "Please check back soon for the real PDF.",
    "",
    "Placeholder ini hanyalah fail sementara.",
    "Buku akhir sedang disiapkan.",
  ];
  lines.forEach((l, i) => {
    page.drawText(latin1(l), { x: 48, y: height - 180 - i * 20, size: 13, font, color: rgb(0.15, 0.15, 0.15) });
  });

  page.drawRectangle({ x: 48, y: 120, width: width - 96, height: 44, borderColor: rgb(0.8, 0.2, 0.2), borderWidth: 2 });
  page.drawText("PLACEHOLDER - NOT THE REAL BOOK", { x: 62, y: 136, size: 13, font: bold, color: rgb(0.8, 0.2, 0.2) });

  page.drawText("Perpustakaan Hati", { x: 48, y: 60, size: 10, font, color: rgb(0.4, 0.4, 0.4) });
  return doc.save();
}
