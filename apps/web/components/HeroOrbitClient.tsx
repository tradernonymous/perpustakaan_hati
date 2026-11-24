"use client";

import dynamic from "next/dynamic";
import { EMBLEM_SRC } from "./HeroOrbit3D";
import styles from "./HeroOrbit3D.module.css";

const HeroOrbit3D = dynamic(() => import("./HeroOrbit3D").then((m) => ({ default: m.HeroOrbit3D })), {
  ssr: false,
  loading: () => (
    <div className={styles.orbit}>
      <img className={styles.poster} src={EMBLEM_SRC} alt="" width={600} height={420} />
    </div>
  ),
});

/** Client-only wrapper: keeps Three.js out of the server bundle while preserving an SSR-visible poster. */
export function HeroOrbitClient() {
  return <HeroOrbit3D />;
}
