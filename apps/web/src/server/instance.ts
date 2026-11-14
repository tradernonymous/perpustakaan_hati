import path from "node:path";
import { openStore, type Store } from "./store";
import { openOrders, type Orders } from "./orders";
import { openThreadsStore, type ThreadsStore } from "./threads-store";
import { openSuratStore, type SuratStore } from "./surat-store";
import { openBookingStore, type BookingStore } from "./booking-store";

let store: Store | null = null;

/** One shared SQLite handle per server process. */
export function getStore(): Store {
  store ??= openStore(path.join(process.env.DATA_DIR ?? "./data", "subscribers.db"));
  return store;
}

let orders: Orders | null = null;

export function getOrders(): Orders {
  orders ??= openOrders(path.join(process.env.DATA_DIR ?? "./data", "orders.db"));
  return orders;
}

let threads: ThreadsStore | null = null;

/** Rahimam's long-lived Threads token, on the same persistent volume as the rest of the data. */
export function getThreadsStore(): ThreadsStore {
  threads ??= openThreadsStore(path.join(process.env.DATA_DIR ?? "./data", "threads.db"));
  return threads;
}

let surat: SuratStore | null = null;

/** Anonymous Surat Hati inbox on the persistent volume. */
export function getSuratStore(): SuratStore {
  surat ??= openSuratStore(path.join(process.env.DATA_DIR ?? "./data", "surat.db"));
  return surat;
}

let booking: BookingStore | null = null;

/** Counselling booking requests on the persistent volume. */
export function getBookingStore(): BookingStore {
  booking ??= openBookingStore(path.join(process.env.DATA_DIR ?? "./data", "booking.db"));
  return booking;
}

/** Public base URL used in provider callbacks and redirects. */
export { siteUrl } from "../site";
