/**
 * Perpustakaan Hati — responsive illustration pipeline.
 *
 * The six painterly illustrations for Edisi Poket live in
 * docs/brand/illustrations/edisi-poket-kehilangan/. The originals are
 * 1600px PNGs at 8-12 MB each; the intermediate compressed/ folders are
 * still 350-870 KB per JPEG. Shipping those to a phone on a slow
 * Malaysian connection is the worst performance problem on the site, so
 * this script renders the sanctioned source into WebP at three widths
 * plus one JPEG fallback.
 *
 * Why not next/image: its production optimizer needs sharp installed at
 * runtime, and sharp is a devDependency in this app, so a Railway deploy
 * would fail to serve optimized images. Pre-rendered files are static,
 * cost nothing to serve, and are already smaller than the optimizer would
 * produce.
 *
 * Widths: 480 (phones), 768 (large phones / small tablets), 1200
 * (desktop hero). No 1600 variant: nothing on the site displays an
 * illustration wider than ~620 CSS px, so 1200 is already 2x on desktop.
 *
 * Run:
 *     node apps/web/scripts/build-illustrations.mjs
 *
 * Output:
 *     apps/web/public/illustrations/<slug>-<width>.webp
 *     apps/web/public/illustrations/<slug>-768.jpg   (fallback only)
 *     apps/web/src/illustrations.ts                   (typed manifest)
 */
import { existsSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import sharp from "sharp";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const ART = path.join(ROOT, "docs/brand/illustrations/edisi-poket-kehilangan");
const SOURCE_DIRS = [path.join(ART, "compressed_jpg"), path.join(ART, "compressed")];
const OUT = path.join(ROOT, "apps/web/public/illustrations");
const MANIFEST_TS = path.join(ROOT, "apps/web/src/illustrations.ts");

const WIDTHS = [480, 768, 1200];
const WEBP_QUALITY = 70;
const JPEG_QUALITY = 78;

/**
 * The six illustrations, with the caption the site shows beside them.
 * `alt` describes the picture, not the feeling, so a screen reader gets
 * something useful. Captions follow the brand copy rules: no em dash,
 * Malay sentence case.
 */
const ILLUSTRATIONS = [
  {
    slug: "dua-kerusi",
    file: "01-dua-kerusi.jpg",
    alt: "Dua kerusi kayu menghadap satu sama lain dalam cahaya senja",
    caption: "Dua kerusi, satu jarak yang belum berani dekat.",
  },
  {
    slug: "hujan-tetingkap",
    file: "02-hujan-tetingkap.jpg",
    alt: "Tetesan hujan menuruni tingkap berkabus",
    caption: "Kadang-kadang yang kita cari bukan jawapan, tetapi ketenangan.",
  },
  {
    slug: "tali-longgar",
    file: "03-tali-longgar.jpg",
    alt: "Tali yang longgar di tepi jambatan kecil",
    caption: "Longgar bukan salah. Ada sesuatu yang belum siap dilepaskan.",
  },
  {
    slug: "lampu-bilik",
    file: "04-lampu-bilik.jpg",
    alt: "Lampu bilik yang menyala hangat dalam bilik kosong",
    caption: "Lampu dibiarkan menyala, walaupun tiada siapa yang kembali.",
  },
  {
    slug: "tangan-hampir",
    file: "05-tangan-hampir.jpg",
    alt: "Dua tangan yang saling menghampiri tanpa menyentuh",
    caption: "Hampir-hampir sudah cukup, untuk kali ini.",
  },
  {
    slug: "jambatan-kecil",
    file: "06-jambatan-kecil.jpg",
    alt: "Jambatan kecil yang menyeberang air gelap",
    caption: "Jambatan kecil, tetapi tetap menyeberang.",
  },
];

function human(bytes) {
  return bytes < 1024 * 1024 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function findSource(file) {
  for (const dir of SOURCE_DIRS) {
    const p = path.join(dir, file);
    if (existsSync(p)) return p;
  }
  throw new Error(`missing illustration source: ${file} (looked in ${SOURCE_DIRS.join(", ")})`);
}

async function build() {
  mkdirSync(OUT, { recursive: true });

  // The source paintings are large (79 MB) and are not kept in the repo,
  // so a fresh clone has no source to render from. The rendered files are
  // committed, so that case is a no-op rather than a failure.
  if (!SOURCE_DIRS.some((d) => existsSync(d))) {
    if (existsSync(path.join(OUT, "manifest.json"))) {
      console.log("illustration sources are not in this checkout; the rendered files are already in place");
      return;
    }
    throw new Error(`no illustration source in ${SOURCE_DIRS.join(", ")} and no rendered output in ${OUT}`);
  }

  const manifest = [];
  let rendered = 0;

  for (const item of ILLUSTRATIONS) {
    const src = findSource(item.file);
    const meta = await sharp(src).metadata();

    const variants = [];
    for (const width of WIDTHS) {
      if (width > meta.width) continue;
      const base = path.join(OUT, `${item.slug}-${width}`);

      const webp = await sharp(src)
        .rotate()
        .resize({ width, withoutEnlargement: true })
        .webp({ quality: WEBP_QUALITY, effort: 6 })
        .toBuffer();
      writeFileSync(`${base}.webp`, webp);
      rendered += webp.length;

      // One JPEG fallback for the one browser family that still lacks
      // WebP (very old Android WebView). 768 is enough for that case.
      if (width === 768) {
        const jpg = await sharp(src)
          .rotate()
          .resize({ width, withoutEnlargement: true })
          .jpeg({ quality: JPEG_QUALITY, mozjpeg: true })
          .toBuffer();
        writeFileSync(`${base}.jpg`, jpg);
        rendered += jpg.length;
      }

      variants.push({ width, webp: `${item.slug}-${width}.webp` });
    }

    manifest.push({
      slug: item.slug,
      alt: item.alt,
      caption: item.caption,
      width: meta.width,
      height: meta.height,
      variants,
    });
  }

  writeFileSync(path.join(OUT, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);

  // Typed manifest for the app. Kept in src/ (not public/) so components
  // can import it and get types, and so a stale image path fails the
  // TypeScript build instead of 404ing in the browser.
  const ts = `// Generated by scripts/build-illustrations.mjs. Do not edit by hand.
// Run: node apps/web/scripts/build-illustrations.mjs

export type IllustrationVariant = { width: number; webp: string };

export type Illustration = {
  slug: string;
  alt: string;
  caption: string;
  width: number;
  height: number;
  variants: IllustrationVariant[];
};

export const ILLUSTRATIONS: Illustration[] = ${JSON.stringify(manifest, null, 2)};

export function illustrationBySlug(slug: string): Illustration {
  const found = ILLUSTRATIONS.find((i) => i.slug === slug);
  if (!found) throw new Error(\`unknown illustration: \${slug}\`);
  return found;
}
`;
  writeFileSync(MANIFEST_TS, ts);

  console.log(`illustrations: ${manifest.length} images`);
  for (const m of manifest) {
    const sizes = m.variants
      .map((v) => `${v.width}:${human(statSync(path.join(OUT, v.webp)).size)}`)
      .join("  ");
    console.log(`  ${m.slug.padEnd(16)} ${m.width}x${m.height}  ${sizes}`);
  }
  console.log(`total rendered ${human(rendered)}`);
  console.log(`manifest: ${path.relative(ROOT, MANIFEST_TS)}`);
}

await build();
