import { CHAPTERS } from "@/src/content";

export function ChapterPreview() {
  return (
    <div className="mx-auto max-w-reading rounded bg-cream px-5 py-8 text-ink md:px-10">
      <ol className="flex flex-col gap-6 font-reading">
        {CHAPTERS.map((c) => (
          <li key={c.no} className={`ph-page-in leading-[1.7] ${c.pending ? "opacity-60" : ""}`}>
            <p className="font-body text-xs font-semibold uppercase tracking-[0.18em] text-gold-deep">Bab {c.no}</p>
            <h3 className={`font-display text-2xl ${c.pending ? "italic text-green-800/70" : "text-green-900"}`}>{c.title}</h3>
            <p className="text-[17px]">{c.note}</p>
          </li>
        ))}
      </ol>
      <p className="mt-6 font-body text-sm text-green-800">Antara bab dalam Edisi Membangun.</p>
    </div>
  );
}
