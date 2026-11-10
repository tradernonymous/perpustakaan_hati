import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import path from "node:path";

export type ThreadsToken = {
  accessToken: string;
  userId: string;
  username: string;
  scopes: string;
  /** Epoch milliseconds. */
  expiresAt: number;
};

export type ThreadsStore = {
  save(token: ThreadsToken): void;
  get(): ThreadsToken | null;
  clear(): void;
  close(): void;
};

type Row = { access_token: string; user_id: string; username: string; scopes: string; expires_at: number };

export function openThreadsStore(file: string): ThreadsStore {
  mkdirSync(path.dirname(file), { recursive: true });
  const db = new Database(file);
  db.pragma("journal_mode = WAL");
  db.exec(`CREATE TABLE IF NOT EXISTS threads_token (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    access_token TEXT NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at INTEGER NOT NULL
  )`);

  const upsert = db.prepare(
    `INSERT INTO threads_token (id, access_token, user_id, username, scopes, expires_at)
     VALUES (1, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       access_token = excluded.access_token,
       user_id = excluded.user_id,
       username = excluded.username,
       scopes = excluded.scopes,
       expires_at = excluded.expires_at`,
  );
  const select = db.prepare("SELECT access_token, user_id, username, scopes, expires_at FROM threads_token WHERE id = 1");
  const remove = db.prepare("DELETE FROM threads_token WHERE id = 1");

  return {
    save(token) {
      upsert.run(token.accessToken, token.userId, token.username, token.scopes, token.expiresAt);
    },
    get() {
      const row = select.get() as Row | undefined;
      if (!row) return null;
      return {
        accessToken: row.access_token,
        userId: row.user_id,
        username: row.username,
        scopes: row.scopes,
        expiresAt: row.expires_at,
      };
    },
    clear() {
      remove.run();
    },
    close() {
      db.close();
    },
  };
}
