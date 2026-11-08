# AJE — Armazas Jaya Enterprise (the second design-system branch)

AJE is **Rahimam's company** (contact name on the company poster: **Pok Him**).
Perpustakaan Hati stays the personal, editorial brand; AJE is the shop. The two
never share a palette — AJE is always **black + gold**, Perpustakaan Hati always
leads with **green**.

Facts recorded from the company's own artwork (AJE "Waktu Urusniaga" poster,
Doop canvas `ONRYXHDlUj`, and the round seal):

| Field | Value |
|---|---|
| Legal name | Armazas Jaya Enterprise (AJE) |
| Registration | (PG0543717-U) |
| Since | 2016 |
| Positioning | One Stop Centre — "Beli di sini, pasti puas hati." |
| Contact | 010 552 4242 · 010 807 4242 (Pok Him) |
| Hours | Sat–Thu 8.30 PG – 11.45 MLM; Fri 2.15 PTG – 11.45 MLM |
| Daily break | 6.30 PTG – 8.20 MLM (makan & solat) |

Do not invent extra facts about the company; add them here only when Rahimam
confirms them.

## The turtle mark

The turtle is one drawing used in both of AJE's own logos: the green
"armazas JAYA Enterprise" wordmark and the black-and-gold "ONE STOP CENTRE AJE"
seal. These files ship the turtle **alone, background removed**, rebuilt as 3D
vector art.

| File | Colourway | Use |
|---|---|---|
| `docs/brand/assets/aje/aje-turtle-emerald.svg` | green face, dark-green extrusion | light grounds, co-branding with Perpustakaan Hati |
| `docs/brand/assets/aje/aje-turtle-noir.svg` | gold face, near-black extrusion | the AJE house look: black grounds, seals, signage |
| `*-1024.png`, `*-512.png`, `*-256.png` | same artwork, transparent | social, favicons, slides, print |

Web copies live in `apps/web/public/brand/aje/` under the same names. The
drawing is the company's own; never redraw, re-type or approximate it. Source
geometry: `packages/brand-tools/aje/turtle-path.txt`; rebuild with
`packages/brand-tools/build-aje-turtle.py` (see its docstring).

### Rules
1. **Two colourways only.** Emerald or gold-on-black. No rainbow, no gradient
   outside these two ramps, no flat mid-grey.
2. **Clear space** ≥ 25% of the mark's height on every side; minimum width
   120 px digital / 18 mm print.
3. **Never** crop the flippers or the tail tip, rotate, outline, or place the
   gold mark on a busy photo without a dark scrim.
4. **AJE surfaces are black + gold.** `#0a0a0a`/`#000` ground, gold `#c9a86a`
   (light `#e9cea2`, deep `#8a6224`) for type, rules and seals. Cream `#fdfee6`
   is the only light ground for AJE print.
5. **Never** use AJE gold as a Perpustakaan Hati primary, and never put the AJE
   turtle on a Perpustakaan Hati green card. If a layout needs both, separate
   them into their own bands with a hairline rule.
6. AJE copy is Bahasa Malaysia, direct and friendly ("Beli di sini, pasti puas
   hati"), never clinical and never the healing voice of Perpustakaan Hati.
