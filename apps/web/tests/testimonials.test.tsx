// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { Testimonials } from "@/components/Testimonials";
import { TESTIMONIALS } from "@/src/content";

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function mountCarousel(reducedMotion: boolean) {
  vi.useFakeTimers();
  vi.stubGlobal("matchMedia", () => ({
    matches: reducedMotion,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  vi.spyOn(document, "visibilityState", "get").mockReturnValue("visible");
  vi.stubGlobal("IntersectionObserver", class {
    constructor(private callback: IntersectionObserverCallback) {}
    observe() {
      const entry = { isIntersecting: true, intersectionRatio: 1 } as IntersectionObserverEntry;
      this.callback([entry], this as unknown as IntersectionObserver);
    }
    disconnect() {}
  });
  render(<Testimonials />);
}

it("shows one reply at a time and allows pausing and navigating all eight links", () => {
  mountCarousel(false);
  const link = () => screen.getByRole("link").getAttribute("href");
  const next = screen.getByRole("button", { name: "Maklum balas seterusnya" });
  expect(link()).toBe(TESTIMONIALS[0].url);
  act(() => vi.advanceTimersByTime(9000));
  expect(link()).toBe(TESTIMONIALS[1].url);

  fireEvent.click(screen.getByRole("button", { name: "Jeda putaran" }));
  act(() => vi.advanceTimersByTime(18000));
  expect(link()).toBe(TESTIMONIALS[1].url);
  for (const item of [...TESTIMONIALS.slice(2), TESTIMONIALS[0]]) {
    fireEvent.click(next);
    expect(link()).toBe(item.url);
  }
  const resume = screen.getByRole("button", { name: "Sambung putaran" });
  fireEvent.focus(resume);
  fireEvent.click(resume);
  act(() => vi.advanceTimersByTime(9000));
  expect(link()).toBe(TESTIMONIALS[1].url);
});

it("keeps rotation off when reduced motion is requested", () => {
  mountCarousel(true);
  act(() => vi.advanceTimersByTime(18000));
  expect(screen.getByRole("link").getAttribute("href")).toBe(TESTIMONIALS[0].url);
  fireEvent.click(screen.getByRole("button", { name: "Maklum balas sebelumnya" }));
  expect(screen.getByRole("link").getAttribute("href")).toBe(TESTIMONIALS[7].url);
});
