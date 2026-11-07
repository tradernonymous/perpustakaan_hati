import { SafetyFooter } from "./SafetyFooter";
import { SiteHeader } from "./SiteHeader";

/** Frame for inner pages (checkout, thank-you, library). Nav links point back to the home page sections. */
export function PageShell({ title, intro, children }: { title: string; intro?: string; children: React.ReactNode }) {
  return (
    <>
      <SiteHeader base="/" />
      <main id="utama" className="min-h-[70vh] bg-forest-night px-5 py-12 md:py-16">
        <div className="mx-auto mb-8 max-w-reading text-center">
          <h1 className="ph-title text-3xl text-gold-light md:text-4xl">{title}</h1>
          {intro && <p className="mt-3 text-on-dark-muted">{intro}</p>}
        </div>
        {children}
      </main>
      <SafetyFooter base="/" />
    </>
  );
}
