/**
 * Perpustakaan Hati — open graph / Twitter card image.
 *
 * Social scrapers (Threads, WhatsApp, Facebook, X) ignore SVG, so the site
 * needs a real raster. The card is built from the sanctioned cinematic
 * lockup (docs/brand/assets/lockup-cinematic.svg) — never a re-typed
 * approximation, because the extrusion is real vector geometry and all
 * brand type in that file is already outlined (no font dependency).
 *
 * The lockup is a 1600x1000 stage; the card is 1200x630. We keep the whole
 * stage width and crop the top and bottom bands, which is what puts the
 * byline rule and the gold tagline on the card.
 *
 * Run:
 *     node apps/web/scripts/build-og-image.mjs
 *
 * Output:
 *     apps/web/public/brand/og-image.png   (1200x630)
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import sharp from "sharp";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const LOCKUP = path.join(ROOT, "docs/brand/assets/lockup-cinematic.svg");
const OUT = path.join(ROOT, "apps/web/public/brand/og-image.png");

const WIDTH = 1200;
const HEIGHT = 630;
const GROUND = "#07140d"; // --forest-night, the same night the stage uses

/** Stage crop: full width, top and bottom bands trimmed. 1200/630 = 1.9048. */
const VIEWBOX = "40 105 1520 840";

/** Pull the inner markup out of the lockup file so it can be nested in a card. */
function innerMarkup() {
  const svg = readFileSync(LOCKUP, "utf8");
  const open = svg.indexOf(">", svg.indexOf("<svg"));
  const close = svg.lastIndexOf("</svg>");
  return svg.slice(open + 1, close);
}

async function build() {
  const card = `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}">
    <rect width="${WIDTH}" height="${HEIGHT}" fill="${GROUND}"/>
    <svg width="${WIDTH}" height="${HEIGHT}" viewBox="${VIEWBOX}" preserveAspectRatio="xMidYMid slice">
      ${innerMarkup()}
    </svg>
  </svg>`;

  await sharp(Buffer.from(card)).png({ compressionLevel: 9 }).toFile(OUT);

  const meta = await sharp(OUT).metadata();
  if (meta.width !== WIDTH || meta.height !== HEIGHT) {
    throw new Error(`og-image must be ${WIDTH}x${HEIGHT}, got ${meta.width}x${meta.height}`);
  }
  console.log(`wrote ${path.relative(ROOT, OUT)} (${meta.width}x${meta.height}, ${meta.size} bytes)`);
}

await build();
