export function anonymize(name: string, dilemma: string): string {
  return dilemma.replace(name, "[nama disembunyikan]").trim();
}

export function acceptsSurat(input: { dilemma: string }): boolean {
  return input.dilemma.trim().length >= 3;
}
