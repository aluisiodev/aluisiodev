"""
gerar_ascii.py — transforma uma foto em arte ASCII para o README

Uso:
    pip install pillow numpy
    python gerar_ascii.py foto.jpg

Ele gera DUAS versoes (o modo escuro precisa da arte invertida em relacao
ao modo claro) e ja imprime o bloco pronto para colar no gerar_svg.py.

Tambem tenta recortar o fundo automaticamente, assumindo que o fundo e
mais CLARO que a pessoa. Se o seu fundo for escuro, use --fundo-escuro.

Opcoes:
    --cols N        colunas   (padrao 58, o maximo do layout)
    --rows N        linhas    (padrao 35, o maximo do layout)
    --gamma N       contraste (padrao 1.45; maior = mais espaco vazio)
    --limiar N      corte do fundo, 0-255 (padrao 140)
    --crop x1,y1,x2,y2   recorta a foto antes de converter (em pixels).
                         Enquadre no rosto/tronco: sobra de fundo vira ruido.
    --fundo-escuro  inverte a logica de recorte do fundo
    --sem-recorte   nao remove o fundo

Dicas: foto com o rosto bem iluminado e fundo liso funciona muito melhor.
Se sair um borrao, mexa primeiro no --limiar, depois no --gamma.
"""

import sys
from collections import deque

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("Faltam dependencias. Rode:  pip install pillow numpy")

# esparso -> denso. Os espacos no inicio deixam a arte "arejada",
# que e o que faz o desenho ser legivel de longe.
PALETA = "  ..::;;=+*#%@@"


def recortar_fundo(a, limiar, fundo_escuro):
    """Flood fill a partir das bordas para separar a pessoa do fundo."""
    H, W = a.shape
    fundo = np.zeros((H, W), bool)
    fila = deque()

    def eh_fundo(y, x):
        return a[y, x] < limiar if fundo_escuro else a[y, x] > limiar

    for x in range(W):
        for y in (0, H - 1):
            if eh_fundo(y, x):
                fundo[y, x] = True
                fila.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if eh_fundo(y, x):
                fundo[y, x] = True
                fila.append((y, x))
    while fila:
        y, x = fila.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and not fundo[ny, nx] and eh_fundo(ny, nx):
                fundo[ny, nx] = True
                fila.append((ny, nx))
    return ~fundo


def converter(caminho, cols=58, rows=35, gamma=1.45, limiar=140,
              fundo_escuro=False, recorte=True, crop=None):
    src = Image.open(caminho).convert("L")
    if crop:
        src = src.crop(crop)
    a = np.array(src).astype(int)
    pessoa = recortar_fundo(a, limiar, fundo_escuro) if recorte else np.ones(a.shape, bool)

    lum = np.array(Image.fromarray(a.astype("uint8")).resize((cols, rows), Image.LANCZOS)).astype(float)
    cob = np.array(Image.fromarray((pessoa * 255).astype("uint8")).resize((cols, rows), Image.LANCZOS)).astype(float) / 255
    dentro = cob > 0.45
    if not dentro.any():
        sys.exit("O recorte removeu a imagem inteira. Ajuste --limiar ou use --sem-recorte.")

    v = lum[dentro]
    lo, hi = np.percentile(v, 2), np.percentile(v, 98)
    N = np.clip((lum - lo) / max(1e-6, hi - lo), 0, 1)

    def desenhar(brilho_denso):
        saida = []
        for y in range(rows):
            linha = ""
            for x in range(cols):
                if not dentro[y, x]:
                    linha += " "
                    continue
                t = (N[y, x] if brilho_denso else 1 - N[y, x]) ** gamma
                linha += PALETA[min(len(PALETA) - 1, int(t * len(PALETA)))]
            saida.append(linha.rstrip())
        return saida

    # modo escuro: texto claro sobre fundo escuro -> brilho vira densidade
    # modo claro:  texto escuro sobre fundo claro -> sombra vira densidade
    return desenhar(True), desenhar(False)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    def opt(nome, padrao, tipo=int):
        return tipo(args[args.index(nome) + 1]) if nome in args else padrao

    escuro, claro = converter(
        args[0],
        cols=opt("--cols", 58),
        rows=opt("--rows", 35),
        gamma=opt("--gamma", 1.45, float),
        limiar=opt("--limiar", 140),
        fundo_escuro="--fundo-escuro" in args,
        recorte="--sem-recorte" not in args,
        crop=tuple(int(n) for n in args[args.index("--crop") + 1].split(",")) if "--crop" in args else None,
    )

    with open("ascii.txt", "w", encoding="utf-8") as f:
        f.write('ASCII_DARK = r"""\n' + "\n".join(escuro) + '\n"""\n\n')
        f.write('ASCII_LIGHT = r"""\n' + "\n".join(claro) + '\n"""\n')

    print("===== ASCII_DARK (modo escuro) =====")
    print("\n".join(escuro))
    print("\n===== ASCII_LIGHT (modo claro) =====")
    print("\n".join(claro))
    print("\nSalvo em ascii.txt. Substitua os dois blocos dentro do gerar_svg.py")
    print("e rode:  python gerar_svg.py")
