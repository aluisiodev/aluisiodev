"""Sprite do mini ciborgue (v3) — baseado na 2ª foto do Aluísio.

Cabelo preto liso e curto com franja (como na foto), rosto limpo,
só o olho direito (lado direito da imagem) modificado: placa metálica + luz vermelha.
Reator no peito, jaqueta techwear com LEDs ciano, braço biônico, voa com propulsores.
Sem magenta, sem cavanhaque, sem brincos.
"""
PX = 3

PAL = {
    "K": "#07040d",                                   # contorno
    "H": "#121018", "h": "#2a3242",                   # cabelo preto + brilho frio
    "S": "#e0aa84", "s": "#b8805e", "d": "#8e5a42",   # pele (luz, sombra, sombra funda)
    "l": "#b46c5c",                                   # boca
    "e": "#f2ebe6", "o": "#1b1214",                   # olho humano
    "M": "#a7b0c6", "m": "#5a6178", "n": "#e3e9f7",   # metal
    "R": "#ff3a3a", "r": "#7a0d14",                   # luz vermelha / soquete
    "J": "#1b1a24", "j": "#2c2b3a",                   # jaqueta
    "L": "#00f0ff",                                   # LEDs
    "C": "#e8fdff", "c": "#00c8e0",                   # reator
    "B": "#272832",                                   # calça
    "T": "#f5e663", "O": "#ff8a1f", "w": "#ffffff",   # chama do propulsor
}

HEAD = [
    "..........K....K.K..........",   # 0  fios soltos no topo
    ".........KHK..KHKHK..K......",
    "......KKKHHHKKHHHHHKKHK.....",
    ".....KHHHHHHHHHHhHHHHHHK....",
    "....KHHHhHHHHHHHHHHHHHHHK...",
    "...KHHHHHHHHHhhHHHHHHHHHHK..",
    "...KHHHHHHHHHHHHHHHHHHHHHHK.",
    "..KHHHHhHHHHHHHHHHHHHhHHHHK.",
    "..KHHHHHHHHHHHHHHHHHHHHHHHK.",
    "..KHHHHHHHHHHHHHHHHHHHHHHHK.",   # 9
    "..KHHHHHHHSHHHHHHSHHHHHHHHK.",   # 10 pontas da franja
    "..KHHHHSSSSHHSSSSSSHHHHmmHK.",   # 11 testa + placa começa na têmpora
    "..KHHSSSSSSSSSSSSSSHmmnnmHK.",   # 12
    ".KSKHSSHHHHSSSSSSHmnMMMMmKK.",   # 13 sobrancelha esq. / placa
    ".KSSKSSeooeSSSSSSmMrrrrMmKK.",   # 14 olho humano / soquete
    ".KsSKSSSSSSSSSSSSmMrRRrMmSK.",   # 15 luz vermelha
    ".KsSKSSSSSSSSSdSSmMrrrrMmsK.",   # 16
    "..KKSSSSSSSSSddSSSmMMMMmSsK.",   # 17 nariz
    "...KSSSSSSSSSSSSSSSmmmmSSK..",   # 18
    "...KsSSSSSSSSSSSSSSSSSSSsK..",   # 19
    "....KSSSSSSSllllSSSSSSSsK...",   # 20 boca
    "....KsSSSSSSSSSSSSSSSSssK...",   # 21
    ".....KssSSSSSSSSSSSSSsK.....",   # 22
    "......KKssSSSSSSSSssKK......",   # 23 queixo
    "........KKKsSSSSsKKK........",   # 24
]
HEAD_PROJECT = list(HEAD)
HEAD_PROJECT[15] = ".KsSKSSSSSSSSSSSSmMrCCrMmSK."   # olho biônico vira projetor

TORSO = [
    "..........KsSSSSsK..........",   # pescoço
    "......KKKKKjjjjjjjjKKKKK....",
    ".....KJJJJJjJJJJJJjJJJJJKK..",
    "....KJJLJJJJJJJJJJJJJLJJmnK.",
    "....KJJLJJJJJJccJJJJJLJJmMK.",
    "...KJjJLJJJJJcCCcJJJJLJJMmK.",
    "...KJjJLJJJJJcCCcJJJJLJJMmK.",
    "...KJjJLJJJJJJccJJJJJLJJnmK.",
    "...KJjJLJJJJJJJJJJJJJLJKMMK.",
    "...KSKJLJJJJJJJJJJJJJLJKnMnK",
    "...KKKJJJJJJJJJJJJJJJJJKKKK.",
    ".....KjjjjjjjjjjjjjjjjjK....",
]
LEGS = [
    ".......KBBBBK....KBBBBK.....",
    ".......KBBBBK....KBBBBK.....",
    ".......KBBBBK....KBBBBK.....",
    ".......KmMMmK....KmMMmK.....",
]
FLAME1 = [
    "........TwwT......TwwT......",
    "........OTTO......OTTO......",
    ".........OO........OO.......",
]
FLAME2 = [
    "........TwwT......TwwT......",
    ".........TT........TT.......",
    "............................",
]
FLAME_BOOST = [
    ".......TTwwTT....TTwwTT.....",
    "........OTTO......OTTO......",
    "........OTTO......OTTO......",
    ".........OO........OO.......",
]

FRAMES = {
    "hover1": HEAD + TORSO + LEGS + FLAME1,
    "hover2": HEAD + TORSO + LEGS + FLAME2,
    "boost": HEAD + TORSO + LEGS + FLAME_BOOST,
    "project": HEAD_PROJECT + TORSO + LEGS + FLAME1,
}
# espelhado: o olho biônico fica do lado esquerdo da imagem, virado para os painéis
FRAMES = {k: [r[::-1] for r in v] for k, v in FRAMES.items()}
W = 28
H = max(len(f) for f in FRAMES.values())
RED_LIGHT = (6 * PX, 15 * PX, 2 * PX, PX)       # x, y, w, h da luz vermelha
EYE = (6 * PX, 15.5 * PX)                       # origem da projeção

for name, rows in FRAMES.items():
    for i, r in enumerate(rows):
        assert len(r) == W, (name, i, len(r), r)
        assert all(c == "." or c in PAL for c in r), (name, i, r)


def svg_group(gid, rows, px=PX):
    out = [f'<g id="{gid}">']
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            out.append(f'<rect x="{x*px}" y="{y*px}" width="{run*px}" height="{px}" fill="{PAL[c]}"/>')
            x += run
    out.append("</g>")
    return "".join(out)


def to_image(rows, scale):
    from PIL import Image
    im = Image.new("RGBA", (W, len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != ".":
                h = PAL[c].lstrip("#")
                im.putpixel((x, y), tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return im.resize((W * scale, len(rows) * scale), Image.NEAREST)
