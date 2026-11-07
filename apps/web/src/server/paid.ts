import { deliverOrder } from "./fulfil";
import { getOrders } from "./instance";

/**
 * Delivery hook shared by both payment webhooks. It runs inside the webhook so links land in seconds.
 * It must never throw: the order is already marked paid, and a thrown error would make the provider
 * retry into a "duplicate" that skips delivery. Failures are recorded so they can be resent by hand.
 */
export async function onPaid(orderId: string): Promise<void> {
  const orders = getOrders();
  const order = orders.get(orderId);
  if (!order) return;
  try {
    await deliverOrder(order, { orders, env: process.env });
  } catch (e) {
    orders.recordDelivery(order.id, "email", "error", e instanceof Error ? e.message : "delivery failed");
  }
}
