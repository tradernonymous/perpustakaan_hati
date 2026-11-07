export function createRateLimiter(max: number, windowMs: number, now: () => number = Date.now) {
  const hits = new Map<string, { count: number; resetAt: number }>();
  return {
    /** Returns true if the request is allowed, false once the key is over the limit. */
    hit(key: string): boolean {
      const t = now();
      const entry = hits.get(key);
      if (!entry || t >= entry.resetAt) {
        hits.set(key, { count: 1, resetAt: t + windowMs });
        return true;
      }
      entry.count += 1;
      return entry.count <= max;
    },
  };
}
