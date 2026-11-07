import Database from "better-sqlite3";
import { randomUUID } from "node:crypto";
import { mkdirSync } from "node:fs";
import path from "node:path";
import type { ProductId } from "../catalog";

export type Provider = "billplz" | "stripe";
export type OrderStatus = "pending" | "paid";

export type Order = {
  id: string;
  items: ProductId[];
  amountSen: number;
  email: string;
  phone: string | null;
  provider: Provider;
  providerRef: string | null;
  status: OrderStatus;
  createdAt: string;
  paidAt: string | null;
};

export type Delivery = { channel: "email" | "whatsapp"; status: "ok" | "error"; detail: string | null; at: string };

export type NewOrder = { items: readonly ProductId[]; amountSen: number; email: string; phone: string | null; provider: Provider };

export type Orders = {
  create(o: NewOrder): Order;
  get(id: string): Order | null;
  setProviderRef(id: string, ref: string): void;
  findByProviderRef(provider: Provider, ref: string): Order | null;
  markPaid(id: string, ref: string): { changed: boolean };
  listPaidByEmail(email: string): Order[];
  recordDelivery(orderId: string, channel: Delivery["channel"], status: Delivery["status"], detail?: string): void;
  deliveries(orderId: string): Delivery[];
  close(): void;
};

type Row = {
  id: string; items: string; amount_sen: number; email: string; phone: string | null;
  provider: Provider; provider_ref: string | null; status: OrderStatus; created_at: string; paid_at: string | null;
};

const toOrder = (r: Row): Order => ({
  id: r.id, items: JSON.parse(r.items) as ProductId[], amountSen: r.amount_sen, email: r.email, phone: r.phone,
  provider: r.provider, providerRef: r.provider_ref, status: r.status, createdAt: r.created_at, paidAt: r.paid_at,
});

export function openOrders(file: string): Orders {
  if (file !== ":memory:") mkdirSync(path.dirname(file), { recursive: true });
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    items TEXT NOT NULL,
    amount_sen INTEGER NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    provider TEXT NOT NULL,
    provider_ref TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    paid_at TEXT
  );
  CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT,
    at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
  );
  CREATE INDEX IF NOT EXISTS orders_email ON orders (email);
  CREATE INDEX IF NOT EXISTS orders_ref ON orders (provider, provider_ref);`);

  const insert = db.prepare("INSERT INTO orders (id, items, amount_sen, email, phone, provider) VALUES (?,?,?,?,?,?)");
  const byId = db.prepare("SELECT * FROM orders WHERE id = ?");
  const byRef = db.prepare("SELECT * FROM orders WHERE provider = ? AND provider_ref = ?");
  const setRef = db.prepare("UPDATE orders SET provider_ref = ? WHERE id = ?");
  // The status guard makes a repeated webhook a no-op, so delivery never runs twice.
  const pay = db.prepare("UPDATE orders SET status='paid', provider_ref=?, paid_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=? AND status='pending'");
  const paidByEmail = db.prepare("SELECT * FROM orders WHERE email = ? AND status='paid' ORDER BY created_at DESC");

  const addDelivery = db.prepare("INSERT INTO deliveries (order_id, channel, status, detail) VALUES (?,?,?,?)");
  const listDeliveries = db.prepare("SELECT channel, status, detail, at FROM deliveries WHERE order_id = ? ORDER BY id");

  const get = (id: string) => {
    const r = byId.get(id) as Row | undefined;
    return r ? toOrder(r) : null;
  };

  return {
    create(o) {
      const id = randomUUID();
      insert.run(id, JSON.stringify(o.items), o.amountSen, o.email.toLowerCase(), o.phone, o.provider);
      return get(id)!;
    },
    get,
    setProviderRef: (id, ref) => void setRef.run(ref, id),
    findByProviderRef(provider, ref) {
      const r = byRef.get(provider, ref) as Row | undefined;
      return r ? toOrder(r) : null;
    },
    markPaid: (id, ref) => ({ changed: pay.run(ref, id).changes === 1 }),
    listPaidByEmail: (email) => (paidByEmail.all(email.toLowerCase()) as Row[]).map(toOrder),
    recordDelivery: (orderId, channel, status, detail) => void addDelivery.run(orderId, channel, status, detail ?? null),
    deliveries: (orderId) => listDeliveries.all(orderId) as Delivery[],
    close: () => db.close(),
  };
}
