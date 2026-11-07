export const guardrails = [
  "Talian HEAL 15555",
  "Befrienders",
  "Befrienders KL: 03-7627 2929",
  "Jika dalam keadaan tidak selamat, hubungi 999",
];

const CRISIS = /bunuh diri|nak mati|hurt myself|kill myself|suicide/i;
const FUNCTIONING = /tak boleh berfungsi|can't function|tak boleh makan|tak boleh tidur|suicide plan|bunuh diri/i;

export function isCrisis(text: string): boolean {
  return CRISIS.test(text);
}

export function needsCounsellor(text: string): boolean {
  return FUNCTIONING.test(text);
}

export function companionReply(text: string): string {
  if (isCrisis(text)) {
    return "Terima kasih kerana berkongsi. Jika kamu sedang dalam kesusahan, sila hubungi Talian HEAL 15555 atau Befrienders 03-7627 2929. Jika dalam bahaya segera, hubungi 999.";
  }
  if (needsCounsellor(text)) {
    return "Aku dengar kau sedang sangat penat. Ini mungkin masa untuk bercakap dengan kaunselor berlesen. Aku ada di sini untuk menemani, tetapi profesional boleh bantu dengan lebih mendalam.";
  }
  return "Terima kasih kerana berkongsi. Aku di sini untuk dengar. Boleh kau ceritakan sedikit lagi tentang apa yang kau rasa sekarang?";
}
