TITULO = "aluisio@github"

# Linhas da coluna da direita. Tipos disponiveis:
#   ("titulo", "texto")              -> cabecalho de secao com tracos
#   ("vazio",)                       -> linha em branco
#   ("campo", "Chave", "valor")      -> o ponto na chave vira separador colorido
#   ("uptime",)                      -> idade, atualizada automaticamente
#   ("stats_repos",) ("stats_commits",) ("stats_loc",)  -> automaticos
#
# Limite: 20 linhas, 72 colunas cada.
LINHAS = [
    ("titulo", TITULO),
    ("campo", "OS", "Windows 11, iOS, Android, Kali Linux"),
    ("uptime",),
    ("campo", "Kernel", "Full-Stack Developer"),
    ("campo", "IDE", "VS Code, Visual Studio, Rider"),
    ("vazio",),
    ("campo", "Languages.Programming", "C#, Python, Java, JavaScript, TypeScript, Go"),
    ("campo", "Languages.Runtime", "Node.js"),
    ("campo", "Languages.Computer", "HTML, CSS, JSON"),
    ("campo", "Languages.Real", "Portuguese, English"),
    ("vazio",),
    ("titulo", "- Contact"),
    ("campo", "LinkedIn", "aluisio-alves"),
    ("campo", "Instagram", "aluisiou"),
    ("campo", "Discord", "aluisio7k"),
    ("vazio",),
    ("titulo", "- GitHub Stats"),
    ("stats_repos",),
    ("stats_commits",),
    ("stats_loc",),
]

# Arte ASCII: 58 colunas x 35 linhas.
# Sao DUAS versoes: no modo escuro o texto e claro (brilho = denso),
# no modo claro o texto e escuro (sombra = denso).
# Para trocar por outra foto:  python gerar_ascii.py foto.jpg
ASCII_DARK = r"""
                                    @@
                    @@#==;=#%#%@@@#@*@@       @
                *=;:::...::;=;;**=;:;==+=%@*;@
              *::;;::..:;:.:::.:;..........:%
            #+=++=;...:::;;:......         ...%
           @#%##*;:::;:..::;:.:::    ...   .  .;%
        @ #%    +;=;;:..:.......:.     ........  .+@
          @    ;;#+;:..:..                       .==;*
        @@ @@%;:#*;....                           .
     %@ @ @@@#+*=+:                                 ;
    @=@ %*@@##*;::.                                  @
    *;%@@@@%#*;......  ..
    *@@@#*#*;:.:;::.....                             #
   #@#*+=:....:;;:..........                         %
  @@;;+;:.. ..::.  .....::::......                   *
   %:;;::.......      ....:;;;::...         ..       +
   @;:;;::...:.......  ...:;==;;:.....:::::...      .
   @====:...=+;=+=;:.....:=*#*=;::......::;;;:.   ..
    @+=;:...*@%*;::.  ..:;*%%#+;::...  ....;=;:   .*
     @=;::.:  @@*+==;;;=+#%@@#+;;;:::::::::;;=;   .;
       =;::+      @@%#%@@@@@@%+;;=;;;;;;======;.  :
       @*+:+        @@@@@@@@@@+;;=======+++++=;:..
         @*@          @%##@@@@*=;;;==+++====++=;:;
                    @@%#*@@@@@*+=;;;++++===+==+;;: .*
                   @@%##*@@@#=;;::;;=++++====++;;.   :
                  @%%%#%%%@*=;;;:::;==++=======.:     :
           @      @@@@@@@@@@@;;=;::;;=========;        #
;::;=#@              @#+%@%*=;=;::::::;=======..       =
:.        *@=+      @*;::::...........:;;;;==: .
:::.      .;*.=    @*======;;:::::::::;;;;;;;
......    :;  .   @#*****+;::::..:::;;;;;;;;           .*
........  ;;; . @@@#*++===;;;;;;:;;:;::;;;:.
     .. .       @***#%%#****++==;;;;;;;;::.
                @++==*@%#*+==;;;:::::.::.
               # ++=;;:::......                          :
"""

ASCII_LIGHT = r"""

                       ....
                 .::::;=;;;:.::  ..:.....   :
               ;;:::;;=:::;;::=;:;+==;;;++=;
             .....:;=;;;:::;+;;;++**###%##*==;
                 .;;:::=;:::;=;:;*#**+++***+**=.
                .:...:=;;;=+===;:=#%##*++=====+**=.
               .: .:;;;;++*%%%#%%#%%%%%%####**###+...
              ::  .===+**##%%%#%%%%%%@@%%%%%%%%%%@;
              . ..:*#%*#%%%%%#%%%%%#%%%@@@@@@%%%%%@@.
     .         :::+*######%#%%#%%%%%%%%@%%%@@@%%%%%#*
     .        :;;;==+**++#####%%%%####%%%#%%@@@%@%%#*
            .;+;:::;=+++*#####%%%#*###%%%%%%%@@@%%%##
       ..:;+==:::;======;=++*##****###%%@%%%%%%%%%%#%
    .:..:;+*+;;;;**++=;=;:::;;=+++*###%##%%#*#%%@%%**
    ::.:;;;;++==#%###*+++;:.:::;;;+*#%%##%##==#%@%%#*.
    :::::;==;;=+++==+**++;:....:;;=+=;;::;;;=;*%@%#*=
    ....;=+=......::;+++;:.   ..:;;===;;;::.::=%@#+;
     ...;=+=    .;:;%#=;:.    ..::;=+%%=;+;:..;%%*+
      ..:;;;     ...::...     ..::::;;;:::::..:*%#=:
       .:::.                  .....:::.........=%*;
         .;.                  .................;=;
                               .::.............::.
                               ..::.............::*=
                             ..:::::...........:.+@@@;
                            .::::;:............;;@@@@@;
                             ...:;::..........:%@@@@@%@
:;;:.                  .    ...:::::;;:.......;=@@@@@%@.
:=%@@@@@%%  ..        :;:;;;=========;;:.....:@+@@@@@@@
:;;=*%%%%#;: +.      ......::::::;;;;:::::..:#@@@@@@@@@
;==+=+*%@@::#@;          ..:;;;;;;;:::::::::*@@@@@@@@@@+
++++++++##::.*+      ......:...::::::::::::=@@@@@@@@@@@@@%
*****++*+*#*#@#             ........:::::;+#@@@@@@@@@@@@%%
##*******#*#%**  ....     ....::::::;;;;=##%@@@@@@@@@@@@%%
%############*%  ....:::;;;;==+****#%%#*###@@@@@@@@@@@@@@:
"""

# ==================================================================
# MOTOR — nao precisa mexer daqui para baixo
# ==================================================================

LARGURA_COL = 72
X_ASCII, X_TEXTO = 15, 390
Y_TEXTO, ALTURA_LINHA = 30, 20
Y_ASCII, ALTURA_ASCII, FONTE_ASCII = 24, 12, 10
ASCII_COLS, ASCII_ROWS = 58, 35
LARGURA_SVG, ALTURA_SVG = 1085, 455

TEMAS = {
    "dark_mode.svg": {
        "arte": "ASCII_DARK", "fundo": "#161b22", "texto": "#c9d1d9",
        "chave": "#ffa657", "valor": "#a5d6ff", "pontos": "#616e7f",
        "mais": "#3fb950", "menos": "#f85149",
    },
    "light_mode.svg": {
        "arte": "ASCII_LIGHT", "fundo": "#f6f8fa", "texto": "#24292f",
        "chave": "#953800", "valor": "#0a3069", "pontos": "#c2cfde",
        "mais": "#1a7f37", "menos": "#cf222e",
    },
}

PADRAO = {
    "age": "0 years, 0 months, 0 days", "repos": "0", "contrib": "0",
    "stars": "0", "commits": "0", "followers": "0",
    "loc": "0", "loc_add": "0", "loc_del": "0",
}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pontos(n):
    if n <= 0:
        return ""
    if n == 1:
        return " "
    if n == 2:
        return ". "
    return " " + "." * (n - 2) + " "


def linha_titulo(texto, y):
    resto = LARGURA_COL - len(texto) - 1
    traco = "-" + "\u2014" * max(0, resto - 4) + "-\u2014-"
    return f'<tspan x="{X_TEXTO}" y="{y}">{esc(texto)} {traco}</tspan>'


def chave_svg(chave):
    return '.'.join(f'<tspan class="key">{esc(p)}</tspan>' for p in chave.split("."))


def linha_campo(chave, valor, y, id_valor=None):
    d = pontos(LARGURA_COL - (2 + len(chave) + 1 + len(str(valor))))
    ip = f' id="{id_valor}_dots"' if id_valor else ""
    iv = f' id="{id_valor}"' if id_valor else ""
    return (f'<tspan x="{X_TEXTO}" y="{y}" class="cc">. </tspan>{chave_svg(chave)}:'
            f'<tspan class="cc"{ip}>{d}</tspan>'
            f'<tspan class="value"{iv}>{esc(valor)}</tspan>')


def linha_stats_repos(y):
    meio = f" {{Contributed: {PADRAO['contrib']}}} | "
    livre = LARGURA_COL - (2 + 6 + len(PADRAO["repos"]) + len(meio) + 6 + len(PADRAO["stars"]))
    d1, d2 = pontos(livre // 2), pontos(livre - livre // 2)
    return (f'<tspan x="{X_TEXTO}" y="{y}" class="cc">. </tspan><tspan class="key">Repos</tspan>:'
            f'<tspan class="cc" id="repo_data_dots">{d1}</tspan><tspan class="value" id="repo_data">{PADRAO["repos"]}</tspan>'
            f' {{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{PADRAO["contrib"]}</tspan>}} | '
            f'<tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots">{d2}</tspan>'
            f'<tspan class="value" id="star_data">{PADRAO["stars"]}</tspan>')


def linha_stats_commits(y):
    livre = LARGURA_COL - (2 + 8 + len(PADRAO["commits"]) + 3 + 10 + len(PADRAO["followers"]))
    d1, d2 = pontos(livre // 2), pontos(livre - livre // 2)
    return (f'<tspan x="{X_TEXTO}" y="{y}" class="cc">. </tspan><tspan class="key">Commits</tspan>:'
            f'<tspan class="cc" id="commit_data_dots">{d1}</tspan><tspan class="value" id="commit_data">{PADRAO["commits"]}</tspan>'
            f' | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots">{d2}</tspan>'
            f'<tspan class="value" id="follower_data">{PADRAO["followers"]}</tspan>')


def linha_stats_loc(y):
    livre = LARGURA_COL - (2 + 14 + len(PADRAO["loc"]) + 3 + len(PADRAO["loc_add"]) + 4 + len(PADRAO["loc_del"]) + 4)
    d1, d2 = pontos(livre - 1), " "
    return (f'<tspan x="{X_TEXTO}" y="{y}" class="cc">. </tspan><tspan class="key">Lines of Code</tspan>:'
            f'<tspan class="cc" id="loc_data_dots">{d1}</tspan><tspan class="value" id="loc_data">{PADRAO["loc"]}</tspan>'
            f' ( <tspan class="addColor" id="loc_add">{PADRAO["loc_add"]}</tspan><tspan class="addColor">++</tspan>, '
            f'<tspan id="loc_del_dots">{d2}</tspan><tspan class="delColor" id="loc_del">{PADRAO["loc_del"]}</tspan>'
            f'<tspan class="delColor">--</tspan> )')


def bloco_ascii(arte):
    linhas = [l for l in arte.split("\n") if l.strip() != ""]
    if len(linhas) > ASCII_ROWS:
        raise SystemExit(f"Arte com {len(linhas)} linhas; maximo {ASCII_ROWS}.")
    largo = max(len(l) for l in linhas)
    if largo > ASCII_COLS:
        raise SystemExit(f"Arte com {largo} colunas; maximo {ASCII_COLS}.")
    topo = (ASCII_ROWS - len(linhas)) // 2
    return "\n".join(
        f'<tspan x="{X_ASCII}" y="{Y_ASCII + (topo + i) * ALTURA_ASCII}">{esc(l)}</tspan>'
        for i, l in enumerate(linhas))


def montar(nome, tema):
    corpo, y = [], Y_TEXTO
    for item in LINHAS:
        t = item[0]
        if t == "vazio":
            corpo.append(f'<tspan x="{X_TEXTO}" y="{y}" class="cc">. </tspan>')
        elif t == "titulo":
            corpo.append(linha_titulo(item[1], y))
        elif t == "campo":
            corpo.append(linha_campo(item[1], item[2], y))
        elif t == "uptime":
            corpo.append(linha_campo("Uptime", PADRAO["age"], y, id_valor="age_data"))
        elif t == "stats_repos":
            corpo.append(linha_stats_repos(y))
        elif t == "stats_commits":
            corpo.append(linha_stats_commits(y))
        elif t == "stats_loc":
            corpo.append(linha_stats_loc(y))
        else:
            raise SystemExit(f"Tipo desconhecido: {t}")
        y += ALTURA_LINHA

    if y - ALTURA_LINHA > ALTURA_SVG - 25:
        raise SystemExit("LINHAS nao cabe na altura do SVG.")

    arte = bloco_ascii(globals()[tema["arte"]])
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{LARGURA_SVG}px" height="{ALTURA_SVG}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {tema['chave']};}}
.value {{fill: {tema['valor']};}}
.addColor {{fill: {tema['mais']};}}
.delColor {{fill: {tema['menos']};}}
.cc {{fill: {tema['pontos']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{LARGURA_SVG}px" height="{ALTURA_SVG}px" fill="{tema['fundo']}" rx="15"/>
<text x="{X_ASCII}" y="{Y_ASCII}" fill="{tema['texto']}" font-size="{FONTE_ASCII}px" class="ascii">
{arte}
</text>
<text x="{X_TEXTO}" y="{Y_TEXTO}" fill="{tema['texto']}">
{chr(10).join(corpo)}
</text>
</svg>"""
    with open(nome, "w", encoding="utf-8") as f:
        f.write(svg)
    print("gerado:", nome)


if __name__ == "__main__":
    for nome, tema in TEMAS.items():
        montar(nome, tema)
    print("\nPronto. Abra os arquivos no navegador para conferir.")
