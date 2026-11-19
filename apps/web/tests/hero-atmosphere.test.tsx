// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { HeroAtmosphere } from "@/components/HeroAtmosphere";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("runs the decorative loop in view, respects pause, and stops as the hero exits", () => {
  const disconnect = vi.fn();
  const observe = vi.fn();
  let setIntersection: (ratio: number) => void = () => {
    throw new Error("The backdrop was not observed");
  };
  vi.stubGlobal("IntersectionObserver", class {
    observe = observe;
    disconnect = disconnect;

    constructor(callback: IntersectionObserverCallback) {
      setIntersection = (ratio) => callback(
        [{ intersectionRatio: ratio } as IntersectionObserverEntry],
        this as unknown as IntersectionObserver
      );
    }
  });

  const { unmount } = render(<HeroAtmosphere />);
  const backdrop = observe.mock.calls[0][0] as HTMLElement;
  expect(backdrop.getAttribute("aria-hidden")).toBe("true");
  expect(backdrop.dataset.visible).toBe("false");

  act(() => setIntersection(0.7));
  expect(backdrop.dataset.visible).toBe("true");
  fireEvent.click(screen.getByRole("button", { name: "Jeda animasi latar" }));
  expect(backdrop.dataset.paused).toBe("true");
  fireEvent.click(screen.getByRole("button", { name: "Sambung animasi latar" }));
  expect(backdrop.dataset.paused).toBe("false");

  act(() => setIntersection(0.1));
  expect(backdrop.dataset.visible).toBe("false");
  unmount();
  expect(disconnect).toHaveBeenCalledOnce();
});
