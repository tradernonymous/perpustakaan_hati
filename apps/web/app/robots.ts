import type { MetadataRoute } from "next";
import { siteUrl } from "@/src/site";

export const dynamic = "force-dynamic";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin", "/api", "/pustaka", "/muat-turun", "/beli", "/terima-kasih", "/demo-bayar", "/astryx-scratch"],
    },
    sitemap: `${siteUrl()}/sitemap.xml`,
  };
}
