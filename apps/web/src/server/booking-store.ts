import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";
import type { SessionType } from "../games/booking";

export type BookingRow = {
  id: number;
  name: string;
  email: string;
  phone: string;
  session_type: SessionType;
  quote_sen: number;
  notes: string | null;
  created_at: string;
};

export type BookingStore = {
  add(input: {
    name: string;
    email: string;
    phone: string;
    sessionType: SessionType;
    quoteSen: number;
    notes: string | null;
  }): { id: number };
  count(): number;
  list(): BookingRow[];
  close(): void;
};

/** SQLite persistence for counselling session booking requests. */
export function openBookingStore(file: string): BookingStore {
  mkdirSync(path.dirname(file), { recursive: true });
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    session_type TEXT NOT NULL,
    quote_sen INTEGER NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
  )`);
  const insert = db.prepare(
    "INSERT INTO bookings (name, email, phone, session_type, quote_sen, notes) VALUES (?, ?, ?, ?, ?, ?)",
  );
  const all = db.prepare(
    "SELECT id, name, email, phone, session_type, quote_sen, notes, created_at FROM bookings ORDER BY id DESC",
  );
  const total = db.prepare("SELECT COUNT(*) AS n FROM bookings");

  return {
    add({ name, email, phone, sessionType, quoteSen, notes }) {
      const info = insert.run(name, email, phone, sessionType, quoteSen, notes);
      return { id: Number(info.lastInsertRowid) };
    },
    list: () => all.all() as BookingRow[],
    count: () => (total.get() as { n: number }).n,
    close: () => db.close(),
  };
}
