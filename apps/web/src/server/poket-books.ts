import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { EBOOK_COVERS } from "../ebook-covers";

export const POKET_BOOKS = [
  { slug: "edisi-poket", title: "Edisi Poket", file: "edisi-poket.pdf" },
  ...EBOOK_COVERS.map(({ slug, title }) => ({
    slug,
    title,
    file: `ebook-edisi-poket-${slug}${slug === "cuma-kawan-pejabat" ? "-slim" : ""}.pdf`,
  })),
];

function bookDirectories() {
  const assets = process.env.ASSETS_DIR ?? path.resolve(process.env.DATA_DIR ?? "./data", "assets");
  return [assets, path.resolve("private/ebooks"), path.resolve("../../docs/brand/preview")];
}

async function hasPocketFile(file: string): Promise<boolean> {
  for (const dir of bookDirectories()) {
    try {
      await access(path.join(dir, file));
      return true;
    } catch {
      continue;
    }
  }
  return false;
}

export async function listPocketBooks() {
  return Promise.all(POKET_BOOKS.map(async (book) => ({
    ...book,
    available: await hasPocketFile(book.file),
  })));
}

export async function pocketDownload(slug: string): Promise<Response> {
  const book = POKET_BOOKS.find((item) => item.slug === slug);
  if (!book) return new Response(null, { status: 404 });
  for (const dir of bookDirectories()) {
    const filename = path.join(dir, book.file);
    try {
      const bytes = await readFile(/*turbopackIgnore: true*/ filename);
      return new Response(new Uint8Array(bytes), {
        headers: {
          "content-type": "application/pdf",
          "content-disposition": `attachment; filename="${book.file}"`,
          "cache-control": "private, no-store",
          "x-robots-tag": "noindex",
        },
      });
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
    }
  }
  return new Response("Fail buku belum tersedia.", { status: 404 });
}
