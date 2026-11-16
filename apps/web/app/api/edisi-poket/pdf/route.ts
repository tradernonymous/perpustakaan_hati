import { readFile } from "node:fs/promises";
import path from "node:path";
import { placeholderPdf } from "@/src/server/watermark";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FILENAME = "edisi-poket-perpustakaan-hati.pdf";

async function loadPocketPdf(): Promise<Uint8Array> {
  const assetsDir = process.env.ASSETS_DIR ?? path.join(process.env.DATA_DIR ?? "./data", "assets");
  const candidates = [
    // An operator may mount the book on the persistent volume.
    path.join(assetsDir, "edisi-poket.pdf"),
    // The build artefact, when the whole repo is present.
    path.resolve(process.cwd(), "../../content/ebooks/tier-1-free/edisi-poket.pdf"),
    // The shipped copy inside the image (public/ is copied into the image).
    path.resolve(process.cwd(), "public/ebooks/edisi-poket.pdf"),
  ];

  for (const candidate of candidates) {
    try {
      const buf = await readFile(/*turbopackIgnore: true*/ candidate);
      if (buf.byteLength > 0) return buf;
    } catch {
      // Try next location before falling back to generated placeholder.
    }
  }

  return placeholderPdf("Edisi Poket: Seni Merawat Luka Hati");
}

/** Public PDF endpoint for the free Edisi Poket edition. */
export async function GET() {
  const bytes = await loadPocketPdf();
  return new Response(Buffer.from(bytes), {
    status: 200,
    headers: {
      "content-type": "application/pdf",
      "content-disposition": `attachment; filename="${FILENAME}"`,
      "cache-control": "private, max-age=300",
      "x-robots-tag": "noindex",
    },
  });
}
