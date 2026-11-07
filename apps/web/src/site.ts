/** Public base URL, no trailing slash. Set SITE_URL in production. */
export function siteUrl(): string {
  return (process.env.SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
}
