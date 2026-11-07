// Cells starting with = + - @ are formulas in Excel/Sheets. Prefix a quote so
// a hostile sign-up (e.g. "=HYPERLINK(...)") cannot run when Jack opens the export.
function cell(v: string | number | null): string {
  if (v === null) return "";
  let s = String(v);
  if (/^[=+\-@]/.test(s)) s = `'${s}`;
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function toCsv(header: string[], rows: (string | number | null)[][]): string {
  return [header, ...rows].map((r) => r.map(cell).join(",") + "\r\n").join("");
}
