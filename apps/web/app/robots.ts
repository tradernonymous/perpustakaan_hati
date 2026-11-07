import type { MetadataRoute } from "next";
import { siteUrl } from "@/src/site";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/api", "/pustaka", "/muat-turun", "/beli", "/terima-kasih"] },
    sitemap: `${siteUrl()}/sitemap.xml`,
  };
}
