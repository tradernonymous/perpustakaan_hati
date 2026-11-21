import { SafetyFooter } from "./SafetyFooter";
import { SiteHeader } from "./SiteHeader";

/** Frame for inner pages (checkout, thank-you, library). Nav links point back to the home page sections. */
export function PageShell({ title, intro, children }: { title: string; intro?: string; children: React.ReactNode }) {
  return (
    <>
      <SiteHeader base="/" />
      <main id="utama" tabIndex={-1} className="min-h-[70vh] bg-surface px-4 py-8 sm:px-5 md:py-16">
        <div className="mx-auto mb-5 max-w-reading text-center md:mb-8">
          <h1 className="ph-title text-balance text-3xl text-fg md:text-4xl">{title}</h1>
          {intro && <p className="mt-3 text-fg-muted">{intro}</p>}
        </div>
        {children}
      </main>
      <SafetyFooter base="/" />
    </>
  );
}
