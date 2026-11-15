import { siteUrl } from "@/src/site";

/**
 * Organization + WebSite structured data for the homepage.
 *
 * The FAQ block (components/Faq.tsx) already covers FAQPage. This adds the
 * two publisher-level types search engines use to tie the brand and its
 * social handle to the site.
 *
 * There is no public search route, so WebSite carries no SearchAction:
 * claiming a search the site cannot serve would be a lie to the crawler.
 */
export function OrganizationSchema() {
  const url = siteUrl();
  const author = {
    "@type": "Person",
    name: "Rahimam",
    url: "https://www.threads.net/@rahimam",
    sameAs: ["https://www.threads.net/@rahimam"],
  };

  const organization = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": `${url}/#organization`,
    name: "Perpustakaan Hati",
    url,
    logo: {
      "@type": "ImageObject",
      url: `${url}/brand/og-image.png`,
      width: 1200,
      height: 630,
    },
    image: `${url}/brand/og-image.png`,
    description:
      "Bahan bacaan psikologi hubungan dalam Bahasa Melayu oleh Rahimam. Mulakan dengan Edisi Poket, percuma.",
    author,
    founder: author,
    sameAs: ["https://www.threads.net/@rahimam"],
  };

  const website = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${url}/#website`,
    name: "Perpustakaan Hati",
    url,
    description:
      "Bahan bacaan psikologi hubungan dalam Bahasa Melayu oleh Rahimam. Mulakan dengan Edisi Poket, percuma.",
    inLanguage: "ms-MY",
    publisher: { "@id": `${url}/#organization` },
    author,
  };

  return (
    <>
      {[organization, website].map((block) => (
        <script
          key={String(block["@type"])}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(block).replace(/</g, "\\u003c") }}
        />
      ))}
    </>
  );
}
