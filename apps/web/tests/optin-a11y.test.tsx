// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { OptInForm } from "@/components/OptInForm";

/*
 * The form slice's contract: an invalid submit must say what is wrong, tie the
 * message to the control with aria-describedby, mark the control aria-invalid,
 * and put focus on it. None of that existed before this slice.
 */
describe("OptInForm accessibility", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ ok: true }), { status: 200 })));
  });
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("points each input at its own description element", () => {
    render(<OptInForm />);
    const email = screen.getByLabelText(/^e-mel$/i);
    const describedBy = email.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(document.getElementById(describedBy!)).not.toBeNull();
  });

  it("rejects an empty submit without calling the API", async () => {
    render(<OptInForm />);
    fireEvent.submit(screen.getByRole("button", { name: /dapatkan edisi poket/i }).closest("form")!);
    expect(await screen.findByText(/masukkan e-mel/i)).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("marks the field invalid and moves focus to it", async () => {
    render(<OptInForm />);
    fireEvent.submit(screen.getByRole("button", { name: /dapatkan edisi poket/i }).closest("form")!);
    const email = screen.getByLabelText(/^e-mel$/i);
    expect(email.getAttribute("aria-invalid")).toBe("true");
    expect(document.activeElement).toBe(email);
  });

  it("clears the error once a valid address is typed", async () => {
    render(<OptInForm />);
    const form = screen.getByRole("button", { name: /dapatkan edisi poket/i }).closest("form")!;
    fireEvent.submit(form);
    const email = screen.getByLabelText(/^e-mel$/i);
    fireEvent.change(email, { target: { value: "nama@contoh.com" } });
    expect(screen.queryByText(/masukkan e-mel/i)).toBeNull();
    expect(email.getAttribute("aria-invalid")).toBe("false");
  });
});