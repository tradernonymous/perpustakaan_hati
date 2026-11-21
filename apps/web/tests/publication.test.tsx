import { execFile, spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { promisify } from "node:util";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { Catalog } from "@/components/Catalog";
import { TIERS } from "@/src/content";

const item = {
  schema_version: 1, id: "poket", slug: "poket", tier: "poket",
  title: "Catatan Edisi Poket", summary: "Satu renungan untuk dibaca bersama.",
  artwork: "/ebooks/cover-poket.png", sample: "/#bab", status: "published", revision: 2,
};

let root: string;
let script: string;
let catalog: string;

beforeEach(() => {
  root = mkdtempSync(join(tmpdir(), "ph-publication-"));
  for (const dir of ["scripts", "src/publication", "public/ebooks"]) mkdirSync(join(root, dir), { recursive: true });
  script = join(root, "scripts/import-publication.py");
  catalog = join(root, "src/publication/catalog.json");
  copyFileSync(resolve("scripts/import-publication.py"), script);
  for (const { cover } of TIERS) {
    if (cover) writeFileSync(join(root, "public", cover), "");
  }
  writeFileSync(catalog, "[]\n");
});
afterEach(() => rmSync(root, { recursive: true, force: true }));

function input(name: string, data: unknown) {
  const path = join(root, name + ".json");
  writeFileSync(path, JSON.stringify(data));
  return path;
}

function run(file: string) {
  return spawnSync("python3", [script, file], { encoding: "utf8" });
}

describe("research export import and storefront card", () => {
  it("renders the approved fields on the matching card, keeping its authoritative access and price", () => {
    expect(run(input("export", item)).status).toBe(0);
    const entries = JSON.parse(readFileSync(catalog, "utf8"));
    const html = renderToStaticMarkup(<Catalog publications={entries} />);
    expect(html).toContain(item.title);
    expect(html).toContain(item.summary);
    expect(html).toContain('href="/#bab"');
    expect(html).toContain('href="#percuma"');
    expect(html).toContain("Percuma");
    expect(html).toContain('href="/beli/membangun"');
    expect(html).toContain('href="/beli/teman-hidup"');
  });

  it("preserves last-good bytes on retries, stale revisions, replays and malformed or private input", () => {
    const valid = input("valid", item);
    expect(run(valid).status).toBe(0);
    const lastGood = readFileSync(catalog, "utf8");
    expect(run(valid).stdout).toContain("Already imported");
    for (const patch of [
      { revision: 1 }, { title: "conflicting revision" }, { status: "draft" },
      { private_notes: "private" }, { price: 0 }, { entitlements: [] }, { schema_version: 2 },
      { slug: "teman-hidup" }, { artwork: "/ebooks/cover-teman-hidup.png" },
      { sample: "/ebooks/paid.pdf" }, { title: "bad\nline" }, { summary: "" }, { title: "<html>" },
      { revision: true }, { revision: 1.5 }, { revision: 2 ** 53 },
    ]) {
      expect(run(input("invalid", { ...item, ...patch })).status).toBe(1);
      expect(readFileSync(catalog, "utf8")).toBe(lastGood);
    }
    expect(run(input("newer", { ...item, revision: 3, title: "Catatan baharu" })).status).toBe(0);
    expect(JSON.parse(readFileSync(catalog, "utf8"))[0].title).toBe("Catatan baharu");
  });

  it("keeps concurrent imports for different products", async () => {
    await Promise.all(TIERS.map(({ id, cover }) => {
      const file = input(id, { ...item, id, tier: id, slug: id, artwork: cover });
      return promisify(execFile)("python3", [script, file]);
    }));
    expect(JSON.parse(readFileSync(catalog, "utf8")).map((record: typeof item) => record.id))
      .toEqual(TIERS.map(({ id }) => id));
  });
});
