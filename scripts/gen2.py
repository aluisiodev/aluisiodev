"""Gera os SVGs holográficos do README (v2).

Painéis de vidro com cantos chanfrados, barras neon e circuitos; o mini ciborgue
chega voando com propulsores e materializa cada bloco projetando pelo olho biônico.
Tudo em SVG + SMIL autocontido, para funcionar dentro do <img> do GitHub.

Uso: python3 gen2.py   (precisa de assets/avatar-gb.png, cyborg.py e gen.py)
"""
import base64
import io
import random
from xml.sax.saxutils import escape

from PIL import Image

import cyborg as cy
from gen import Timeline, typed_clip

THEMES = {
    # tema escuro (original)
    "dark": dict(CYAN="#00f0ff", MAGENTA="#ff2ec4", VIOLET="#9d5cff", YELLOW="#f5e663", RED="#ff3a3a",
                 TEXT="#e8fdff", DIM="#7fa9c4", BG="#05030c", NAME2="#b9f6ff", GLASS2="#3a7bff",
                 GLOW=3, GLASS_A=0.16, PANEL_A=0.85),
    # tema claro: vidro azulado sobre papel frio, neons aprofundados para manter contraste
    "light": dict(CYAN="#0086a8", MAGENTA="#d21b8f", VIOLET="#6a3fd6", YELLOW="#a77a00", RED="#e0262b",
                  TEXT="#121733", DIM="#56607e", BG="#f3f6ff", NAME2="#6a3fd6", GLASS2="#5b8cff",
                  GLOW=1.2, GLASS_A=0.10, PANEL_A=0.92),
}


def apply_theme(name):
    globals().update(THEMES[name])


apply_theme("dark")
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

SW = cy.W * cy.PX
SH = len(cy.FRAMES["hover1"]) * cy.PX
EX, EY = cy.EYE
RX, RY, RW, RH = cy.RED_LIGHT

LINKEDIN_URL = "https://linkedin.com/in/aluisio-alves"


# ───────────────────────── blocos visuais ─────────────────────────
def chamfer(x, y, w, h, c=16):
    return f"M{x+c} {y} H{x+w} V{y+h-c} L{x+w-c} {y+h} H{x} V{y+c} Z"


def common_defs(uid, sprite=True):
    return f'''
<filter id="{uid}-glow" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="{GLOW}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<linearGradient id="{uid}-glass" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="{GLASS_A}"/><stop offset="0.6" stop-color="{GLASS2}" stop-opacity="0.06"/>
  <stop offset="1" stop-color="{VIOLET}" stop-opacity="0.12"/>
</linearGradient>
<pattern id="{uid}-lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{CYAN}" opacity="0.07"/></pattern>
<linearGradient id="{uid}-cone" x1="1" x2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.5"/>
  <stop offset="1" stop-color="{CYAN}" stop-opacity="0.03"/></linearGradient>
<radialGradient id="{uid}-red"><stop offset="0" stop-color="{RED}" stop-opacity="0.95"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<linearGradient id="{uid}-name" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{NAME2}"/></linearGradient>
{"".join(cy.svg_group(f"{uid}-{k}", v) for k, v in cy.FRAMES.items()) if sprite else ""}
'''


def circuits(w, h, uid, seed, n=7):
    """Trilhas de circuito ao fundo, com pulsos de luz percorrendo algumas delas."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        side = rnd.choice(["l", "r"])
        y = rnd.randint(50, h - 30)
        x0 = 6 if side == "l" else w - 6
        dx = 1 if side == "l" else -1
        a = rnd.randint(24, 70)
        b = rnd.randint(14, 34) * rnd.choice([-1, 1])
        c = rnd.randint(18, 50)
        pts = [(x0, y), (x0 + dx * a, y), (x0 + dx * (a + abs(b)), y + b), (x0 + dx * (a + abs(b) + c), y + b)]
        d = "M" + " L".join(f"{px} {py}" for px, py in pts)
        col = rnd.choice([CYAN, VIOLET, CYAN])
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1" opacity="0.28"/>'
                   f'<circle cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="2.5" fill="none" stroke="{col}" opacity="0.5"/>')
        if i % 2 == 0:
            ln = a + abs(b) * 1.42 + c
            dur = rnd.uniform(2.2, 4.0)
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="10 {ln:.0f}" '
                       f'opacity="0.9"><animate attributeName="stroke-dashoffset" values="{ln+10:.0f};0" '
                       f'dur="{dur:.1f}s" repeatCount="indefinite"/></path>')
    return f'<g>{"".join(out)}</g>'


def outer_frame(w, h, uid):
    """Moldura externa do 'dispositivo' (como na referência): chanfros, barras neon."""
    bar_w = min(260, w * 0.4)
    return f'''
<path d="{chamfer(2, 2, w-4, h-4, 22)}" fill="{BG}"/>
<path d="{chamfer(2, 2, w-4, h-4, 22)}" fill="url(#{uid}-lines)"/>
{circuits(w, h, uid, sum(map(ord, uid)) * 7)}
<path d="{chamfer(2, 2, w-4, h-4, 22)}" fill="none" stroke="{CYAN}" stroke-width="1.5" opacity="0.55"/>
<path d="{chamfer(8, 8, w-16, h-16, 18)}" fill="none" stroke="{VIOLET}" stroke-width="1" opacity="0.35"/>
<g filter="url(#{uid}-glow)">
  <rect x="{(w-bar_w)/2}" y="4" width="{bar_w}" height="4" rx="2" fill="{MAGENTA}"/>
  <rect x="{(w-bar_w*0.6)/2}" y="{h-8}" width="{bar_w*0.6}" height="4" rx="2" fill="{MAGENTA}"/>
  <rect x="3" y="{h*0.3}" width="3" height="{h*0.2}" fill="{MAGENTA}" opacity="0.85"/>
  <rect x="{w-6}" y="{h*0.55}" width="3" height="{h*0.2}" fill="{MAGENTA}" opacity="0.85"/>
</g>'''


def holo_panel(x, y, w, h, uid, label, accent=None, readout=""):
    """Painel de vidro chanfrado com rótulo e leitura piscante."""
    accent = accent or CYAN
    rd = ""
    if readout:
        rd = (f'<text x="{x+w-14}" y="{y+20}" font-size="10" fill="{accent}" text-anchor="end" letter-spacing="1">'
              f'{escape(readout)}<animate attributeName="opacity" values="1;0.3;1;1" dur="2.4s" repeatCount="indefinite"/></text>')
    return f'''
<path d="{chamfer(x, y, w, h)}" fill="{BG}" opacity="{PANEL_A}"/>
<path d="{chamfer(x, y, w, h)}" fill="url(#{uid}-glass)"/>
<path d="{chamfer(x, y, w, h)}" fill="none" stroke="{accent}" stroke-width="1.3" opacity="0.9"/>
<rect x="{x+w*0.3}" y="{y-2}" width="{w*0.4}" height="3" fill="{accent}" filter="url(#{uid}-glow)"/>
<path d="M{x} {y+h-30} V{y+h} H{x+30} M{x+w-30} {y} H{x+w} V{y+30}" fill="none" stroke="{accent}" stroke-width="3"/>
<text x="{x+22}" y="{y+20}" font-size="10" fill="{accent}" letter-spacing="3">{escape(label)}</text>
<line x1="{x+14}" y1="{y+28}" x2="{x+w-14}" y2="{y+28}" stroke="{accent}" stroke-width="0.6" opacity="0.4"/>
{rd}'''


def img_b64(path, scale):
    im = Image.open(path)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def red_light(uid):
    return (f'<circle cx="{RX + RW/2}" cy="{RY + RH/2}" r="8" fill="url(#{uid}-red)">'
            f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.6;1" calcMode="discrete" dur="1.2s" repeatCount="indefinite"/></circle>'
            f'<rect x="{RX}" y="{RY}" width="{RW}" height="{RH}" fill="{cy.PAL["r"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;0.6;1" calcMode="discrete" dur="1.2s" repeatCount="indefinite"/></rect>')


def hover_flicker(uid):
    """Chamas alternando para sempre (usado dentro de um grupo que controla quando aparece)."""
    return (f'<use href="#{uid}-hover1"><animate attributeName="opacity" values="1;0" calcMode="discrete" dur="0.24s" repeatCount="indefinite"/></use>'
            f'<use href="#{uid}-hover2" opacity="0"><animate attributeName="opacity" values="0;1" calcMode="discrete" dur="0.24s" repeatCount="indefinite"/></use>')


def cone(uid, tx, ty0, ty1):
    """Cone de projeção do olho até a borda (tx, ty0..ty1), em coordenadas do sprite."""
    return (f'<polygon points="{EX},{EY} {tx},{ty0} {tx},{ty1}" fill="url(#{uid}-cone)"/>'
            f'<line x1="{EX}" y1="{EY}" x2="{tx}" y2="{ty0}" stroke="{CYAN}" stroke-width="0.8" opacity="0.6"/>'
            f'<line x1="{EX}" y1="{EY}" x2="{tx}" y2="{ty1}" stroke="{CYAN}" stroke-width="0.8" opacity="0.6"/>'
            f'<circle cx="{EX}" cy="{EY}" r="4" fill="{TEXT}"/>')


def svg_wrap(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>\n{body}\n</svg>\n')


# ───────────────────────── cabeçalho ─────────────────────────
def header():
    W, H, uid = 900, 390, "h"
    tl = Timeline(12.0, loop=False)
    AX, AY, AS = 40, 82, 240
    CX, CY = 296, 128
    t_fly0, t_arrive = 0.3, 1.5
    t_p0, t_p1 = 1.9, 4.1
    t_panel = 4.3

    b = [f"<defs>{common_defs(uid)}</defs>", outer_frame(W, H, uid)]
    b.append(f'<g font-family="{MONO}">')

    # moldura do avatar
    b.append(holo_panel(AX - 10, AY - 34, AS + 20, AS + 44, uid, "SUJEITO // ID-0x2A"))
    b.append(f'<text x="{AX+AS/2}" y="{AY+AS/2}" font-size="12" fill="{DIM}" text-anchor="middle">[ AGUARDANDO PROJEÇÃO ]'
             f'{tl.discrete("opacity", [(0.5, 0), (0.9, 1), (1.3, 0), (1.7, 1), (t_p0, 0)], 1)}</text>')

    img = img_b64("assets/avatar-gb.png", 6)
    rows = 40
    reveal = tl.steps("height", 0, AS, t_p0, t_p1, rows)
    b.append(f'<clipPath id="h-rev"><rect x="{AX}" y="{AY}" width="{AS}" height="0">{reveal}</rect></clipPath>')
    b.append(f'<image href="data:image/png;base64,{img}" x="{AX}" y="{AY}" width="{AS}" height="{AS}" '
             f'clip-path="url(#h-rev)" style="image-rendering:pixelated"/>')
    # linha da projeção percorrendo a imagem
    yv = tl.linear("y", [(t_p0, AY), (t_p1, AY + AS)])
    b.append(f'<rect x="{AX}" y="{AY}" width="{AS}" height="3" fill="{CYAN}" filter="url(#{uid}-glow)" opacity="0">'
             f'{yv}{tl.show([(t_p0, t_p1)])}</rect>')
    # glitch ocasional (para sempre, depois do reveal)
    for i, (sy, sh, dx, col) in enumerate([(AY + 60, 18, 10, CYAN), (AY + 150, 12, -8, MAGENTA)]):
        b.append(f'<clipPath id="h-gl{i}"><rect x="{AX}" y="{sy}" width="{AS}" height="{sh}"/></clipPath>'
                 f'<g clip-path="url(#h-gl{i})" opacity="0">'
                 f'<image href="data:image/png;base64,{img}" x="{AX+dx}" y="{AY}" width="{AS}" height="{AS}" style="image-rendering:pixelated"/>'
                 f'<rect x="{AX}" y="{sy}" width="{AS}" height="{sh}" fill="{col}" opacity="0.25"/>'
                 f'<animate attributeName="opacity" values="0;1;0;1;0" keyTimes="0;0.9;0.93;0.96;1" calcMode="discrete" '
                 f'begin="{t_p1 + 0.3}s" dur="{4.5 + i}s" repeatCount="indefinite"/></g>')
    b.append(f'<g opacity="0">{tl.show([(t_p1 + 0.2, tl.T + 1)])}'
             f'<text x="{AX}" y="{AY+AS+28}" font-size="11" fill="{CYAN}">ID ▸ aluisiodev</text>'
             f'<text x="{AX+AS}" y="{AY+AS+28}" font-size="11" fill="{CYAN}" text-anchor="end">● ONLINE'
             f'<animate attributeName="opacity" values="1;0.35;1" dur="1.6s" repeatCount="indefinite"/></text></g>')

    # painel de texto (inicializa sozinho depois do avatar)
    PX0, PY0, PW, PH = 400, 48, 466, 300
    boot = tl.steps("height", 0, PH + 10, t_panel, t_panel + 0.5, 10)
    b.append(f'<clipPath id="h-pb"><rect x="{PX0-4}" y="{PY0-6}" width="{PW+8}" height="0">{boot}</rect></clipPath>'
             f'<g clip-path="url(#h-pb)">{holo_panel(PX0, PY0, PW, PH, uid, "IDENTIDADE // SYSTEM", readout="SYNC ▮▮▮▮▯ 98%")}</g>')

    TX = PX0 + 24
    clips, lines = [], []

    def cmd(y, text, t0, cid):
        clip, t1 = typed_clip(tl, cid, TX, y, 16, 2 + len(text), t0)
        clips.append(clip)
        lines.append(f'<text x="{TX}" y="{y}" font-size="16" clip-path="url(#{cid})" filter="url(#{uid}-glow)">'
                     f'<tspan fill="{CYAN}">&gt;</tspan><tspan fill="{TEXT}"> {escape(text)}</tspan></text>')
        return t1

    t = cmd(PY0 + 62, "whoami", t_panel + 0.6, "h-c1")
    tn = t + 0.3
    lines.append(f'<g opacity="0">{tl.show([(tn, tl.T + 1)])}'
                 f'<text x="{TX}" y="{PY0+122}" font-size="50" font-weight="800" fill="{MAGENTA}" opacity="0.65">ALUÍSIO'
                 f'{tl.linear("x", [(tn, TX - 10), (tn + 0.25, TX - 3)])}</text>'
                 f'<text x="{TX}" y="{PY0+122}" font-size="50" font-weight="800" fill="{CYAN}" opacity="0.65">ALUÍSIO'
                 f'{tl.linear("x", [(tn, TX + 10), (tn + 0.25, TX + 3)])}</text>'
                 f'<text x="{TX}" y="{PY0+122}" font-size="50" font-weight="800" fill="url(#{uid}-name)" filter="url(#{uid}-glow)">ALUÍSIO</text></g>')
    sub = "dev full stack // back-end · cloud · segurança"
    clip, t = typed_clip(tl, "h-c2", TX, PY0 + 152, 14, len(sub), tn + 0.35, cps=40)
    clips.append(clip)
    lines.append(f'<text x="{TX}" y="{PY0+152}" font-size="14" fill="{DIM}" clip-path="url(#h-c2)">{escape(sub)}</text>')
    t = cmd(PY0 + 196, "cat missao.txt", t + 0.3, "h-c3")
    bio = ["Construo back-ends rápidos com C# e Go,",
           "interfaces com TypeScript e coloco tudo",
           "de pé com Docker e Kubernetes."]
    for i, line in enumerate(bio):
        lines.append(f'<text x="{TX}" y="{PY0 + 224 + i*22}" font-size="15" fill="{TEXT}" opacity="0">{escape(line)}'
                     f'{tl.show([(t + 0.25 + i * 0.22, tl.T + 1)])}</text>')
    b.append(f'<defs>{"".join(clips)}</defs>{"".join(lines)}')
    b.append("</g>")

    # ciborgue: voa até perto do avatar, projeta, fica flutuando
    move = tl.linear(None, [(t_fly0, f"{W + 40} -160"), (t_arrive - 0.2, f"{CX - 8} {CY + 6}"),
                            (t_arrive, f"{CX} {CY}")], transform="translate")
    bob = (f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" '
           f'begin="{t_arrive}s" dur="1.1s" repeatCount="indefinite"/>')
    b.append(f'<g transform="translate({W + 40} -160)">{move}<g>{bob}'
             f'<g opacity="0">{tl.show([(t_p0, t_p1)])}{cone(uid, AX + AS - CX, AY - CY, AY + AS - CY)}</g>'
             f'<use href="#{uid}-boost">{tl.show([(t_fly0, t_arrive)])}</use>'
             f'<g opacity="0">{tl.show([(t_arrive, t_p0), (t_p1, tl.T + 1)])}{hover_flicker(uid)}</g>'
             f'<use href="#{uid}-project">{tl.show([(t_p0, t_p1)])}</use>'
             f'{red_light(uid)}</g></g>')

    label = ("Aluísio (aluisiodev) — dev full stack. Back-ends com C# e Go, interfaces com TypeScript, "
             "infra com Docker e Kubernetes.")
    return svg_wrap(W, H, "".join(b), label)


# ───────────────────────── stack ─────────────────────────
def stack_items():
    return [
        ("LANG", "C#", CYAN), ("LANG", "TypeScript", CYAN), ("LANG", "Go", CYAN), ("RUNTIME", "Node.js", VIOLET),
        ("INFRA", "Docker", MAGENTA), ("INFRA", "Kubernetes", MAGENTA), ("DATA", "Redis", YELLOW),
        ("SECOPS", "Kali Linux", YELLOW),
    ]


def stack():
    W, H, uid = 900, 290, "s"
    tl = Timeline(11.0, loop=False)
    t0 = 5.0
    b = [f"<defs>{common_defs(uid, sprite=False)}</defs>", outer_frame(W, H, uid), f'<g font-family="{MONO}">']
    b.append(holo_panel(24, 34, W - 48, H - 58, uid, "MÓDULOS // STACK", readout="CARGA ▮▮▮▮▮"))
    clip, t = typed_clip(tl, "s-c1", 46, 92, 16, 2 + len("ls ./stack --modulos"), t0)
    b.append(f'<defs>{clip}</defs><text x="46" y="92" font-size="16" clip-path="url(#s-c1)" filter="url(#{uid}-glow)">'
             f'<tspan fill="{CYAN}">&gt;</tspan><tspan fill="{TEXT}"> ls ./stack --modulos</tspan></text>')
    cw, ch, gx, gy = 192, 64, 14, 16
    x0, y0 = 46, 112
    # trilha de energia ligando os módulos
    for r in range(2):
        yy = y0 + r * (ch + gy) + ch / 2
        b.append(f'<line x1="{x0-12}" y1="{yy}" x2="{x0 + 4*(cw+gx)}" y2="{yy}" stroke="{CYAN}" stroke-width="1" opacity="0.18"/>')
    for i, (cat, name, col) in enumerate(stack_items()):
        x = x0 + (i % 4) * (cw + gx)
        y = y0 + (i // 4) * (ch + gy)
        ti = t + 0.3 + i * 0.25
        bar = tl.linear("width", [(ti, 0), (ti + 0.5, cw - 28)])
        flash = tl.discrete("opacity", [(ti, 0.5), (ti + 0.1, 0.1), (ti + 0.18, 0.4), (ti + 0.26, 0.06)], 0)
        b.append(f'<g opacity="0">{tl.show([(ti, tl.T + 1)])}'
                 f'<path d="{chamfer(x, y, cw, ch, 12)}" fill="{col}" opacity="0">{flash}</path>'
                 f'<path d="{chamfer(x, y, cw, ch, 12)}" fill="url(#{uid}-glass)"/>'
                 f'<path d="{chamfer(x, y, cw, ch, 12)}" fill="none" stroke="{col}" stroke-width="1.3"/>'
                 f'<rect x="{x+cw*0.25}" y="{y-1.5}" width="{cw*0.5}" height="3" fill="{col}" filter="url(#{uid}-glow)"/>'
                 f'<text x="{x+16}" y="{y+20}" font-size="10" fill="{col}" letter-spacing="2">{cat}</text>'
                 f'<text x="{x+16}" y="{y+42}" font-size="18" font-weight="700" fill="{TEXT}">{escape(name)}</text>'
                 f'<rect x="{x+16}" y="{y+51}" width="{cw-28}" height="3" fill="{col}" opacity="0.18"/>'
                 f'<rect x="{x+16}" y="{y+51}" width="0" height="3" fill="{col}">{bar}</rect></g>')
    b.append("</g>")
    return svg_wrap(W, H, "".join(b), "Stack: C#, TypeScript, Go, Node.js, Docker, Kubernetes, Redis e Kali Linux.")


# ───────────────── cards projetados (repos e conectar) ─────────────────
def projected_card(uid, W, H, label, readout, content_fn, title_for_a11y, accent=None):
    """Card em loop: ciborgue chega voando, projeta o painel, espera, o painel some e ele parte."""
    accent = accent or CYAN
    tl = Timeline(9.0, loop=True)
    CX = W - SW - 14
    CY = (H - SH) // 2 + 6
    t_arrive, t_p0, t_p1, t_out, t_leave = 1.0, 1.25, 2.85, 7.6, 8.2
    PX0, PY0, PW, PH = 22, 30, CX - 40, H - 52

    hov = [(t_arrive, t_p0), (t_p1, t_leave)]
    move = tl.linear(None, [(0, f"{W + 30} -150"), (t_arrive - 0.15, f"{CX - 6} {CY + 6}"), (t_arrive, f"{CX} {CY}"),
                            (t_leave, f"{CX} {CY}"), (8.95, f"{W + 30} -150")], transform="translate")
    reveal = tl.steps("height", 0, PH + 12, t_p0 + 0.05, t_p1, 20, hide_after=t_out + 0.5)
    flick = tl.discrete("opacity", [(t_out, 0.25), (t_out + 0.1, 0.9), (t_out + 0.2, 0.1), (t_out + 0.32, 0.7),
                                    (t_out + 0.42, 0.2)], 1)
    yv = tl.linear("y", [(t_p0, PY0), (t_p1, PY0 + PH)])

    b = [f"<defs>{common_defs(uid)}</defs>", outer_frame(W, H, uid), f'<g font-family="{MONO}">']
    b.append(f'<text x="{PX0 + PW/2}" y="{PY0 + PH/2}" font-size="12" fill="{DIM}" text-anchor="middle" opacity="0.7">'
             f'[ SINAL CRIPTOGRAFADO ]{tl.show([(0, t_p0), (t_out + 0.5, tl.T + 1)])}</text>')
    b.append(f'<clipPath id="{uid}-rv"><rect x="{PX0-4}" y="{PY0-6}" width="{PW+8}" height="0">{reveal}</rect></clipPath>'
             f'<g clip-path="url(#{uid}-rv)">{flick}{holo_panel(PX0, PY0, PW, PH, uid, label, accent, readout)}'
             f'{content_fn(PX0, PY0, PW, PH)}</g>')
    b.append(f'<rect x="{PX0}" y="{PY0}" width="{PW}" height="3" fill="{CYAN}" filter="url(#{uid}-glow)" opacity="0">'
             f'{yv}{tl.show([(t_p0, t_p1)])}</rect>')
    b.append("</g>")
    b.append(f'<g transform="translate({W + 30} -150)">{move}<g>'
             f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="1.1s" repeatCount="indefinite"/>'
             f'<g opacity="0">{tl.show([(t_p0, t_p1)])}{cone(uid, PX0 + PW - CX, PY0 - CY, PY0 + PH - CY)}</g>'
             f'<use href="#{uid}-boost">{tl.show([(0, t_arrive), (t_leave, tl.T + 1)])}</use>'
             f'<g opacity="0">{tl.show(hov)}{hover_flicker(uid)}</g>'
             f'<use href="#{uid}-project">{tl.show([(t_p0, t_p1)])}</use>'
             f'{red_light(uid)}</g></g>')
    return svg_wrap(W, H, "".join(b), title_for_a11y)


def repo_card(uid, slug, title, tag, desc, accent):
    def content(x, y, w, h):
        out = [f'<text x="{x+22}" y="{y+74}" font-size="30" font-weight="800" fill="{accent}" filter="url(#{uid}-glow)">{escape(title)}</text>',
               f'<path d="{chamfer(x+22, y+86, len(tag)*7.4+22, 22, 6)}" fill="none" stroke="{accent}"/>',
               f'<text x="{x+33}" y="{y+101}" font-size="12" fill="{accent}">{escape(tag)}</text>']
        for i, line in enumerate(desc):
            out.append(f'<text x="{x+22}" y="{y+134 + i*20}" font-size="14" fill="{TEXT}">{escape(line)}</text>')
        out.append(f'<text x="{x+22}" y="{y+h-16}" font-size="11" fill="{DIM}"><tspan fill="{CYAN}">&gt;</tspan>'
                   f' abrir repo://{escape(slug)}</text>')
        return "".join(out)
    return projected_card(uid, 460, 280, "PROJETO // REPO", "▮▮▮▯", content,
                          f"{title} — {' '.join(desc)}", accent)


def connect_card():
    uid = "c"
    small = img_b64("assets/avatar-gb.png", 3)

    def net_icon(cx, cy):
        # ícone próprio de "rede": três nós ligados
        pts = [(cx - 14, cy + 10), (cx + 14, cy + 10), (cx, cy - 14)]
        lines = "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{CYAN}" stroke-width="2"/>'
                        for a, b in [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])])
        nodes = "".join(f'<circle cx="{p[0]}" cy="{p[1]}" r="5" fill="{BG}" stroke="{CYAN}" stroke-width="2"/>' for p in pts)
        return (f'<path d="{chamfer(cx-26, cy-26, 52, 52, 10)}" fill="url(#{uid}-glass)" stroke="{CYAN}" stroke-width="1.3"/>'
                f'<g filter="url(#{uid}-glow)">{lines}{nodes}</g>')

    def content(x, y, w, h):
        ax, ay = x + 24, y + 46
        out = [f'<path d="{chamfer(ax-4, ay-4, 128, 128, 10)}" fill="none" stroke="{CYAN}" stroke-width="1.3"/>',
               f'<image href="data:image/png;base64,{small}" x="{ax}" y="{ay}" width="120" height="120" style="image-rendering:pixelated"/>',
               f'<text x="{ax+150}" y="{y+74}" font-size="26" font-weight="800" fill="url(#{uid}-name)" filter="url(#{uid}-glow)">Aluísio Alves</text>',
               f'<text x="{ax+150}" y="{y+98}" font-size="13" fill="{TEXT}">Dev full stack · C# · Go · TypeScript · Docker</text>',
               f'<text x="{ax+150}" y="{y+120}" font-size="12" fill="{DIM}">linkedin.com/in/aluisio-alves</text>',
               net_icon(x + w - 52, y + 74)]
        bx, by, bw, bh = ax + 150, y + 136, 220, 40
        out.append(f'<path d="{chamfer(bx, by, bw, bh, 10)}" fill="{CYAN}" opacity="0.14">'
                   f'<animate attributeName="opacity" values="0.1;0.32;0.1" dur="1.6s" repeatCount="indefinite"/></path>'
                   f'<path d="{chamfer(bx, by, bw, bh, 10)}" fill="none" stroke="{CYAN}" stroke-width="1.6" filter="url(#{uid}-glow)"/>'
                   f'<text x="{bx+bw/2}" y="{by+26}" font-size="15" font-weight="700" fill="{TEXT}" text-anchor="middle" '
                   f'letter-spacing="3">CONECTAR ▸</text>')
        out.append(f'<text x="{bx+bw+16}" y="{by+26}" font-size="11" fill="{DIM}">clique para abrir o perfil</text>')
        return "".join(out)

    return projected_card(uid, 900, 250, "PERFIL // LINKEDIN", "CANAL SEGURO ●", content,
                          "Aluísio Alves no LinkedIn — clique para abrir o perfil.")


def cmd_button(uid, cmd, hint, c1, c2):
    """Botão de comando para o <summary>: preenchido em neon, brilho varrendo, 'EXECUTAR' piscando."""
    W, H = 560, 72
    sh = chamfer(6, 8, W - 12, H - 16, 14)
    return svg_wrap(W, H, f'''
<defs>
  <linearGradient id="{uid}-fill" x1="0" x2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
  <linearGradient id="{uid}-shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="{uid}-glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>
  <clipPath id="{uid}-clip"><path d="{sh}"/></clipPath>
</defs>
<path d="{sh}" fill="url(#{uid}-fill)" filter="url(#{uid}-glow)" opacity="0.55">
  <animate attributeName="opacity" values="0.35;0.8;0.35" dur="2s" repeatCount="indefinite"/></path>
<path d="{sh}" fill="url(#{uid}-fill)"/>
<g clip-path="url(#{uid}-clip)">
  <rect x="-160" y="0" width="120" height="{H}" fill="url(#{uid}-shine)" transform="skewX(-20)">
    <animate attributeName="x" values="-160;{W+80};{W+80}" keyTimes="0;0.45;1" dur="3.2s" repeatCount="indefinite"/></rect>
</g>
<path d="{chamfer(14, 16, 40, 40, 8)}" fill="{BG}"/>
<path d="M29 26 L43 36 L29 46 Z" fill="{c1}">
  <animate attributeName="opacity" values="1;0.35;1" dur="1.2s" repeatCount="indefinite"/></path>
<g font-family="{MONO}">
  <text x="68" y="36" font-size="11" font-weight="700" fill="{BG}" letter-spacing="2" opacity="0.75">{escape(hint)}</text>
  <text x="68" y="55" font-size="19" font-weight="800" fill="{BG}">{escape(cmd)}</text>
  <path d="{chamfer(W-150, 20, 132, 32, 8)}" fill="{BG}"/>
  <text x="{W-84}" y="41" font-size="12" font-weight="700" fill="{c1}" text-anchor="middle" letter-spacing="3">EXECUTAR
    <animate attributeName="opacity" values="1;1;0.25;1" keyTimes="0;0.6;0.8;1" dur="1.4s" repeatCount="indefinite"/></text>
</g>
<path d="M6 {H-24} V{H-8} H22 M{W-22} 8 H{W-6} V24" fill="none" stroke="{TEXT}" stroke-width="2" opacity="0.8"/>
''', f"{cmd} — clique para executar")


def build_all():
    return {
        "btn-repos": cmd_button("br", "./revelar --repos", "PROJETOS EM DESTAQUE", CYAN, VIOLET),
        "btn-conectar": cmd_button("bc", "./conectar", "ABRIR CANAL · LINKEDIN", VIOLET, MAGENTA),
        "btn-tudo": cmd_button("bt", "./revelar --tudo", "VERSÃO COMPLETA EM TEXTO", YELLOW, CYAN),
        "header": header(),
        "stack": stack(),
        "repo-mirav": repo_card(
            "rm", "MiraV", "MiraV", "site · projeto acadêmico",
            ["Site de um projeto acadêmico", "feito para prospectar", "potenciais clientes."], CYAN),
        "repo-doce-e-afeto": repo_card(
            "rd", "doce-e-afeto", "Doce & Afeto", "SPA · confeitaria",
            ["SPA que amplia a prospecção", "e a divulgação da", "confeitaria Doce & Afeto."], MAGENTA),
        "conectar": connect_card(),
    }


if __name__ == "__main__":
    for theme, suffix in (("dark", ""), ("light", "-light")):
        apply_theme(theme)
        for name, svg in build_all().items():
            path = f"assets/{name}{suffix}.svg"
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"{path}: {len(svg.encode())/1024:.1f} KB")
