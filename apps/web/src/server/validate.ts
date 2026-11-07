export type SubscribeValue = { email: string | null; phone: string | null };
export type ValidateResult =
  | { ok: true; bot: boolean; value: SubscribeValue }
  | { ok: false; error: string };

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// Malaysian mobile: 01x-xxxxxxx or 011-xxxxxxxx, with optional 60 / +60 prefix.
const MY_MOBILE = /^(?:\+?60|0)(1\d{8,9})$/;

const fail = (error: string): ValidateResult => ({ ok: false, error });

export function validateSubscribe(input: unknown): ValidateResult {
  if (typeof input !== "object" || input === null) return fail("Permintaan tidak sah.");
  const body = input as Record<string, unknown>;

  const rawEmail = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
  const rawPhone = typeof body.phone === "string" ? body.phone.replace(/[\s-]/g, "") : "";

  if (!rawEmail && !rawPhone) return fail("Sila isi e-mel atau nombor WhatsApp.");
  if (body.consent !== true) return fail("Sila setuju dengan notis privasi (PDPA) untuk teruskan.");

  let email: string | null = null;
  if (rawEmail) {
    if (rawEmail.length > 254 || !EMAIL.test(rawEmail)) return fail("Alamat e-mel tidak sah.");
    email = rawEmail;
  }

  let phone: string | null = null;
  if (rawPhone) {
    const m = MY_MOBILE.exec(rawPhone);
    if (!m) return fail("Nombor WhatsApp mesti nombor mudah alih Malaysia, contoh 012-345 6789.");
    phone = `+60${m[1]}`;
  }

  const bot = typeof body.website === "string" && body.website.length > 0;
  return { ok: true, bot, value: { email, phone } };
}
