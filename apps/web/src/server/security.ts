/**
 * Build a Content-Security-Policy header string.
 *
 * When a per-request cryptographic nonce is provided (via proxy.ts), script-src
 * enforces `'self' 'nonce-<nonce>' 'strict-dynamic'` and drops `'unsafe-inline'`.
 * Static fallback (`CSP`) preserves `'unsafe-inline'` for routes that bypass proxy.
 */
export function buildCsp(nonce?: string): string {
  const scriptSrc = nonce
    ? `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`
    : "script-src 'self' 'unsafe-inline'";

  return [
    "default-src 'self'",
    scriptSrc,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join("; ");
}

export const CSP = buildCsp();

export const SECURITY_HEADERS = [
  { key: "Content-Security-Policy", value: CSP },
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];
