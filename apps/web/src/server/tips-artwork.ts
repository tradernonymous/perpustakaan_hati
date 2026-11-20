import { readFile } from "node:fs/promises";
import path from "node:path";
import { existsSync } from "node:fs";

const file = "tips-flipbook.webp";

function artworkLocation() {
  if (process.env.NODE_ENV === "production") {
    return path.join(process.env.ASSETS_DIR ?? path.resolve(process.env.DATA_DIR ?? "./data", "assets"), file);
  }
  return path.resolve("private/ebooks", file);
}

export function hasTipsArtwork() {
  return existsSync(/* turbopackIgnore: true */ artworkLocation());
}

export async function readTipsArtwork() {
  try {
    return await readFile(/* turbopackIgnore: true */ artworkLocation());
  } catch {
    return null;
  }
}
