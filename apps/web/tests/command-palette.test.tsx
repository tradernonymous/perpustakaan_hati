// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { CommandPalette, PALETTE_ITEMS } from "@/components/CommandPalette";
import { SiteHeader } from "@/components/SiteHeader";

afterEach(cleanup);

describe("quick-jump palette", () => {
  it("lists the home sections and the key pages with real hrefs", () => {
    const hrefs = PALETTE_ITEMS.map((i) => i.href);
    expect(hrefs).not.toContain("/teman-hati");
    for (const h of ["#percuma", "#bab", "#edisi", "#katalog", "#cara", "#soalan", "/pustaka", "/booking"]) {
      expect(hrefs).toContain(h);
    }
  });

  it("is closed until Ctrl+K, then opens a labelled dialog with the search focused", () => {
    render(<CommandPalette />);
    expect(screen.queryByRole("dialog")).toBeNull();
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    const dialog = screen.getByRole("dialog", { name: /lompat/i });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(document.activeElement).toBe(screen.getByRole("combobox"));
  });

  it("also opens with Cmd+K and from the header hint button", () => {
    render(<><SiteHeader /><CommandPalette /></>);
    fireEvent.click(screen.getByRole("button", { name: /lompat ke/i }));
    expect(screen.getByRole("dialog")).toBeTruthy();
  });

  it("filters by what is typed and says so when nothing matches", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", metaKey: true });
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "booking" } });
    expect(screen.getAllByRole("option").length).toBe(1);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "zzzz" } });
    expect(screen.queryAllByRole("option").length).toBe(0);
    expect(screen.getByRole("status").textContent).toMatch(/tiada/i);
  });

  it("moves the active option with the arrow keys and wraps", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    const box = screen.getByRole("combobox");
    const first = screen.getAllByRole("option")[0];
    expect(first.getAttribute("aria-selected")).toBe("true");
    expect(box.getAttribute("aria-activedescendant")).toBe(first.id);
    fireEvent.keyDown(box, { key: "ArrowUp" });
    const opts = screen.getAllByRole("option");
    expect(opts[opts.length - 1].getAttribute("aria-selected")).toBe("true");
  });

  it("closes on Escape and returns focus to the page", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Escape" });
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("does not hijack Ctrl+K while typing in another field", () => {
    render(<><input aria-label="lain" /><CommandPalette /></>);
    const other = screen.getByLabelText("lain");
    other.focus();
    fireEvent.keyDown(other, { key: "k", ctrlKey: true });
    expect(screen.getByRole("dialog")).toBeTruthy(); // Ctrl/Cmd+K is a chord, so it is allowed everywhere
  });
});

describe("palette review fixes", () => {
  it("is mounted once in the root layout so every page has it, not only the home page", async () => {
    const { readFileSync } = await import("node:fs");
    const { join } = await import("node:path");
    const layout = readFileSync(join(__dirname, "../app/layout.tsx"), "utf8");
    const page = readFileSync(join(__dirname, "../app/page.tsx"), "utf8");
    expect(layout).toContain("<CommandPalette />");
    expect(page).not.toContain("<CommandPalette />");
  });

  it("keeps Tab inside the dialog", () => {
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    const tab = new KeyboardEvent("keydown", { key: "Tab", bubbles: true, cancelable: true });
    screen.getByRole("combobox").dispatchEvent(tab);
    expect(tab.defaultPrevented).toBe(true);
  });

  it("returns focus to the element that had it, even after a repeated Ctrl+K", () => {
    render(<><button>Mula</button><CommandPalette /></>);
    const btn = screen.getByRole("button", { name: "Mula" });
    btn.focus();
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Escape" });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(btn);
  });

  it("locks body scroll while open and restores it on close", () => {
    document.body.style.overflow = "";
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(document.body.style.overflow).toBe("hidden");
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "Escape" });
    expect(document.body.style.overflow).toBe("");
  });

  it("scrolls the active option into view", () => {
    const calls: string[] = [];
    Element.prototype.scrollIntoView = function (this: Element) { calls.push(this.id); };
    render(<CommandPalette />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    calls.length = 0;
    fireEvent.keyDown(screen.getByRole("combobox"), { key: "ArrowDown" });
    expect(calls.length).toBe(1);
    expect(calls[0]).toMatch(/-opt-1$/);
  });
});
