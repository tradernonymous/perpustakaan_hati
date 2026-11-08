/**
 * Marquee ticker (ported from website_sam `.ticker-*`): one row of what is
 * inside the books, duplicated so a translateX(-50%) loop is seamless, faded
 * at both edges with a mask, paused on hover/focus. The duplicate row is
 * aria-hidden so screen readers hear the list once. Reduced motion: static,
 * wrapping row (see .ph-ticker in design-tokens.css).
 */
const ITEMS = [
  "Kad Refleksi",
  "7 Hari Reset",
  "Ceklis Pencetus Attach",
  "Skrip Bincang Hati ke Hati",
  "Buku Kerja 30 Hari",
  "Nota Suara Rahimam",
  "Red flag & green flag",
  "Bahasa Melayu yang dekat di hati",
];

function Row({ hidden = false }: { hidden?: boolean }) {
  return (
    <ul className="ph-ticker-row" aria-hidden={hidden || undefined}>
      {ITEMS.map((t) => (
        <li key={t}>
          <svg viewBox="0 0 10 10" width="10" height="10" aria-hidden="true" focusable="false">
            <path d="M5 0l5 5-5 5-5-5z" fill="#7a5a22" />
          </svg>
          {t}
        </li>
      ))}
    </ul>
  );
}

export function Ticker() {
  return (
    <div className="ph-ticker" role="region" aria-label="Kandungan buku" tabIndex={0}>
      <div className="ph-ticker-track">
        <Row />
        <Row hidden />
      </div>
    </div>
  );
}
