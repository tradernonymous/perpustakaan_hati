import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";

let database: Database.Database | undefined;

function bookmarks(): Database.Database {
  if (database) return database;
  const directory = path.resolve(process.env.DATA_DIR ?? "./data");
  mkdirSync(directory, { recursive: true });
  const db = new Database(path.join(directory, "reader-bookmarks.db"));
  db.pragma("journal_mode = WAL");
  db.exec("CREATE TABLE IF NOT EXISTS tips_bookmarks (email TEXT PRIMARY KEY, page INTEGER NOT NULL)");
  database = db;
  return db;
}

export function getTipsBookmark(email: string): number | null {
  const entry = bookmarks().prepare("SELECT page FROM tips_bookmarks WHERE email = ?").get(email) as { page: number } | undefined;
  return entry?.page ?? null;
}

export function setTipsBookmark(email: string, page: number | null): void {
  if (page === null) {
    bookmarks().prepare("DELETE FROM tips_bookmarks WHERE email = ?").run(email);
    return;
  }
  bookmarks().prepare(
    "INSERT INTO tips_bookmarks (email, page) VALUES (?, ?) ON CONFLICT (email) DO UPDATE SET page = excluded.page",
  ).run(email, page);
}
