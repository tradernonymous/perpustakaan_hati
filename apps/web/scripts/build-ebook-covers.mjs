/**
 * Perpustakaan Hati — A4 ebook cover preview generator.
 *
 * Extracts page 1 from each PDF in docs/brand/preview/ (source PDFs stay
 * outside git tracking) and normalizes every preview into an exact A4 aspect
 * ratio (560x792, 210:297) WebP + JPG fallback inside apps/web/public/ebooks/.
 *
 * Run:
 *     node apps/web/scripts/build-ebook-covers.mjs
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const PREVIEW_DIR = path.join(ROOT, "docs/brand/preview");
const OUT = path.join(ROOT, "apps/web/public/ebooks");
const MANIFEST_TS = path.join(ROOT, "apps/web/src/ebook-covers.ts");

// Exact A4 portrait proportions (210:297 -> 560x792 at ~2x display resolution)
const A4_WIDTH = 560;
const A4_HEIGHT = 792;

const EBOOKS = [
  {
    slug: "ruang-atau-hukuman",
    pdf: "ebook-edisi-poket-ruang-atau-hukuman.pdf",
    title: "Ruang atau Hukuman",
    edition: "Edisi Poket",
    pages: "9 muka surat · A4",
    tagline: "Bila ruang untuk tenang berubah menjadi hukuman tanpa penghujung.",
    summary: "Membezakan diam yang matang untuk bertenang daripada diam yang menghukum pasangan.",
  },
  {
    slug: "perkara-kecil-hati-kenyang",
    pdf: "ebook-edisi-poket-perkara-kecil-hati-kenyang.pdf",
    title: "Perkara Kecil, Hati Kenyang",
    edition: "Edisi Poket",
    pages: "14 muka surat · A4",
    tagline: "Kasih sayang jarang jatuh dari langit. Ia turun setiap hari, dalam perkara kecil.",
    summary: "Panduan praktikal menunjukkan perhatian dan kepekaan melalui gestur harian yang sederhana.",
  },
  {
    slug: "pulang-kepada-suara-sendiri",
    pdf: "ebook-edisi-poket-pulang-kepada-suara-sendiri.pdf",
    title: "Pulang kepada Suara Sendiri",
    edition: "Edisi Poket",
    pages: "14 muka surat · A4",
    tagline: "Selepas putus cinta, suara sendiri tidak hilang. Ia cuma lama tidak diberi ruang.",
    summary: "Panduan lembut memahami pengalaman tidak didengari dan kembali mendengar suara hati sendiri.",
  },
  {
    slug: "cuma-kawan-pejabat",
    pdf: "ebook-edisi-poket-cuma-kawan-pejabat.pdf",
    title: "Cuma Kawan Pejabat",
    edition: "Edisi Poket",
    pages: "13 muka surat · A4",
    tagline: "Bila “cuma kawan” menjadi tempat menyembunyikan apa yang paling dekat.",
    summary: "Mengesan sempadan emosi yang kabur di tempat kerja sebelum ia melukakan pasangan.",
  },
  {
    slug: "tips-psikologi-suami-isteri",
    pdf: "ebook-edisi-poket-tips-psikologi-suami-isteri.pdf",
    title: "Tips Psikologi Suami Isteri",
    edition: "Edisi Poket",
    pages: "10 muka surat · A4",
    tagline: "Karya untuk jiwa yang pernah terluka: “Tulisan yang memulihkan.”",
    summary: "Kompilasi prinsip psikologi perkahwinan untuk meredakan konflik dan membina rasa selamat.",
  },
];

function human(bytes) {
  return bytes < 1024 * 1024 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

async function build() {
  mkdirSync(OUT, { recursive: true });

  const hasSources = EBOOKS.every((e) => existsSync(path.join(PREVIEW_DIR, e.pdf)));
  if (!hasSources) {
    if (existsSync(MANIFEST_TS)) {
      console.log("ebook PDF previews are not in this checkout; rendered covers are already in place");
      return;
    }
    throw new Error(`missing source PDFs in ${PREVIEW_DIR}`);
  }

  for (const entry of readdirSync(OUT)) {
    rmSync(path.join(OUT, entry), { recursive: true, force: true });
  }

  const tmp = mkdtempSync(path.join(tmpdir(), "ph-ebook-covers-"));
  const manifest = [];
  let totalBytes = 0;

  try {
    for (const item of EBOOKS) {
      const pdfPath = path.join(PREVIEW_DIR, item.pdf);
      const prefix = path.join(tmp, item.slug);
      execFileSync("pdftoppm", ["-png", "-f", "1", "-l", "1", "-singlefile", "-r", "150", pdfPath, prefix]);
      const pngPath = `${prefix}.png`;

      // Contain inside exact A4 560x792 forest ground so border details never clip
      const pipeline = sharp(pngPath).resize({
        width: A4_WIDTH,
        height: A4_HEIGHT,
        fit: "contain",
        background: { r: 9, g: 31, b: 20, alpha: 1 },
      });

      const webp = await pipeline.clone().webp({ quality: 82, effort: 6 }).toBuffer();
      const jpg = await pipeline.clone().jpeg({ quality: 84, mozjpeg: true }).toBuffer();

      const webpFile = `${item.slug}-a4.webp`;
      const jpgFile = `${item.slug}-a4.jpg`;
      writeFileSync(path.join(OUT, webpFile), webp);
      writeFileSync(path.join(OUT, jpgFile), jpg);
      totalBytes += webp.length + jpg.length;

      manifest.push({
        slug: item.slug,
        title: item.title,
        edition: item.edition,
        pages: item.pages,
        tagline: item.tagline,
        summary: item.summary,
        width: A4_WIDTH,
        height: A4_HEIGHT,
        webp: `/ebooks/${webpFile}`,
        jpg: `/ebooks/${jpgFile}`,
      });
    }
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }

  const ts = `// Generated by scripts/build-ebook-covers.mjs. Do not edit by hand.
// Run: node apps/web/scripts/build-ebook-covers.mjs

export type EbookCover = {
  slug: string;
  title: string;
  edition: string;
  pages: string;
  tagline: string;
  summary: string;
  width: number;
  height: number;
  webp: string;
  jpg: string;
};

export const EBOOK_COVERS: EbookCover[] = ${JSON.stringify(manifest, null, 2)};
`;
  writeFileSync(MANIFEST_TS, ts);

  console.log(`ebook covers: ${manifest.length} A4 previews (${A4_WIDTH}x${A4_HEIGHT})`);
  for (const m of manifest) {
    console.log(`  ${m.slug.padEnd(32)} ${human(statSync(path.join(OUT, path.basename(m.webp))).size)}`);
  }
  console.log(`total rendered ${human(totalBytes)}`);
}

await build();
