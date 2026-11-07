import path from "node:path";
import { openStore, type Store } from "./store";

let store: Store | null = null;

/** One shared SQLite handle per server process. */
export function getStore(): Store {
  store ??= openStore(path.join(process.env.DATA_DIR ?? "./data", "subscribers.db"));
  return store;
}
