// Delivery copy in Bahasa Melayu. Plain text so it works in every mail app and WhatsApp.
export type Link = { name: string; url: string };

export function emailSubject(): string {
  return "Buku kamu dari Perpustakaan Hati sudah sedia";
}

export function emailText(links: Link[], libraryUrl: string): string {
  return [
    "Terima kasih kerana mempercayai Perpustakaan Hati.",
    "",
    "Pautan muat turun kamu (sah selama 7 hari):",
    ...links.map((l) => `- ${l.name}: ${l.url}`),
    "",
    `Pautan tamat? Buka Pustaka Saya untuk pautan baharu: ${libraryUrl}`,
    "",
    "Setiap salinan ditandakan dengan nama pembeli. Mohon jangan kongsi.",
    "Jika kamu perlu bercakap dengan seseorang sekarang, hubungi Talian HEAL 15555.",
    "",
    "Perpustakaan Hati oleh @rahimam",
  ].join("\n");
}

export function whatsappLinkText(links: Link[]): string {
  return links.map((l) => `${l.name}: ${l.url}`).join("\n");
}

export function loginEmailText(url: string): string {
  return [
    "Klik pautan ini untuk membuka Pustaka Saya (sah 30 minit):",
    url,
    "",
    "Jika bukan kamu yang meminta, abaikan e-mel ini.",
  ].join("\n");
}
