// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { StickyCta } from "@/components/StickyCta";
import { TierCompare } from "@/components/TierCompare";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("starts with Poket and Membangun and can compare a different pair", () => {
  render(<TierCompare />);
  const comparison = within(screen.getByRole("region", { name: "Bandingkan dua edisi" }));
  const first = comparison.getByRole<HTMLSelectElement>("combobox", { name: "Edisi 1" });
  const second = comparison.getByRole<HTMLSelectElement>("combobox", { name: "Edisi 2" });
  expect(first.selectedOptions[0].text).toBe("Poket");
  expect(second.selectedOptions[0].text).toBe("Membangun");
  expect(within(second).getByRole<HTMLOptionElement>("option", { name: "Poket" }).disabled).toBe(true);

  fireEvent.click(comparison.getByRole("checkbox", { name: "Tunjuk perbezaan sahaja" }));
  expect(comparison.queryByText("7 Hari Reset (60 saat sehari)")).toBeNull();
  expect(comparison.getByText("7 bab panduan dengan situasi sebenar rumah tangga Malaysia")).toBeTruthy();

  fireEvent.change(second, { target: { value: "2" } });
  expect(comparison.getByText("Buku Kerja 30 Hari")).toBeTruthy();
  expect(comparison.getByRole("link", { name: "Lihat Teman Hidup" }).getAttribute("href")).toBe("/beli/teman-hidup");
});

it("keeps the fixed action hidden while any inline action section is visible", () => {
  let onIntersection: IntersectionObserverCallback;
  const observer = { observe: vi.fn(), disconnect: vi.fn() };
  vi.stubGlobal("IntersectionObserver", class {
    constructor(callback: IntersectionObserverCallback) { onIntersection = callback; }
    observe = observer.observe;
    disconnect = observer.disconnect;
  });
  const { container } = render(<><section id="percuma" /><section id="edisi" /><StickyCta /></>);
  const reader = container.querySelector("#percuma")!;
  const compare = container.querySelector("#edisi")!;
  const bar = container.querySelector("[data-sticky-cta]")!;
  const intersect = (...entries: [Element, boolean][]) => act(() => {
    onIntersection(entries.map(([target, isIntersecting]) => ({ target, isIntersecting }) as IntersectionObserverEntry),
      observer as unknown as IntersectionObserver);
  });

  expect(bar.getAttribute("data-hidden")).toBe("true");
  expect(observer.observe).toHaveBeenCalledWith(compare);
  intersect([reader, true], [compare, true]);
  intersect([reader, false]);
  expect(bar.getAttribute("data-hidden")).toBe("true");
  intersect([compare, false]);
  expect(bar.getAttribute("data-hidden")).toBe("false");
});
