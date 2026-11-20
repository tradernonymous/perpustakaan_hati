import { temanHatiEnabled } from "@/src/feature-flags";
import type { MetadataRoute } from "next";
import { siteUrl } from "@/src/site";

export const dynamic = "force-dynamic";

const PUBLIC_ROUTES = [
  { path: "/", changeFrequency: "weekly" as const, priority: 1 },
  ...(temanHatiEnabled ? [{ path: "/teman-hati", changeFrequency: "weekly" as const, priority: 0.8 }] : []),
  { path: "/kad-jujur-hati", changeFrequency: "weekly" as const, priority: 0.8 },
  { path: "/cermin-pasangan", changeFrequency: "weekly" as const, priority: 0.8 },
  { path: "/cabaran-7-hari", changeFrequency: "weekly" as const, priority: 0.7 },
  { path: "/hadiah-hati", changeFrequency: "weekly" as const, priority: 0.7 },
  { path: "/surat-hati", changeFrequency: "weekly" as const, priority: 0.7 },
  { path: "/booking", changeFrequency: "weekly" as const, priority: 0.7 },
  { path: "/kelab", changeFrequency: "monthly" as const, priority: 0.6 },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteUrl();
  return PUBLIC_ROUTES.map((r) => ({
    url: `${base}${r.path}`,
    changeFrequency: r.changeFrequency,
    priority: r.priority,
  }));
}
