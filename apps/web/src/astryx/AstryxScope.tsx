"use client";

/*
 * AstryxScope — the only place Astryx CSS and the stone theme enter the app.
 *
 * Deliberately NOT mounted in app/layout.tsx: Astryx ships ~271 kB of CSS, and
 * the spike showed Next scopes that to the routes that import it. The storefront
 * keeps its own 53 kB chunk; only routes that adopt Astryx components pay for it.
 */
import "@astryxdesign/core/astryx.css";
import "@astryxdesign/theme-stone/theme.css";
import "./astryx-brand.css";

import type { ReactNode } from "react";
import { Theme } from "@astryxdesign/core/theme";
import { stoneTheme } from "@astryxdesign/theme-stone";

export function AstryxScope({ children }: { children: ReactNode }) {
  return (
    <Theme theme={stoneTheme} mode="light">
      {children}
    </Theme>
  );
}
