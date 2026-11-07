import { describe, expect, it } from "vitest";
import { createRateLimiter } from "@/src/server/ratelimit";

describe("rate limiter", () => {
  it("allows up to max hits per window per key, then blocks", () => {
    let t = 0;
    const rl = createRateLimiter(3, 1000, () => t);
    expect([rl.hit("a"), rl.hit("a"), rl.hit("a"), rl.hit("a")]).toEqual([true, true, true, false]);
    expect(rl.hit("b")).toBe(true);
  });
  it("resets after the window passes", () => {
    let t = 0;
    const rl = createRateLimiter(1, 1000, () => t);
    expect(rl.hit("a")).toBe(true);
    expect(rl.hit("a")).toBe(false);
    t = 1001;
    expect(rl.hit("a")).toBe(true);
  });
});
