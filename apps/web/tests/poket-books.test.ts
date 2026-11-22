import { describe, expect, it } from "vitest";
import { listPocketBooks, POKET_BOOKS } from "@/src/server/poket-books";

describe("listPocketBooks", () => {
  it("lists every Poket title with a boolean availability flag", async () => {
    const books = await listPocketBooks();
    expect(books.map((book) => book.slug)).toEqual(POKET_BOOKS.map((book) => book.slug));
    for (const book of books) expect(typeof book.available).toBe("boolean");
  });

  it("marks the free edition available because its PDF is tracked", async () => {
    const books = await listPocketBooks();
    expect(books.find((book) => book.slug === "edisi-poket")?.available).toBe(true);
  });
});
