import { readTipsArtwork } from "@/src/server/tips-artwork";

export const dynamic = "force-dynamic";

export async function GET() {
  const artwork = await readTipsArtwork();
  if (!artwork) return new Response(null, { status: 404, headers: { "cache-control": "no-store" } });
  return new Response(new Uint8Array(artwork), {
    headers: { "content-type": "image/webp", "cache-control": "public, max-age=300", "x-content-type-options": "nosniff" },
  });
}
