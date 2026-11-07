import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";
import type { SubscribeValue } from "./validate";

export type SubscriberRow = { id: number; email: string | null; phone: string | null; created_at: string };

export type Store = {
  add(v: SubscribeValue): { created: boolean };
  count(): number;
  list(): SubscriberRow[];
  close(): void;
};

export function openStore(file: string): Store {
  mkdirSync(path.dirname(file), { recursive: true });
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
  )`);
  const insert = db.prepare("INSERT INTO subscribers (email, phone) VALUES (?, ?)");
  const all = db.prepare("SELECT id, email, phone, created_at FROM subscribers ORDER BY id DESC");
  const total = db.prepare("SELECT COUNT(*) AS n FROM subscribers");

  return {
    add({ email, phone }) {
      try {
        insert.run(email, phone);
        return { created: true };
      } catch (e) {
        if ((e as { code?: string }).code === "SQLITE_CONSTRAINT_UNIQUE") return { created: false };
        throw e;
      }
    },
    list: () => all.all() as SubscriberRow[],
    count: () => (total.get() as { n: number }).n,
    close: () => db.close(),
  };
}
