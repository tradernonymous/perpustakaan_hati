/**
 * Gilt section ornament — the flanked diamond rule from the cinematic lockup
 * (build-logos.py `flank()`): two tapering gold hairlines, a diamond tip on
 * each inner end and an emerald diamond in the middle. Decoration only.
 * Imported by app/page.tsx (every section title). No props, no data.
 */
export function SectionOrnament({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 240 14"
      width="240"
      height="14"
      className={`ph-ornament mx-auto block h-3.5 w-48 md:w-60 ${className}`}
      aria-hidden="true"
      focusable="false"
    >
      <path fill="#c9a86a" d="M0,7 L96,5.6 L96,8.4 Z" />
      <path fill="#c9a86a" d="M240,7 L144,5.6 L144,8.4 Z" />
      <path fill="#e9cea2" d="M104,2 l5,5 l-5,5 l-5,-5 Z" />
      <path fill="#e9cea2" d="M136,2 l5,5 l-5,5 l-5,-5 Z" />
      <path fill="#7db895" d="M120,0 l7,7 l-7,7 l-7,-7 Z" />
    </svg>
  );
}
