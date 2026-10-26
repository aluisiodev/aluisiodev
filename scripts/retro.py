"""Retratos estilo videogame retrô a partir da foto: materiais + sombreamento em blocos + contorno.

Uso: python3 retro.py photo.jpg saida.png   (gera a cartela de opções)
"""
import colorsys
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

photo = Image.open(sys.argv[1] if __name__ == "__main__" else "photo.jpg").convert("RGB")
CROP = (70, 15, 330, 275)
SIL = Image.new("L", photo.size, 0)
ImageDraw.Draw(SIL).polygon([
    (150, 62), (163, 42), (200, 33), (240, 38), (258, 56), (263, 95), (258, 133),
    (247, 168), (236, 192), (262, 202), (305, 216), (332, 232), (346, 262),
    (362, 400), (34, 400), (48, 252), (70, 226), (112, 207), (162, 196),
    (166, 172), (151, 136), (145, 96)], fill=255)

BG, HAIR, SKIN, SHIRT, SUIT, FEAT = range(6)


def materials(n):
    src = photo.crop(CROP).filter(ImageFilter.MedianFilter(5)).resize((n, n), Image.LANCZOS)
    sil = SIL.crop(CROP).resize((n, n), Image.BOX)
    px, sp = src.load(), sil.load()
    lab = [[BG] * n for _ in range(n)]
    lum = [[0.0] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            r, g, b = px[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            lum[y][x] = v
            if sp[x, y] < 128:
                continue
            if (h < 0.11 or h > 0.95) and s > 0.22 and v > 0.42 and (y > n * 0.3 or s > 0.38 and v > 0.8):
                lab[y][x] = SKIN
            elif s < 0.16 and v > 0.66 and y > n * 0.6:
                lab[y][x] = SHIRT
            elif y < n * 0.58:
                lab[y][x] = HAIR
            else:
                lab[y][x] = SUIT
    # pixels escuros cercados de pele = olhos/boca/sobrancelhas
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if lab[y][x] == HAIR:
                skin_nb = sum(lab[y + dy][x + dx] == SKIN for dy in (-1, 0, 1) for dx in (-1, 0, 1))
                if skin_nb >= 5:
                    lab[y][x] = FEAT
    # filtro de moda para limpar ruído (mantém traços do rosto)
    out = [row[:] for row in lab]
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            if lab[y][x] == FEAT:
                continue
            nb = [lab[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 6:
                out[y][x] = best
    return out, lum


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def render(n, ramps, bg_fn, outline="#07040d", levels=3, inner=True):
    lab, lum = materials(n)
    img = Image.new("RGB", (n, n))
    p = img.load()
    # níveis por material usando quantis da própria luminância (sombreado em blocos)
    by = {}
    for y in range(n):
        for x in range(n):
            by.setdefault(lab[y][x], []).append(lum[y][x])
    cuts = {}
    for m, vals in by.items():
        vals = sorted(vals)
        cuts[m] = [vals[int(len(vals) * k / levels)] for k in range(1, levels)]
    for y in range(n):
        for x in range(n):
            m = lab[y][x]
            if m == BG:
                p[x, y] = bg_fn(x, y, n)
                continue
            ramp = ramps[m]
            lvl = sum(lum[y][x] > c for c in cuts[m])
            lvl = min(lvl, len(ramp) - 1)
            p[x, y] = hexrgb(ramp[lvl])
    o = hexrgb(outline)
    edge = [[False] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if lab[y][x] == BG:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < n and 0 <= yy < n and lab[yy][xx] == BG:
                    edge[y][x] = True
            # linha interna entre cabelo e rosto (como nos sprites)
            if inner and lab[y][x] == HAIR and y + 1 < n and lab[y + 1][x] == SKIN:
                edge[y][x] = True
    for y in range(n):
        for x in range(n):
            if edge[y][x] and y < n - 1:
                p[x, y] = o
    return img


def synthwave_bg(x, y, n):
    t = y / n
    if t > 0.62 and (y % 3 == 0 or x % 6 == 0):
        return (0, 150, 180)
    bands = [(22, 8, 48), (40, 12, 78), (70, 18, 110), (110, 30, 120)]
    return bands[min(3, int(t * 4.2))]


def flat_bg(c):
    return lambda x, y, n: c


def checker_bg(a, b):
    return lambda x, y, n: a if ((x // 4) + (y // 4)) % 2 else b


SKIN_R = ["#8e5a42", "#c98a66", "#f0bf98"]
STYLES = [
    ("16-bit RPG", "retrato de diálogo de RPG: 48px, 3 tons por material, contorno", 48,
     {HAIR: ["#0e0b14", "#231c2c", "#3a3550"], SKIN: SKIN_R, SHIRT: ["#9aa3c0", "#d7deef", "#ffffff"],
      SUIT: ["#262838", "#3e4258", "#5d6380"], FEAT: ["#3a1f22"]}, synthwave_bg, 3),
    ("NES", "8-bit clássico: 32px, paleta mínima, fundo chapado", 32,
     {HAIR: ["#000000", "#2b2b2b"], SKIN: ["#a0522d", "#f0a868"], SHIRT: ["#bcbcbc", "#fcfcfc"],
      SUIT: ["#3c3c5c", "#6c6c8c"], FEAT: ["#000000"]}, flat_bg((0, 56, 120)), 2),
    ("Game Boy neon", "4 tons apenas, com a paleta trocada por ciano/roxo: 40px", 40,
     {HAIR: ["#0b0820", "#0b0820", "#2a1e5c"], SKIN: ["#2a1e5c", "#1a9bb0", "#a8fbff"],
      SHIRT: ["#1a9bb0", "#a8fbff", "#a8fbff"], SUIT: ["#0b0820", "#2a1e5c", "#1a9bb0"], FEAT: ["#0b0820"]},
     checker_bg((11, 8, 32), (20, 14, 48)), 3),
    ("Arcade (seleção de lutador)", "16-bit com mais contraste e fundo listrado, como tela de 'escolha seu personagem'", 56,
     {HAIR: ["#08060c", "#1c1622", "#34304a", "#4c4a6a"], SKIN: ["#7a4430", "#b8744e", "#e8a678", "#ffd6b0"],
      SHIRT: ["#8c94b4", "#c8d0ea", "#f4f6ff", "#ffffff"], SUIT: ["#1e2030", "#30344a", "#4a5070", "#6a7298"],
      FEAT: ["#2a1418"]},
     lambda x, y, n: (14, 30, 70) if (x + y) % 8 < 4 else (24, 48, 100), 4),
]

if __name__ == "__main__":
    TILE, GAP = 280, 22
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 17)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
    Wd = len(STYLES) * (TILE + GAP) + GAP
    sheet = Image.new("RGB", (Wd, TILE + 110), (10, 6, 19))
    d = ImageDraw.Draw(sheet)
    for i, (name, desc, n, ramps, bgf, lv) in enumerate(STYLES):
        img = render(n, ramps, bgf, levels=lv).resize((TILE, TILE), Image.NEAREST)
        x = GAP + i * (TILE + GAP)
        sheet.paste(img, (x, 20))
        d.rectangle([x - 3, 17, x + TILE + 2, 22 + TILE], outline=(0, 240, 255), width=2)
        d.text((x, TILE + 34), f"{i+1}. {name}", font=font, fill=(0, 240, 255))
        words, line, ly = desc.split(), "", TILE + 60
        for w in words:
            if len(line + " " + w) > 38:
                d.text((x, ly), line.strip(), font=small, fill=(236, 230, 255)); ly += 16; line = ""
            line += " " + w
        d.text((x, ly), line.strip(), font=small, fill=(236, 230, 255))
    sheet.save(sys.argv[2])
    print(sys.argv[2], sheet.size)
