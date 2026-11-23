"use client";

import { useEffect, useState } from "react";
import { TIERS } from "@/src/content";
import { EBOOK_COVERS } from "@/src/ebook-covers";
import { ProductCover } from "./ProductCover";
import { PsycheBadge } from "./PsycheIcon";
import { TIER_PSYCHE, EBOOK_PSYCHE } from "@/src/psyche";

type PublishedCard = {
  tier: string;
  title: string;
  summary: string;
  artwork: string;
  sample: string | null;
};

type Filters = { q: string; edisi: string };
const EMPTY: Filters = { q: "", edisi: "" };

const FILTERS = [
  { slug: "", label: "Semua" },
  ...TIERS.map((t) => ({ slug: t.id as string, label: t.name })),
];

/** The A4 covers are Poket previews, so they share the Poket edition filter. */
function editionSlug(edition: string): string {
  const found = TIERS.find((t) => edition.toLowerCase().includes(t.name.toLowerCase()));
  return found?.id ?? "";
}

function readUrl(): Filters {
  if (typeof window === "undefined") return EMPTY;
  const params = new URLSearchParams(window.location.search);
  const q = params.get("q")?.trim() ?? "";
  const raw = params.get("edisi") ?? "";
  return { q, edisi: FILTERS.some((f) => f.slug === raw) ? raw : "" };
}

/** Filters live in the URL so a link or a refresh restores the same view. */
function writeUrl(next: Filters) {
  const params = new URLSearchParams(window.location.search);
  if (next.q) params.set("q", next.q);
  else params.delete("q");
  if (next.edisi) params.set("edisi", next.edisi);
  else params.delete("edisi");
  const query = params.toString();
  const { pathname, hash } = window.location;
  window.history.replaceState(null, "", `${pathname}${query ? `?${query}` : ""}${hash}`);
}

function matches(parts: (string | undefined)[], q: string): boolean {
  const needle = q.trim().toLowerCase();
  return !needle || parts.some((part) => (part ?? "").toLowerCase().includes(needle));
}

/**
 * One catalog for the three editions and the real A4 books. Search and the
 * edition chips are plain URL state (?q=&edisi=), so they work without JS,
 * survive a refresh and are shareable. The quick-jump palette stays the
 * single navigation search; this box only filters the items below it.
 */
export function Catalog({ publications = [], prices = {} }: { publications?: PublishedCard[]; prices?: Record<string, string> }) {
  // Server and first client render agree on "all items"; the URL is applied
  // after mount so hydration never depends on browser state.
  const [filters, setFilters] = useState<Filters>(EMPTY);

  useEffect(() => {
    const apply = () => setFilters(readUrl());
    apply();
    window.addEventListener("popstate", apply);
    return () => window.removeEventListener("popstate", apply);
  }, []);

  const change = (next: Filters) => {
    writeUrl(next);
    setFilters(next);
  };

  const tiers = TIERS.map((tier) => {
    const editorial = publications.find((record) => record.tier === tier.id);
    return {
      ...tier,
      price: prices[tier.id] ?? tier.price,
      title: editorial?.title ?? tier.name,
      summary: editorial?.summary ?? tier.subcopy,
      artwork: editorial?.artwork ?? tier.cover,
      sample: editorial?.sample,
    };
  }).filter((t) =>
    (!filters.edisi || filters.edisi === t.id) &&
    matches([t.name, t.title, t.summary, t.size, t.price, ...t.includes], filters.q)
  );
  const covers = EBOOK_COVERS.filter((c) =>
    (!filters.edisi || filters.edisi === editionSlug(c.edition)) &&
    matches([c.title, c.edition, c.pages, c.tagline, c.summary], filters.q)
  );
  const total = TIERS.length + EBOOK_COVERS.length;

  return (
    <div className="mx-auto flex max-w-grid flex-col gap-8">
      <div className="mx-auto flex w-full max-w-reading flex-col items-center gap-4">
        <form role="search" onSubmit={(e) => e.preventDefault()} className="w-full">
          <label htmlFor="katalog-cari" className="sr-only">Cari edisi atau tajuk buku</label>
          <input
            id="katalog-cari"
            type="search"
            name="q"
            value={filters.q}
            onChange={(e) => change({ ...filters, q: e.target.value })}
            placeholder="Cari edisi atau tajuk buku…"
            className="min-h-tap w-full rounded border border-line bg-surface-raised px-4 text-fg placeholder:text-fg-muted"
          />
        </form>

        <nav aria-label="Tapis edisi" className="grid w-full grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:justify-center">
          {FILTERS.map((f) => {
            const active = filters.edisi === f.slug;
            return (
              <a
                key={f.slug}
                href={f.slug ? `?edisi=${f.slug}` : "?"}
                aria-current={active ? "true" : undefined}
                onClick={(e) => {
                  e.preventDefault();
                  change({ ...filters, edisi: f.slug });
                }}
                className={`min-h-tap inline-flex items-center justify-center rounded-pill border px-2 text-center text-sm transition-colors sm:px-3 ${
                  active ? "border-gold-deep bg-surface-raised font-semibold text-fg" : "border-line text-fg-muted hover:text-fg"
                }`}
              >
                {f.label}
              </a>
            );
          })}
        </nav>

        <p role="status" aria-live="polite" className="text-sm text-fg-muted">
          {tiers.length + covers.length} daripada {total} hasil
        </p>
      </div>

      {tiers.length > 0 && (
        <section aria-labelledby="katalog-edisi">
          <h3 id="katalog-edisi" className="ph-title mb-5 text-center text-2xl">Tiga edisi</h3>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {tiers.map((t) => (
              <article key={t.id} data-tier={t.id} className="ph-tier-card ph-lux flex flex-col gap-3 p-5">
                <div className="ph-book-stage mx-auto w-full max-w-[220px]">
                  <div className="ph-book-object">
                    <ProductCover name={t.title} src={t.artwork} seal={t.seal} tier={t.id} />
                  </div>
                </div>
                <div className="flex items-center gap-2.5">
                  <PsycheBadge id={TIER_PSYCHE[t.id as "poket" | "membangun" | "teman-hidup"]} tier={t.id as "poket" | "membangun" | "teman-hidup"} />
                  <h4 className="ph-title text-xl ph-tier-ink">{t.title}</h4>
                </div>
                <p className="font-display text-2xl ph-tier-ink">{t.price}</p>
                <p className="text-sm text-fg-muted">{t.size} · {t.summary}</p>
                {t.sample && (
                  <a href={t.sample} className="inline-flex min-h-tap items-center text-fg-accent underline">
                    Lihat pratonton bab
                  </a>
                )}
                <a
                  href={t.id === "poket" ? "#percuma" : `/beli/${t.id}`}
                  className="ph-cta mt-auto inline-flex min-h-tap items-center justify-center"
                >
                  {t.id === "poket" ? "Dapatkan percuma" : `Beli ${t.name}`}
                </a>
              </article>
            ))}
          </div>
        </section>
      )}

      {covers.length > 0 && (
        <section aria-labelledby="katalog-a4">
          <h3 id="katalog-a4" className="ph-title mb-5 text-center text-2xl">Buku A4 untuk dibaca sekarang</h3>
          <div className="ph-ebook-shelf" role="region" aria-label="Pratonton kulit ebook A4" tabIndex={0}>
            {covers.map((ebook) => (
              <figure key={ebook.slug} data-ebook={ebook.slug} className="flex flex-col gap-2.5">
                <div className="ph-book-stage">
                  <div className="ph-book-object">
                    <div className="ph-a4-cover">
                      <picture>
                        <source srcSet={ebook.webp} type="image/webp" />
                        <img
                          src={ebook.jpg}
                          alt={`Kulit A4 ebook ${ebook.title}`}
                          width={ebook.width}
                          height={ebook.height}
                          loading="lazy"
                          decoding="async"
                        />
                      </picture>
                    </div>
                  </div>
                </div>
                <figcaption className="flex flex-col gap-0.5">
                  <span className="flex items-center gap-2">
                    <PsycheBadge id={EBOOK_PSYCHE[ebook.slug] ?? "awareness"} tier="poket" className="!h-7 !w-7 [&_.ph-psyche-glyph]:!h-3.5 [&_.ph-psyche-glyph]:!w-3.5" />
                    <span className="text-[11px] font-semibold uppercase tracking-caps text-fg-accent">{ebook.pages}</span>
                  </span>
                  <span className="font-display text-base leading-snug text-fg">{ebook.title}</span>
                  <span className="text-xs leading-relaxed text-fg-muted">{ebook.summary}</span>
                </figcaption>
              </figure>
            ))}
          </div>
        </section>
      )}

      {tiers.length === 0 && covers.length === 0 && (
        <div className="mx-auto max-w-reading rounded border border-line bg-surface-raised p-6 text-center">
          <p className="text-fg">Tiada hasil untuk tapis ini. Cuba kata kunci lain atau pilih Semua.</p>
          <button
            type="button"
            onClick={() => change(EMPTY)}
            className="mt-4 min-h-tap rounded-pill border border-gold-deep px-4 text-sm text-fg"
          >
            Padam tapis
          </button>
        </div>
      )}
    </div>
  );
}
