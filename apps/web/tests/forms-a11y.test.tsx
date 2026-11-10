// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CheckoutForm } from "@/components/CheckoutForm";
import { LibraryLogin } from "@/components/LibraryLogin";

/* Same contract as the opt-in form: describe the error, mark the field, move focus. */
beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ ok: true }), { status: 200 })));
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("CheckoutForm accessibility", () => {
  const props = { product: "membangun" as const, name: "Edisi Membangun", priceLabel: "RM 29.00", priceSen: 2900, bump: null };

  it("ties the email input to its error element", () => {
    render(<CheckoutForm {...props} />);
    const email = screen.getByLabelText(/^e-mel \(buku dihantar ke sini\)$/i);
    const describedBy = email.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(document.getElementById(describedBy!)).not.toBeNull();
  });

  it("blocks an empty submit and focuses the email", async () => {
    render(<CheckoutForm {...props} />);
    fireEvent.submit(screen.getByRole("button", { name: /bayar/i }).closest("form")!);
    expect(await screen.findByText(/masukkan e-mel/i)).toBeTruthy();
    const email = screen.getByLabelText(/^e-mel \(buku dihantar ke sini\)$/i);
    expect(email.getAttribute("aria-invalid")).toBe("true");
    expect(document.activeElement).toBe(email);
    expect(fetch).not.toHaveBeenCalled();
  });
});

describe("LibraryLogin accessibility", () => {
  it("blocks an empty submit and focuses the email", async () => {
    render(<LibraryLogin />);
    fireEvent.submit(screen.getByRole("button", { name: /hantar pautan/i }).closest("form")!);
    expect(await screen.findByText(/masukkan e-mel/i)).toBeTruthy();
    const email = screen.getByLabelText(/e-mel yang kamu guna semasa membeli/i);
    expect(email.getAttribute("aria-invalid")).toBe("true");
    expect(document.activeElement).toBe(email);
    expect(fetch).not.toHaveBeenCalled();
  });
});