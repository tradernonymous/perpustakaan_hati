// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { TipsFlipbook } from "@/components/TipsFlipbook";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function renderReader() {
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  const { container } = render(<TipsFlipbook artwork />);
  return {
    viewer: screen.getByRole("region", { name: "Buku selak Tips Psikologi Suami Isteri" }),
    dialog: container.querySelector("dialog")!,
  };
}

it("opens the expanded reader on mobile without native fullscreen and keeps the current page", () => {
  const { viewer, dialog } = renderReader();
  dialog.showModal = () => { dialog.open = true; };
  dialog.close = () => {
    dialog.open = false;
    dialog.dispatchEvent(new Event("close"));
  };

  const open = within(viewer).getByRole("button", { name: "Buka skrin penuh" });
  fireEvent.click(open);
  const expanded = within(dialog);
  const region = expanded.getByRole("region", { name: "Buku selak Tips Psikologi Suami Isteri" });
  expect(region.getAttribute("data-expanded")).toBe("true");
  expect(expanded.getByRole("img", { name: "Reka letak asal halaman 1" })).toBeTruthy();
  fireEvent.click(expanded.getByRole("button", { name: "Seterusnya" }));
  expect(expanded.getByRole("img", { name: "Reka letak asal halaman 2" })).toBeTruthy();
  fireEvent.click(expanded.getByRole("button", { name: "Tutup skrin penuh" }));
  expect(dialog.open).toBe(false);
  expect(within(viewer).getByRole("img", { name: "Reka letak asal halaman 2" })).toBeTruthy();
  expect(document.activeElement).toBe(open);
});

it("switches the inline reader layout when native fullscreen changes", () => {
  const { viewer, dialog } = renderReader();
  let fullscreenElement: Element | null = null;
  Object.defineProperty(document, "fullscreenElement", { configurable: true, get: () => fullscreenElement });
  try {
    act(() => {
      fullscreenElement = viewer;
      document.dispatchEvent(new Event("fullscreenchange"));
    });
    expect(viewer.getAttribute("data-expanded")).toBe("true");
    expect(within(viewer).getByRole("button", { name: "Tutup skrin penuh" })).toBeTruthy();
    expect(dialog.open).toBe(false);

    act(() => {
      fullscreenElement = null;
      document.dispatchEvent(new Event("fullscreenchange"));
    });
    expect(viewer.getAttribute("data-expanded")).toBe("false");
    expect(within(viewer).getByRole("button", { name: "Buka skrin penuh" })).toBeTruthy();
  } finally {
    Reflect.deleteProperty(document, "fullscreenElement");
  }
});
