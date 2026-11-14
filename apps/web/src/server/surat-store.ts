import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";

export type SuratRow = {
  id: number;
  alias: string | null;
  anonymized_dilemma: string;
  consent_publish: number;
  created_at: string;
};

export type SuratStore = {
  add(input: { alias: string | null; anonymizedDilemma: string; consentPublish: boolean }): { id: number };
  count(): number;
  list(): SuratRow[];
  close(): void;
};

/** SQLite persistence for anonymous Surat Hati confessions. */
export function openSuratStore(file: string): SuratStore {
  mkdirSync(path.dirname(file), { recursive: true });
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS surat_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT,
    anonymized_dilemma TEXT NOT NULL,
    consent_publish INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
  )`);
  const insert = db.prepare(
    "INSERT INTO surat_entries (alias, anonymized_dilemma, consent_publish) VALUES (?, ?, ?)",
  );
  const all = db.prepare(
    "SELECT id, alias, anonymized_dilemma, consent_publish, created_at FROM surat_entries ORDER BY id DESC",
  );
  const total = db.prepare("SELECT COUNT(*) AS n FROM surat_entries");

  return {
    add({ alias, anonymizedDilemma, consentPublish }) {
      const info = insert.run(alias, anonymizedDilemma, consentPublish ? 1 : 0);
      return { id: Number(info.lastInsertRowid) };
    },
    list: () => all.all() as SuratRow[],
    count: () => (total.get() as { n: number }).n,
    close: () => db.close(),
  };
}
