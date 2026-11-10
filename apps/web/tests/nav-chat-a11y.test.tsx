// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { SiteHeader } from "@/components/SiteHeader";
import { TemanHatiChat } from "@/components/TemanHatiChat";

afterEach(cleanup);

describe("SiteHeader skip link", () => {
  it("offers a skip link to the main landmark", () => {
    render(<SiteHeader />);
    const skip = screen.getByRole("link", { name: /lompat ke kandungan/i });
    expect(skip.getAttribute("href")).toBe("#utama");
  });

  it("keeps the mobile disclosure wired to its panel", () => {
    render(<SiteHeader />);
    const toggle = screen.getByRole("button", { name: /buka menu/i });
    expect(toggle.getAttribute("aria-expanded")).toBe("false");
    expect(toggle.getAttribute("aria-controls")).toBe("menu-mudah-alih");
    fireEvent.click(toggle);
    expect(screen.getByRole("button", { name: /tutup menu/i }).getAttribute("aria-expanded")).toBe("true");
    expect(document.getElementById("menu-mudah-alih")).not.toBeNull();
  });
});

describe("TemanHatiChat", () => {
  it("exposes the transcript as a live log", () => {
    render(<TemanHatiChat />);
    const log = screen.getByRole("log");
    expect(log.getAttribute("aria-live")).toBe("polite");
    expect(log.textContent).toContain("Teman Hati");
  });

  it("labels the composer and sends on submit", () => {
    render(<TemanHatiChat />);
    const input = screen.getByLabelText(/tulis mesej/i);
    fireEvent.change(input, { target: { value: "Aku rasa sunyi" } });
    fireEvent.submit(input.closest("form")!);
    expect(screen.getByRole("log").textContent).toContain("Aku rasa sunyi");
    expect((input as HTMLInputElement).value).toBe("");
  });

  it("ignores an empty submit", () => {
    render(<TemanHatiChat />);
    const before = screen.getByRole("log").textContent;
    fireEvent.submit(screen.getByLabelText(/tulis mesej/i).closest("form")!);
    expect(screen.getByRole("log").textContent).toBe(before);
  });
});