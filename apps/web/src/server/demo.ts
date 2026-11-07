import type { Env } from "../env";

/**
 * Demo mode lets the whole buy -> pay -> deliver -> library flow run with no
 * provider keys and no product files. It is off unless DEMO_MODE=1, and every
 * demo route answers 404 while it is off. Never enable it on the live site.
 */
export function demoMode(env: Env = process.env): boolean {
  return env.DEMO_MODE === "1";
}
