"use client";

import { useEffect, useRef, useState } from "react";
import styles from "./HeroAtmosphere.module.css";

export function HeroAtmosphere() {
  const backdrop = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (!backdrop.current || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      ([entry]) => setVisible(entry.intersectionRatio >= 0.15),
      { threshold: 0.15 }
    );
    observer.observe(backdrop.current);
    return () => observer.disconnect();
  }, []);

  return (
    <>
      <div
        ref={backdrop}
        className={styles.backdrop}
        aria-hidden="true"
        data-visible={visible}
        data-paused={paused}
      >
        <div className={styles.fan}>
          <i />
          <i />
          <i />
          <i />
        </div>
      </div>
      <button
        type="button"
        className={styles.pause}
        aria-label={paused ? "Sambung animasi latar" : "Jeda animasi latar"}
        onClick={() => setPaused((current) => !current)}
      >
        <span aria-hidden="true" className={paused ? styles.playIcon : styles.pauseIcon} />
      </button>
    </>
  );
}
