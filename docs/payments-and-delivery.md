# Payments, delivery and the customer library (`apps/web`)

All provider keys are optional. A provider without keys simply reports "belum tersedia" at checkout.

## Flow

1. Buyer opens `/beli/membangun` or `/beli/teman-hidup`, picks FPX/DuitNow QR or card, and (on Membangun) can tick the one-click Teman Hidup add-on.
2. `POST /api/checkout` validates the form, creates a pending order in `DATA_DIR/orders.db`, and sends the buyer to Billplz (FPX, DuitNow QR) or Stripe Checkout (card).
3. The provider calls our webhook. We verify the signature, check the amount against the order, mark it paid exactly once, and deliver.
4. Delivery runs inside the webhook: e-mail (Resend) and WhatsApp (Cloud API) are sent in parallel, each with an 8 second cap, so links normally land in 1 to 3 seconds. Each result is stored in the `deliveries` table.
5. Links look like `/muat-turun/<signed token>` and expire after 7 days. The PDF is read from `ASSETS_DIR`, stamped on every page with the buyer's e-mail and order id, and streamed. Nothing is ever served from `public/`.
6. `/pustaka` lets a buyer ask for a 30 minute sign-in link by e-mail, then download again with fresh links. The form gives the same answer whether or not the e-mail has bought.

## Setup you must do (needs your accounts)

| Item | Where |
|---|---|
| Billplz | Create a collection, enable FPX and DuitNow QR on it. Set `BILLPLZ_API_KEY`, `BILLPLZ_COLLECTION_ID`, `BILLPLZ_X_SIGNATURE` (X Signature Key in Billplz settings). Callback URL is sent per bill: `https://<domain>/api/webhooks/billplz`. Test on `billplz-sandbox.com` first (`BILLPLZ_BASE_URL`). |
| Stripe | Set `STRIPE_SECRET_KEY`. Add a webhook endpoint `https://<domain>/api/webhooks/stripe` for `checkout.session.completed` and copy its signing secret to `STRIPE_WEBHOOK_SECRET`. |
| E-mail | Resend account, verify your domain, set `RESEND_API_KEY` and `EMAIL_FROM`. |
| WhatsApp | Meta WhatsApp Cloud API. Create and get approved a template named `pesanan_siap` (language Bahasa Melayu) with one body variable `{{1}}` for the links. Set `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`. Business-initiated messages fail without an approved template. |
| Files | Put `edisi-membangun.pdf` and `teman-hidup.pdf` in `ASSETS_DIR` (default `/data/assets` on the Railway volume). Until they exist, downloads answer "belum sedia". |
| Prices | Set `PRICE_MEMBANGUN_SEN`, `PRICE_TEMAN_HIDUP_SEN`, `BUMP_TEMAN_HIDUP_SEN` (sen). Defaults: RM 29, RM 79, RM 50 add-on. |
| Secrets | `DOWNLOAD_SECRET` (32+ random characters) and `ADMIN_TOKEN`. |

## When a delivery fails

Failures never block the order. Look in `deliveries` (status `error`, with the reason) and resend by hand from the Railway shell:

```bash
node -e "const D=require('better-sqlite3');console.table(new D('/data/orders.db',{readonly:true}).prepare(\"select o.id,o.email,o.phone,d.channel,d.status,d.detail from orders o left join deliveries d on d.order_id=o.id where o.status='paid' order by o.created_at desc limit 20\").all())"
```

The buyer can also fetch fresh links themselves at `/pustaka`.

## Security notes

- Webhooks only act on a valid signature (Billplz HMAC-SHA256 X-Signature, Stripe `t=,v1=` with 5 minute tolerance) and a matching amount.
- A repeated webhook is a no-op (`status` guard), so delivery never runs twice.
- Tokens are HMAC-signed with `DOWNLOAD_SECRET` and carry an expiry. Library links use `Referrer-Policy: no-referrer`.
- The CSP blocks third-party scripts. Payment pages are reached by top-level redirect, which `form-action 'self'` does not affect.
