"""Gera os SVGs animados do README (cabeçalho, stack e cards de repositório).

Tudo é SVG puro com SMIL, sem fontes ou imagens externas, para funcionar
dentro do <img> do GitHub. O avatar entra embutido em base64.

Uso: python3 gen.py   (lê assets/avatar-pixel.png, escreve em assets/)
"""
import base64
import io
from xml.sax.saxutils import escape

from PIL import Image

# ───────────────────────── paleta ─────────────────────────
BG = "#0a0613"
PANEL_EDGE = "#2c1747"
GRID = "#160c28"
CYAN = "#00f0ff"
MAGENTA = "#ff2ec4"
YELLOW = "#f5e663"
VIOLET = "#9d5cff"
TEXT = "#ece6ff"
DIM = "#8b7fb3"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CHAR_W = 0.61  # largura média de um caractere monoespaçado, em em

# ───────────────────── sprite do ciborgue ─────────────────────
# Versão PROVISÓRIA: cabelo escuro, blazer cinza e camisa branca como na foto,
# visor ciano + olho magenta e braço biônico. Será trocada pela versão feita
# a partir da imagem que o Aluísio vai mandar.
SP = {
    "K": "#07040d", "H": "#2b1f1b", "h": "#55423a", "S": "#e2aa84", "s": "#b97d5f",
    "V": CYAN, "v": "#00788c", "E": MAGENTA, "M": "#9aa3b8", "m": "#545b70",
    "B": "#41434f", "b": "#2b2c35", "W": "#e3e9f2", "C": CYAN,
}
HEAD = [
    "....KKKKKKKK....",
    "...KHHhHHHHHK...",
    "..KHHHHhHHHHHK..",
    "..KmHHSSSSSHHK..",
    "..KMmSSSSSSSHK..",
    "..KVVVVSSKKSSK..",
    "..KVEEVSSSSSSK..",
    "..KmMSSSSSSSSK..",
    "...KMSSssSSSK...",
    "....KSSSSSSK....",
    "......KSSKK.....",
]
TORSO = [
    "...KKBBWWWBBKK..",
    "..KmMBBWWWBBBBK.",
    ".KmMMBBbWWbBBBBK",
    ".KmCMBBWWWBBBbBK",
    ".KmMMBBWWWBBBbBK",
    ".KMMKBBWWWBBBKSK",
    ".KKKKBBBBBBBBKKK",
]
TORSO_AIM = [  # braço biônico apontando para a esquerda
    "...KKBBWWWBBKK..",
    "KKKKKBBWWWBBBBK.",
    "VMMMMMBbWWbBBBBK",
    "KKKKKBBWWWBBBbBK",
    "....KBBWWWBBBbBK",
    "....KBBWWWBBBKSK",
    "....KBBBBBBBBKKK",
]
LEGS_STAND = [
    "....KbbbKbbbK...",
    "....KbbbKbbbK...",
    "....KbbbKbbbK...",
    "....KmmK.KmmK...",
    "...KKKKK.KKKKK..",
]
LEGS_WALK1 = [
    "....KbbbKbbbK...",
    "...KbbbK..KbbK..",
    "..KbbbK....KbbK.",
    "..KmmK.....KmmK.",
    ".KKKKK....KKKKK.",
]
LEGS_WALK2 = [
    "....KbbbKbbbK...",
    "....KbbKbbbK....",
    ".....KbbbbK.....",
    ".....KmmmmK.....",
    "....KKKKKKKK....",
]
FRAMES = {
    "stand": HEAD + TORSO + LEGS_STAND,
    "walk1": HEAD + TORSO + LEGS_WALK1,
    "walk2": HEAD + TORSO + LEGS_WALK2,
    "aim": HEAD + TORSO_AIM + LEGS_STAND,
}
PX = 4                                   # tamanho de cada pixel do sprite
SPRITE_W, SPRITE_H = 16 * PX, len(FRAMES["stand"]) * PX
EMITTER = (0, (11 + 2) * PX + PX // 2)   # ponta do braço na pose "aim"


def sprite_group(gid, rows):
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
            out.append(f'<rect x="{x*PX}" y="{y*PX}" width="{run*PX}" height="{PX}" fill="{SP[c]}"/>')
            x += run
    out.append("</g>")
    return "".join(out)


def sprite_defs(prefix):
    return "".join(sprite_group(f"{prefix}-{k}", v) for k, v in FRAMES.items())


# ───────────────────── utilidades de animação ─────────────────────
class Timeline:
    def __init__(self, total, loop):
        self.T = total
        self.loop = loop

    def _tail(self):
        if self.loop:
            return f'dur="{self.T}s" repeatCount="indefinite"'
        return f'dur="{self.T}s" fill="freeze"'

    def kt(self, t):
        return f"{min(max(t / self.T, 0), 1):.4f}"

    def discrete(self, attr, points, default):
        """points: [(t, valor), ...] -> valor vale a partir de t (degrau)."""
        pts = [(0, default)] + sorted(points)
        vals, kts = [], []
        for t, v in pts:
            if kts and kts[-1] == self.kt(t):
                vals[-1] = str(v)
                continue
            vals.append(str(v))
            kts.append(self.kt(t))
        return (f'<animate attributeName="{attr}" calcMode="discrete" values="{";".join(vals)}" '
                f'keyTimes="{";".join(kts)}" {self._tail()}/>')

    def show(self, intervals, attr="opacity"):
        pts = []
        for a, b in intervals:
            pts.append((a, 1))
            if b < self.T:            # intervalo que vai até o fim fica ligado no congelamento
                pts.append((b, 0))
        return self.discrete(attr, pts, 0)

    def linear(self, attr, points, transform=None):
        """points: [(t, valor)] interpolado linearmente; segura nas pontas."""
        pts = sorted(points)
        if pts[0][0] > 0:
            pts = [(0, pts[0][1])] + pts
        if pts[-1][0] < self.T:
            pts = pts + [(self.T, pts[-1][1])]
        vals = ";".join(str(v) for _, v in pts)
        kts = ";".join(self.kt(t) for t, _ in pts)
        if transform:
            return (f'<animateTransform attributeName="transform" type="{transform}" values="{vals}" '
                    f'keyTimes="{kts}" {self._tail()}/>')
        return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kts}" {self._tail()}/>'

    def steps(self, attr, start, end, t0, t1, n, hide_after=None):
        """Valor sobe de start a end em n degraus entre t0 e t1."""
        pts = [(t0 + (t1 - t0) * i / n, round(start + (end - start) * i / n, 2)) for i in range(n + 1)]
        if hide_after is not None:
            pts.append((hide_after, start))
        return self.discrete(attr, pts, start)


def typed_clip(tl, cid, x, y, fs, nchars, t0, cps=22, hide_after=None):
    """clipPath que 'digita' o texto caractere a caractere."""
    cw = fs * CHAR_W
    t1 = t0 + nchars / cps
    full = nchars * cw + fs * 2
    anim = tl.steps("width", 0, full, t0, t1, nchars, hide_after)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y - fs}" width="0" height="{fs * 1.5}">{anim}</rect></clipPath>',
            t1)


def walk_frames(tl, prefix, t0, t1, flip_every=0.14):
    """Intervalos alternando walk1/walk2 entre t0 e t1."""
    w1, w2 = [], []
    t, i = t0, 0
    while t < t1:
        nxt = min(t + flip_every, t1)
        (w1 if i % 2 == 0 else w2).append((t, nxt))
        t, i = nxt, i + 1
    return (f'<use href="#{prefix}-walk1">{tl.show(w1)}</use>'
            f'<use href="#{prefix}-walk2">{tl.show(w2)}</use>')


def panel(w, h, title, uid):
    """Fundo comum: painel escuro, grade, barra de janela e scanlines."""
    return f'''
<defs>
  <pattern id="{uid}-grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0H0V24" fill="none" stroke="{GRID}" stroke-width="1"/>
  </pattern>
  <pattern id="{uid}-scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#000" opacity="0.35"/>
  </pattern>
  <linearGradient id="{uid}-edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{MAGENTA}"/>
  </linearGradient>
</defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{BG}"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#{uid}-grid)"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="none" stroke="url(#{uid}-edge)" stroke-width="1.5" opacity="0.9"/>
<g font-family="{MONO}">
  <circle cx="22" cy="20" r="5" fill="{MAGENTA}"/><circle cx="40" cy="20" r="5" fill="{YELLOW}"/><circle cx="58" cy="20" r="5" fill="{CYAN}"/>
  <text x="{w/2}" y="25" fill="{DIM}" font-size="13" text-anchor="middle">{escape(title)}</text>
</g>
<line x1="1" y1="38" x2="{w-1}" y2="38" stroke="{PANEL_EDGE}"/>
'''


def scan_overlay(w, h, uid):
    return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#{uid}-scan)" pointer-events="none"/>'


def svg_wrap(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}">\n<title>{escape(label)}</title>\n{body}\n</svg>\n')


def avatar_b64(path, scale):
    im = Image.open(path)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


# ───────────────────────── cabeçalho ─────────────────────────
def header():
    W, H = 900, 350
    uid = "h"
    tl = Timeline(12.0, loop=False)
    AX, AY, AS = 40, 64, 240              # moldura do avatar
    rows = 48
    CX, CY = 300, AY + AS - SPRITE_H       # onde o ciborgue para

    t_walk0, t_walk1 = 0.3, 1.7
    t_aim = 1.9
    t_scan0, t_scan1 = 2.1, 4.1
    t_glitch = 4.15
    t_done = 4.5

    b = [panel(W, H, "aluisio@cyberdeck: ~ — sessão 0x2A", uid)]
    b.append(f"<defs>{sprite_defs('cy')}"
             f'<radialGradient id="h-glow"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.8"/>'
             f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="h-name" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/>'
             f'<stop offset="1" stop-color="{MAGENTA}"/></linearGradient></defs>')

    # moldura vazia "aguardando sinal"
    b.append(f'<rect x="{AX}" y="{AY}" width="{AS}" height="{AS}" fill="#0d0819" stroke="{PANEL_EDGE}"/>')
    b.append(f'<g font-family="{MONO}" font-size="13" fill="{DIM}" text-anchor="middle">'
             f'<text x="{AX+AS/2}" y="{AY+AS/2-4}">[ AGUARDANDO SINAL ]'
             f'{tl.discrete("opacity", [(t, (i % 2)) for i, t in enumerate([0.5,0.9,1.3,1.7,2.1])] + [(t_scan0, 0)], 1)}</text>'
             f'<text x="{AX+AS/2}" y="{AY+AS/2+16}" font-size="11">id: ????????'
             f'{tl.discrete("opacity", [(t_scan0, 0)], 1)}</text></g>')

    # avatar revelado linha a linha (48 linhas = 48 pixels do avatar)
    img = avatar_b64("assets/avatar-pixel.png", 5)
    reveal = tl.steps("height", 0, AS, t_scan0, t_scan1, rows)
    b.append(f'<clipPath id="h-rev"><rect x="{AX}" y="{AY}" width="{AS}" height="0">{reveal}</rect></clipPath>')
    b.append(f'<image href="data:image/png;base64,{img}" x="{AX}" y="{AY}" width="{AS}" height="{AS}" '
             f'clip-path="url(#h-rev)" style="image-rendering:pixelated"/>')

    # glitch: duas fatias do avatar deslocadas por um instante
    for i, (sy, sh, dx) in enumerate([(AY + 70, 18, 9), (AY + 150, 10, -7)]):
        b.append(f'<clipPath id="h-gl{i}"><rect x="{AX}" y="{sy}" width="{AS}" height="{sh}"/></clipPath>'
                 f'<g clip-path="url(#h-gl{i})" opacity="0">'
                 f'<image href="data:image/png;base64,{img}" x="{AX+dx}" y="{AY}" width="{AS}" height="{AS}" style="image-rendering:pixelated"/>'
                 f'{tl.show([(t_glitch, t_glitch + 0.12), (t_glitch + 0.22, t_glitch + 0.3)])}</g>')

    # linha de scan + feixe saindo do braço do ciborgue
    scan_y = tl.linear("y1", [(t_scan0, AY), (t_scan1, AY + AS)])
    scan_y2 = tl.linear("y2", [(t_scan0, AY), (t_scan1, AY + AS)])
    ex, ey = CX + EMITTER[0], CY + EMITTER[1]
    b.append(f'<g opacity="0">{tl.show([(t_scan0, t_scan1)])}'
             f'<line x1="{AX-4}" x2="{AX+AS+4}" y1="{AY}" y2="{AY}" stroke="{CYAN}" stroke-width="3">{scan_y}{scan_y2}</line>'
             f'<line x1="{AX-4}" x2="{AX+AS+4}" y1="{AY}" y2="{AY}" stroke="{CYAN}" stroke-width="12" opacity="0.18">{scan_y}{scan_y2}</line>'
             f'<line x1="{ex}" y1="{ey}" x2="{AX+AS}" y2="{AY}" stroke="{MAGENTA}" stroke-width="2" opacity="0.9">'
             f'{tl.linear("y2", [(t_scan0, AY), (t_scan1, AY + AS)])}</line>'
             f'<circle cx="{ex}" cy="{ey}" r="9" fill="url(#h-glow)"/></g>')

    # cantoneiras da moldura (acendem depois do reveal)
    c = 16
    corners = (f"M{AX-6} {AY-6+c}V{AY-6}H{AX-6+c} M{AX+AS+6-c} {AY-6}H{AX+AS+6}V{AY-6+c} "
               f"M{AX+AS+6} {AY+AS+6-c}V{AY+AS+6}H{AX+AS+6-c} M{AX-6+c} {AY+AS+6}H{AX-6}V{AY+AS+6-c}")
    b.append(f'<path d="{corners}" fill="none" stroke="{PANEL_EDGE}" stroke-width="2"/>')
    b.append(f'<path d="{corners}" fill="none" stroke="{CYAN}" stroke-width="2" opacity="0">'
             f'{tl.show([(t_done, tl.T + 1)])}</path>')
    b.append(f'<g opacity="0" font-family="{MONO}" font-size="12">{tl.show([(t_done, tl.T + 1)])}'
             f'<rect x="{AX}" y="{AY+AS+12}" width="{AS}" height="22" fill="{CYAN}" opacity="0.1"/>'
             f'<text x="{AX+10}" y="{AY+AS+27}" fill="{CYAN}">ID ▸ aluisiodev</text>'
             f'<text x="{AX+AS-10}" y="{AY+AS+27}" fill="{MAGENTA}" text-anchor="end">● ONLINE</text></g>')

    # ciborgue: entra andando, mira, escaneia, fica parado piscando o olho
    move = tl.linear(None, [(t_walk0, f"-90 {CY}"), (t_walk1, f"{CX} {CY}")], transform="translate")
    eye = tl.discrete("opacity", [(t_done + i * 0.9, 0.35 if i % 2 else 1) for i in range(9)], 1)
    b.append(f'<g transform="translate(-90 {CY})">{move}'
             f'{walk_frames(tl, "cy", t_walk0, t_walk1)}'
             f'<use href="#cy-stand">{tl.show([(0, t_walk0), (t_walk1, t_aim), (t_scan1, tl.T + 1)])}</use>'
             f'<use href="#cy-aim">{tl.show([(t_aim, t_scan1)])}</use>'
             f'<rect x="{3*PX}" y="{5*PX}" width="{4*PX}" height="{2*PX}" fill="{MAGENTA}" opacity="0">'
             f'{tl.discrete("opacity", [(t_scan1 + 0.2, 0.0)] + [(t_done + i * 0.9, 0.55 if i % 2 == 0 else 0.1) for i in range(9)], 0)}</rect>'
             f'</g>')
    _ = eye

    # coluna de texto
    TX = 400
    lines = []
    clips = []

    def prompt_line(y, cmd, t0, cid):
        clip, t1 = typed_clip(tl, cid, TX, y, 17, 2 + len(cmd), t0)
        clips.append(clip)
        lines.append(f'<text x="{TX}" y="{y}" font-size="17" clip-path="url(#{cid})">'
                     f'<tspan fill="{MAGENTA}">$</tspan><tspan fill="{TEXT}"> {escape(cmd)}</tspan></text>')
        return t1

    t = prompt_line(78, "whoami", t_done + 0.3, "h-c1")
    t_name = t + 0.35
    lines.append(f'<g opacity="0">{tl.show([(t_name, tl.T + 1)])}'
                 f'<text x="{TX-2}" y="140" font-size="52" font-weight="800" fill="{MAGENTA}" opacity="0.7">ALUÍSIO'
                 f'{tl.linear("x", [(t_name, TX - 10), (t_name + 0.25, TX - 3)])}</text>'
                 f'<text x="{TX+2}" y="140" font-size="52" font-weight="800" fill="{CYAN}" opacity="0.7">ALUÍSIO'
                 f'{tl.linear("x", [(t_name, TX + 10), (t_name + 0.25, TX + 3)])}</text>'
                 f'<text x="{TX}" y="140" font-size="52" font-weight="800" fill="url(#h-name)">ALUÍSIO</text></g>')
    sub = "dev full stack // back-end · cloud · segurança"
    clip, t = typed_clip(tl, "h-c2", TX, 172, 15, len(sub), t_name + 0.4, cps=40)
    clips.append(clip)
    lines.append(f'<text x="{TX}" y="172" font-size="15" fill="{DIM}" clip-path="url(#h-c2)">{escape(sub)}</text>')

    t = prompt_line(222, "cat missao.txt", t + 0.4, "h-c3")
    bio = ["Construo back-ends rápidos com C# e Go,",
           "interfaces com TypeScript e coloco tudo",
           "de pé com Docker e Kubernetes."]
    for i, line in enumerate(bio):
        lines.append(f'<text x="{TX}" y="{252 + i*24}" font-size="15" fill="{TEXT}" opacity="0">{escape(line)}'
                     f'{tl.show([(t + 0.3 + i * 0.25, tl.T + 1)])}</text>')
    t_cur = t + 0.3 + len(bio) * 0.25 + 0.2
    blink = [(t_cur + i * 0.5, t_cur + i * 0.5 + 0.25) for i in range(0, int((tl.T - t_cur) / 0.5))]
    blink.append((tl.T - 0.01, tl.T + 1))
    lines.append(f'<text x="{TX}" y="{252 + len(bio)*24 + 8}" font-size="17">'
                 f'<tspan fill="{MAGENTA}" opacity="0">$ {tl.show([(t_cur, tl.T + 1)])}</tspan>'
                 f'<tspan fill="{CYAN}" opacity="0">█{tl.show(blink)}</tspan></text>')

    b.append(f'<defs>{"".join(clips)}</defs><g font-family="{MONO}">{"".join(lines)}</g>')
    b.append(scan_overlay(W, H, uid))
    label = ("Aluísio (aluisiodev) — dev full stack. Back-ends com C# e Go, interfaces com TypeScript, "
             "infra com Docker e Kubernetes.")
    return svg_wrap(W, H, "".join(b), label)


# ───────────────────────── stack ─────────────────────────
STACK = [
    ("LANG", "C#", CYAN), ("LANG", "TypeScript", CYAN), ("LANG", "Go", CYAN), ("RUNTIME", "Node.js", VIOLET),
    ("INFRA", "Docker", MAGENTA), ("INFRA", "Kubernetes", MAGENTA), ("DATA", "Redis", YELLOW), ("SECOPS", "Kali Linux", YELLOW),
]


def stack():
    W, H = 900, 250
    uid = "s"
    tl = Timeline(11.0, loop=False)
    t0 = 4.8                     # começa quando o cabeçalho termina o reveal
    b = [panel(W, H, "~/stack — módulos carregados", uid)]
    clip, t = typed_clip(tl, "s-c1", 28, 72, 16, 2 + len("ls ./stack --modulos"), t0)
    b.append(f'<defs>{clip}</defs><g font-family="{MONO}">'
             f'<text x="28" y="72" font-size="16" clip-path="url(#s-c1)"><tspan fill="{MAGENTA}">$</tspan>'
             f'<tspan fill="{TEXT}"> ls ./stack --modulos</tspan></text>')
    cw, ch, gx, gy = 200, 66, 16, 16
    x0, y0 = 28, 92
    for i, (cat, name, col) in enumerate(STACK):
        x = x0 + (i % 4) * (cw + gx)
        y = y0 + (i // 4) * (ch + gy)
        ti = t + 0.25 + i * 0.22
        bar = tl.linear("width", [(ti, 0), (ti + 0.5, cw - 28)])
        flash = tl.discrete("opacity", [(ti, 0.55), (ti + 0.12, 0.08)], 0)
        b.append(f'<g opacity="0">{tl.show([(ti, tl.T + 1)])}'
                 f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="{col}" opacity="0">{flash}</rect>'
                 f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="none" stroke="{col}" stroke-width="1.5"/>'
                 f'<path d="M{x+cw-18} {y}h18v18" fill="none" stroke="{col}" stroke-width="3"/>'
                 f'<text x="{x+14}" y="{y+20}" font-size="10" fill="{col}" letter-spacing="2">{cat}</text>'
                 f'<text x="{x+14}" y="{y+42}" font-size="18" font-weight="700" fill="{TEXT}">{escape(name)}</text>'
                 f'<rect x="{x+14}" y="{y+52}" width="{cw-28}" height="4" fill="{PANEL_EDGE}"/>'
                 f'<rect x="{x+14}" y="{y+52}" width="0" height="4" fill="{col}">{bar}</rect></g>')
    b.append("</g>")
    b.append(scan_overlay(W, H, uid))
    label = "Stack: C#, TypeScript, Go, Node.js, Docker, Kubernetes, Redis e Kali Linux."
    return svg_wrap(W, H, "".join(b), label)


# ───────────────────── cards de repositório ─────────────────────
def repo_card(uid, slug, title, tag, desc, accent):
    W, H = 440, 250
    tl = Timeline(9.0, loop=True)
    CX = W - SPRITE_W - 16
    CY = H - SPRITE_H - 14
    t_w0, t_w1 = 0.2, 1.1
    t_aim = 1.25
    t_s0, t_s1 = 1.4, 3.0
    t_out = 8.3
    LX, LW = 22, CX - 34              # área de conteúdo
    b = [panel(W, H, f"repo://{slug}", uid)]
    b.append(f"<defs>{sprite_defs(uid + 'c')}"
             f'<linearGradient id="{uid}-t" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/>'
             f'<stop offset="1" stop-color="{accent}"/></linearGradient></defs>')

    # estado "criptografado" antes do reveal
    noise = "".join(f'<text x="{LX}" y="{78 + i*24}" font-size="13" fill="{PANEL_EDGE}">'
                    f'{escape(("▒░▓█░▒" * 8)[i:i + 26])}</text>' for i in range(6))
    b.append(f'<g font-family="{MONO}">{noise}'
             f'{tl.show([(0, t_s0), (t_out + 0.4, tl.T + 1)], attr="opacity")}</g>'.replace(
                 f'<g font-family="{MONO}">', f'<g font-family="{MONO}" opacity="1">', 1))

    # conteúdo revelado da esquerda para a direita
    reveal = tl.steps("width", 0, LW + 12, t_s0, t_s1, 24, hide_after=t_out + 0.4)
    flick = tl.discrete("opacity", [(t_out, 0.2), (t_out + 0.1, 1), (t_out + 0.2, 0.1), (t_out + 0.3, 0.8), (t_out + 0.4, 1)], 1)
    content = [f'<text x="{LX}" y="84" font-size="34" font-weight="800" fill="url(#{uid}-t)">{escape(title)}</text>',
               f'<rect x="{LX}" y="96" width="{len(tag)*7.6+18}" height="22" rx="11" fill="none" stroke="{accent}"/>',
               f'<text x="{LX+9}" y="111" font-size="12" fill="{accent}">{escape(tag)}</text>']
    for i, line in enumerate(desc):
        content.append(f'<text x="{LX}" y="{146 + i*20}" font-size="14" fill="{TEXT}">{escape(line)}</text>')
    content.append(f'<text x="{LX}" y="{H-24}" font-size="12" fill="{DIM}">'
                   f'<tspan fill="{MAGENTA}">$</tspan> git clone …/{escape(slug)}</text>')
    b.append(f'<clipPath id="{uid}-rv"><rect x="{LX-6}" y="44" width="0" height="{H-50}">{reveal}</rect></clipPath>'
             f'<g font-family="{MONO}" clip-path="url(#{uid}-rv)">{flick}{"".join(content)}</g>')

    # scan vertical + feixe
    sx = tl.linear("x1", [(t_s0, LX - 6), (t_s1, LX + LW + 6)])
    sx2 = tl.linear("x2", [(t_s0, LX - 6), (t_s1, LX + LW + 6)])
    ex, ey = CX + EMITTER[0], CY + EMITTER[1]
    b.append(f'<g opacity="0">{tl.show([(t_s0, t_s1)])}'
             f'<line x1="{LX}" x2="{LX}" y1="46" y2="{H-10}" stroke="{accent}" stroke-width="3">{sx}{sx2}</line>'
             f'<line x1="{LX}" x2="{LX}" y1="46" y2="{H-10}" stroke="{accent}" stroke-width="12" opacity="0.18">{sx}{sx2}</line>'
             f'<line x1="{ex}" y1="{ey}" x2="{LX}" y2="{ey}" stroke="{CYAN}" stroke-width="2">'
             f'{tl.linear("x2", [(t_s0, LX - 6), (t_s1, LX + LW + 6)])}</line></g>')

    # ciborgue: entra pela direita, mira, escaneia, espera, se teletransporta
    move = tl.linear(None, [(0, f"{W+10} {CY}"), (t_w0, f"{W+10} {CY}"), (t_w1, f"{CX} {CY}")], transform="translate")
    tele = tl.discrete("opacity", [(t_out, 0.3), (t_out + 0.08, 1), (t_out + 0.16, 0.2), (t_out + 0.26, 0.9), (t_out + 0.34, 0)], 1)
    b.append(f'<g transform="translate({W+10} {CY})">{move}{tele}'
             f'{walk_frames(tl, uid + "c", t_w0, t_w1)}'
             f'<use href="#{uid}c-stand">{tl.show([(t_w1, t_aim), (t_s1, tl.T + 1)])}</use>'
             f'<use href="#{uid}c-aim">{tl.show([(t_aim, t_s1)])}</use>'
             f'<rect x="{3*PX}" y="{5*PX}" width="{4*PX}" height="{2*PX}" fill="{MAGENTA}" opacity="0">'
             f'{tl.discrete("opacity", [(t_s1 + 0.6 + i * 0.8, 0.55 if i % 2 == 0 else 0.05) for i in range(10)], 0)}</rect>'
             f'</g>')
    b.append(scan_overlay(W, H, uid))
    return svg_wrap(W, H, "".join(b), f"{title} — {' '.join(desc)}")


if __name__ == "__main__":
    files = {
        "assets/header.svg": header(),
        "assets/stack.svg": stack(),
        "assets/repo-mirav.svg": repo_card(
            "rm", "MiraV", "MiraV", "site · projeto acadêmico",
            ["Site de um projeto acadêmico", "feito para prospectar", "potenciais clientes."], CYAN),
        "assets/repo-doce-e-afeto.svg": repo_card(
            "rd", "doce-e-afeto", "Doce & Afeto", "SPA · confeitaria",
            ["SPA que amplia a prospecção", "e a divulgação da", "confeitaria Doce & Afeto."], MAGENTA),
    }
    for path, svg in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{path}: {len(svg.encode())/1024:.1f} KB")
