import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";

let database: Database.Database | undefined;
type Feedback = { name: string; email: string; source: string; message: string };

function feedbackDb() {
  if (database) return database;
  const directory = path.resolve(process.env.DATA_DIR ?? "./data");
  mkdirSync(directory, { recursive: true });
  const db = new Database(path.join(directory, "reader-feedback.db"));
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS reader_feedback (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, source TEXT NOT NULL,
    message TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )`);
  database = db;
  return db;
}

export function saveReaderFeedback({ name, email, source, message }: Feedback) {
  feedbackDb().prepare("INSERT INTO reader_feedback (name, email, source, message) VALUES (?, ?, ?, ?)")
    .run(name, email, source, message);
}

export function recentReaderFeedback() {
  return feedbackDb().prepare("SELECT id, name, email, source, message, created_at FROM reader_feedback ORDER BY id DESC LIMIT 100")
    .all() as (Feedback & { id: number; created_at: string })[];
}
