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
