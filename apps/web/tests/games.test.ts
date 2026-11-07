import { describe, expect, it } from "vitest";
import { CARDS, drawCard, bingoMarks, scoreBingo, isRed, isGreen, isLuka } from "@/src/games/cards";
import { QUESTIONS, scoreCermin, verdictFor } from "@/src/games/cermin";

describe("Kad Jujur Hati", () => {
  it("has 12 cards", () => {
    expect(CARDS).toHaveLength(12);
  });
  it("drawCard returns a card from the deck", () => {
    const c = drawCard(0);
    expect(CARDS).toContain(c);
    expect(c.category).toMatch(/red|green|luka/);
  });
  it("drawCard picks deterministically for a given index", () => {
    expect(drawCard(3)).toEqual(drawCard(3));
  });
  it("category helpers work", () => {
    const red = CARDS.find((c) => isRed(c))!;
    const green = CARDS.find((c) => isGreen(c))!;
    const luka = CARDS.find((c) => isLuka(c))!;
    expect(red.category).toBe("red");
    expect(green.category).toBe("green");
    expect(luka.category).toBe("luka");
  });
  it("bingoMarks marks only supplied entries", () => {
    const marks = bingoMarks(["red-1", "green-2"]);
    expect(marks).toContain("red-1");
    expect(marks).toContain("green-2");
    expect(marks).toHaveLength(2);
  });
  it("scoreBingo counts a full row", () => {
    const row = ["a", "b", "c", "d", "e"];
    expect(scoreBingo(row, row)).toBe(1);
  });
  it("scoreBingo counts zero when no row is complete", () => {
    expect(scoreBingo(["a", "b"], ["c", "d"])).toBe(0);
  });
});

describe("Cermin Pasangan", () => {
  it("has 5 questions", () => {
    expect(QUESTIONS).toHaveLength(5);
  });
  it("scoreCermin sums answer scores", () => {
    const answers = QUESTIONS.map(() => 2);
    expect(scoreCermin(answers)).toBe(10);
  });
  it("verdictFor maps score to verdict", () => {
    expect(verdictFor(10)).toBe("cermin-clear");
    expect(verdictFor(5)).toBe("warm-up");
    expect(verdictFor(0)).toBe("need-care");
  });
});
