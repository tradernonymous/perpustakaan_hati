export type WorkbookInput = { status: "dating" | "engaged" | "married" | "recovering"; style: "anxious" | "avoidant" | "secure" };

export type Section = { heading: string; body: string };

export type Workbook = { title: string; sections: Section[] };

const STATUS_LABEL: Record<WorkbookInput["status"], string> = {
  dating: "Dating",
  engaged: "Bertunang",
  married: "Kahwin",
  recovering: "Pulih",
};

const STYLE_BODY: Record<WorkbookInput["style"], string> = {
  anxious: "Fokus pada menenangkan kecemasan dan komunikasi yang jelas tanpa menuntut kepastian segera.",
  avoidant: "Fokus pada mencipta ruang yang selamat untuk membuka diri sedikit demi sedikit.",
  secure: "Fokus pada menyelenggara kestabilan dan memperdalam keintiman yang sihat.",
};

export function generateWorkbook(input: WorkbookInput): Workbook {
  const label = STATUS_LABEL[input.status];
  const sections: Section[] = [
    { heading: `Pengenalan untuk ${label}`, body: `Supplement ini disusun untuk pembaca berstatus ${label} dengan corak ${input.style}.` },
    { heading: "Latihan untuk corak kamu", body: STYLE_BODY[input.style] },
    { heading: "Skrip yang sesuai", body: "Gunakan skrip Bincang Hati ke Hati yang paling dekat dengan situasi kamu sekarang." },
  ];
  return { title: `Workbook ${label} — ${input.style}`, sections };
}
