import { describe, expect, it, vi } from "vitest";
import { GET } from "@/app/api/edisi-poket/pdf/route";

const { activeReader } = vi.hoisted(() => ({ activeReader: vi.fn() }));
vi.mock("@/src/server/reader-session", () => ({ activeReader }));

describe("GET /api/edisi-poket/pdf", () => {
  it("redirects a guest to Pustaka", async () => {
    activeReader.mockResolvedValue(null);
    const response = await GET();
    expect(response.status).toBe(303);
    expect(response.headers.get("location")).toBe("/pustaka");
  });

  it("serves a valid PDF attachment with noindex header", async () => {
    activeReader.mockResolvedValue("reader@example.com");
    const res = await GET();
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("application/pdf");
    expect(res.headers.get("content-disposition")).toContain("edisi-poket.pdf");
    expect(res.headers.get("x-robots-tag")).toBe("noindex");
    const buf = new Uint8Array(await res.arrayBuffer());
    const header = new TextDecoder().decode(buf.slice(0, 5));
    expect(header).toBe("%PDF-");
  });
});
