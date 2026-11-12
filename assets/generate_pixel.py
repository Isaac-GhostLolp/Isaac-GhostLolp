#!/usr/bin/env python3
"""
Ghost Mart — versão PIXEL ART.

Mesma cena e mesmos dados da versão lisa, mas desenhada numa grade de pixels
(cada "pixel" = 4px na tela), com fonte bitmap 5x7 própria, dithering no lugar
de gradientes e animações em passos (steps) para o movimento ficar "travadinho".

    python3 assets/generate_pixel.py      → gera tudo em assets/pixel/
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "pixel"
OUT.mkdir(exist_ok=True)
S = 4  # tamanho de um pixel da arte, em px de tela

ICE, CYAN, SKY, DEEP, MUTED, WARM = "#e0f7ff", "#67e8f9", "#7dd3fc", "#38bdf8", "#5b7a99", "#fbbf24"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

# ---------------------------------------------------------------------------
# fonte bitmap 5x7
# ---------------------------------------------------------------------------
_F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I .###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.
J ..### ...#. ...#. ...#. ...#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# #...# ##..# #.#.# #..## #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# #.#.# .#.#.
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ####. ....# ....# .###. ....# ....# ####.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 .###. #.... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ....# .###.
. ..... ..... ..... ..... ..... .##.. .##..
, ..... ..... ..... ..... .##.. ..#.. .#...
: ..... .##.. .##.. ..... .##.. .##.. .....
- ..... ..... ..... .###. ..... ..... .....
/ ....# ....# ...#. ..#.. .#... #.... #....
& .##.. #..#. #.#.. .#... #.#.# #..#. .##.#
' ..#.. ..#.. .#... ..... ..... ..... .....
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
% ##..# ##..# ...#. ..#.. .#... #..## #..##
$ ..#.. .#### #.#.. .###. ..#.# ####. ..#..
_ ..... ..... ..... ..... ..... ..... #####
# .#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.
< ...#. ..#.. .#... #.... .#... ..#.. ...#.
> .#... ..#.. ...#. ....# ...#. ..#.. .#...
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
( ...#. ..#.. .#... .#... .#... ..#.. ...#.
) .#... ..#.. ...#. ...#. ...#. ..#.. .#...
? .###. #...# ....# ...#. ..#.. ..... ..#..
* ..... ..... ..#.. .###. ..#.. ..... .....
"""
FONT = {}
for ln in _F.strip().splitlines():
    ch, *rows = ln.split(" ")
    FONT[ch] = rows
FONT["·"] = [".....", ".....", ".....", "..#..", ".....", ".....", "....."]
FONT["Ç"] = FONT["C"] + ["..#..", ".#..."]
TRANS = str.maketrans({"é": "E", "É": "E", "ç": "Ç", "—": "-", "ã": "A", "á": "A", '"': "'"})


def glyphs(s):
    s = s.translate(TRANS).upper()
    pts, x = [], 0
    for ch in s:
        if ch == " ":
            x += 4
            continue
        rows = FONT.get(ch, FONT["?"])
        for y, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == "#":
                    pts.append((x + i, y))
        x += 6
    return pts, max(x - 1, 0)


def text_width(s, scale):
    return glyphs(s)[1] * scale


def runs_path(pts):
    """pontos -> path com retângulos (junta corridas na horizontal e depois na vertical)"""
    rows = {}
    for x, y in pts:
        rows.setdefault(y, set()).add(x)
    spans = {}
    for y, xs in rows.items():
        xs = sorted(xs)
        st = pv = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == pv + 1:
                pv = x
                continue
            spans.setdefault((st, pv - st + 1), []).append(y)
            if x is not None:
                st = pv = x
    d = []
    for (x, w), ys in spans.items():
        ys.sort()
        y0 = prev = ys[0]
        for y in ys[1:] + [None]:
            if y is not None and y == prev + 1:
                prev = y
                continue
            d.append(f"M{x} {y0}h{w}v{prev - y0 + 1}h-{w}z")
            if y is not None:
                y0 = prev = y
    return "".join(d)


def text(s, x, y, scale=1.0, fill=ICE, anchor="start", extra="", neon=None):
    pts, w = glyphs(s)
    if anchor == "middle":
        x -= w * scale / 2
    elif anchor == "end":
        x -= w * scale
    d = runs_path(pts)
    out = ""
    if neon:  # "brilho" pixelado: contorno de 1 pixel da fonte
        halo = {(px + dx, py + dy) for px, py in pts for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - set(pts)
        out += f'<path d="{runs_path(halo)}" fill="{neon}" opacity=".45"/>'
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})"{extra}>{out}<path d="{d}" fill="{fill}"/></g>'


class Layer:
    """camada de pixels: {(x,y): cor}. Vira um <path> por cor."""

    def __init__(self):
        self.px = {}

    def set(self, x, y, c):
        self.px[(int(x), int(y))] = c

    def rect(self, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.px[(xx, yy)] = c

    def svg(self, attrs=""):
        by = {}
        for p, c in self.px.items():
            by.setdefault(c, []).append(p)
        inner = "".join(f'<path d="{runs_path(v)}" fill="{c}"/>' for c, v in by.items())
        return f"<g{attrs}>{inner}</g>"


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def bayer(x, y):
    return (BAYER[y % 4][x % 4] + .5) / 16


def vgrad(layer, x0, y0, w, h, colors):
    """gradiente vertical com dithering ordenado (só nas transições)"""
    n = len(colors) - 1
    for y in range(h):
        p = y / max(h - 1, 1) * n
        i = min(int(p), n - 1)
        f = min(max((p - i - .5) * 3 + .5, 0), 1)  # dither só numa faixa estreita de transição
        for x in range(w):
            c = colors[i + 1] if bayer(x0 + x, y0 + y) < f else colors[i]
            layer.set(x0 + x, y0 + y, c)


def snow(W, H, seed, layers=((60, 1, .5, 26), (35, 1, .75, 17), (12, 2, .95, 11))):
    rnd = random.Random(seed)
    css, out = [], []
    for i, (n, size, op, dur) in enumerate(layers):
        pts = set()
        for _ in range(n):
            x, y = rnd.randrange(W), rnd.randrange(H)
            for dx in range(size):
                for dy in range(size):
                    pts.add((x + dx, y + dy))
        d = runs_path(pts)
        sw = 2 + i
        css.append(
            f".s{i}{{animation:f{i} {dur}s steps({H}) infinite}}@keyframes f{i}{{from{{transform:translateY(-{H}px)}}to{{transform:translateY(0)}}}}"
            f".w{i}{{animation:w{i} {dur * .6:.1f}s steps({sw * 2}) infinite alternate}}@keyframes w{i}{{from{{transform:translateX(-{sw}px)}}to{{transform:translateX({sw}px)}}}}"
        )
        out.append(
            f'<g class="w{i}" opacity="{op}"><g class="s{i}"><path d="{d}" fill="{ICE}"/>'
            f'<path d="{d}" fill="{ICE}" transform="translate(0 {H})"/></g></g>'
        )
    return "".join(css), "".join(out)


def wrap(W, H, body, css, title, label):
    title, label = (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for v in (title, label))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W * S}" height="{H * S}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}"><title>{title}</title>'
        f"<style>{css}{REDUCED}</style>{body}</svg>"
    )


# ---------------------------------------------------------------------------
# sprite do fantasma (13x36) — a figura da foto de perfil
# ---------------------------------------------------------------------------
GHOST = """
.....###.....
....#####....
....#####....
....#####....
....#####....
.....###.....
.....###.....
..#########..
.###########.
.###########.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
.##.#####.##.
....#####....
....#####....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
....##.##....
...###.###...
""".split()


def ghost_layers(fx, fy):
    """fx,fy = pé central. Retorna svg com halo dithered, rastro e corpo."""
    h = len(GHOST)
    M = {(fx - 6 + x, fy - h + 1 + y) for y, r in enumerate(GHOST) for x, c in enumerate(r) if c == "#"}

    def dil(S_, k):
        return {(x + dx, y + dy) for x, y in S_ for dx in range(-k, k + 1) for dy in range(-k, k + 1) if abs(dx) + abs(dy) <= k + k // 2}

    d1, d2, d4, d7 = dil(M, 1), dil(M, 2), dil(M, 4), dil(M, 7)
    out = []
    # reflexo no chão
    refl = {(x, fy + 1 + dy) for x in range(fx - 16, fx + 17) for dy in range(3)
            if ((x - fx) / 16) ** 2 + (dy / 3) ** 2 < 1 and (x + dy) % 2 == 0}
    out.append(f'<path class="br" d="{runs_path(refl)}" fill="{CYAN}" opacity=".45"/>')
    # rastro (afterimage, como a foto em longa exposição)
    for k, (dx, dy, op) in enumerate([(7, -5, .14), (4, -3, .26)]):
        tr = {(x + dx, y + dy) for x, y in M if (x + y + k) % 2 == 0}
        out.append(f'<path class="tr" d="{runs_path(tr)}" fill="{DEEP}" opacity="{op}"/>')
    ring4 = {p for p in d7 - d4 if p[0] % 2 == 0 and p[1] % 2 == 0}
    ring3 = {p for p in d4 - d2 if (p[0] + p[1]) % 2 == 0}
    out.append(f'<g class="br"><path d="{runs_path(ring4)}" fill="{DEEP}" opacity=".3"/>'
               f'<path d="{runs_path(ring3)}" fill="{DEEP}" opacity=".55"/>'
               f'<path d="{runs_path(d2 - d1)}" fill="{DEEP}" opacity=".8"/></g>')
    out.append(f'<path d="{runs_path(d1 - M)}" fill="#a5f3fc"/>')
    out.append(f'<path d="{runs_path(M)}" fill="#f4feff"/>')
    return "".join(out)


def pine(L, cx, base, h):
    for r in range(h):
        tier = r % (h // 3)
        half = int(1 + tier * .55 + (r // (h // 3)) * 2)
        for x in range(cx - half, cx + half + 1):
            L.set(x, base - h + r, "#0b1a33")
        if tier == 0:
            L.set(cx, base - h + r, "#5d86ad")
            if r:
                L.set(cx - 1, base - h + r, "#3c6189")
                L.set(cx + 1, base - h + r, "#3c6189")


# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
def header():
    W, H = 300, 115
    rnd = random.Random(7)
    L = Layer()
    vgrad(L, 0, 0, W, 92, ["#03050b", "#050a16", "#081226", "#0c1c36"])

    stars, twinkle = Layer(), Layer()
    for _ in range(70):
        x, y = rnd.randrange(W), rnd.randrange(70)
        (twinkle if rnd.random() < .3 else stars).set(x, y, rnd.choice([ICE, SKY, "#9cc7e6"]))

    # morros e luzes distantes
    for x in range(W):
        top = 86 + round(1.3 * __import__("math").sin(x / 19) + .8 * __import__("math").sin(x / 7))
        for y in range(top, 93):
            L.set(x, y, "#060c19")
    for x, c in [(8, ICE), (13, SKY), (22, "#fde68a"), (24, "#fff7d6"), (25, "#fde68a"), (38, SKY), (44, ICE), (57, SKY), (65, ICE)]:
        L.set(x, 88, c)
    for x in range(18, 30):
        if x % 2 == 0:
            L.set(x, 89, "#3d3520")

    for cx, base, h in [(172, 94, 30), (290, 94, 36), (296, 95, 24), (164, 95, 21)]:
        pine(L, cx, base, h)

    # chão de neve
    import math
    for x in range(W):
        top = 92 + round(1.2 * math.sin(x / 31) + .6 * math.sin(x / 11))
        L.set(x, top, "#6f98bf")
        L.set(x, top + 1, "#3a6290")
        vgrad(L, x, top + 2, 1, H - top - 2, ["#1d3b60", "#122a47", "#08132a"])

    # luz da loja derramada na neve (dither)
    for y in range(96, 112):
        for x in range(150, W):
            dx, dy = (x - 232) / 75, (y - 101) / 11
            v = dx * dx + dy * dy
            if v < 1 and bayer(x, y) < (1 - v) * .8:
                L.set(x, y, "#4a7aa8" if v < .35 else "#2c5582")

    # poste
    lamp = Layer()
    for y in range(57, 99):
        L.set(152, y, "#1f3556")
    for x in range(152, 162):
        L.set(x, 56, "#1f3556")
    L.rect(157, 55, 6, 2, "#2a4468")
    
    for y in range(59, 100):
        half = 2 + (y - 59) * .5
        for x in range(int(160 - half), int(160 + half) + 1):
            if bayer(x, y) < .55 * (1 - (y - 59) / 44) ** 1.5:
                lamp.set(x, y, "#c9ecff")
    for x in range(140, 182):
        for y in range(97, 102):
            dx, dy = (x - 160) / 20, (y - 99) / 3
            if dx * dx + dy * dy < 1 and (x + y) % 2 == 0:
                lamp.set(x, y, "#6f98bf")

    # loja
    st = Layer()
    st.rect(180, 47, 107, 52, "#0b1628")
    st.rect(177, 45, 113, 3, "#070f1e")
    for x in range(176, 291):
        st.set(x, 43, "#d9eef9")
        st.set(x, 44, "#d9eef9")
        if x in (190, 191, 214, 238, 239, 262, 281):
            st.set(x, 45, "#d9eef9")
            if x % 2 == 0:
                st.set(x, 46, "#a9cbe2")
    for x in range(178, 289, 3):
        st.set(x, 42, "#d9eef9")
    st.rect(195, 49, 76, 13, "#123a5c")
    st.rect(196, 50, 74, 11, "#050b16")

    def glass(x0, y0, w, h):
        vgrad(st, x0, y0, w, h, ["#eafcff", "#cdeefb", "#a9def3"])

    def shelf_row(x0, x1, y):
        x = x0 + 1
        while x < x1 - 2:
            w = rnd.choice([1, 2, 2, 3])
            h = rnd.choice([2, 3, 4])
            c = rnd.choice(["#2b5f8a", "#3b82a6", "#1e4f7a", "#6f98bf", "#c99a3b", "#4f7f9f"])
            st.rect(x, y - h, w, h, c)
            x += w + rnd.choice([0, 1, 1])
        st.rect(x0, y, x1 - x0, 1, "#1b3a5c")

    glass(185, 66, 36, 27)
    for y in (73, 80, 87):
        shelf_row(185, 221, y)
    st.rect(203, 66, 1, 27, "#08111f")
    glass(225, 66, 16, 32)
    for y in (75, 83):
        shelf_row(225, 241, y)
    st.rect(238, 78, 1, 4, "#08111f")
    glass(245, 66, 36, 27)
    shelf_row(245, 281, 73)
    # caixa: o programador do turno da noite
    st.rect(267, 76, 3, 3, "#0b1830")
    st.rect(265, 79, 7, 7, "#0b1830")
    st.rect(245, 85, 36, 8, "#0b1830")
    st.rect(255, 79, 7, 5, "#132a4a")
    st.rect(254, 84, 9, 1, "#132a4a")
    st.rect(250, 83, 2, 2, "#e9d7b5")
    for x0, y0, w, h in [(184, 65, 38, 29), (224, 65, 18, 34), (244, 65, 38, 29)]:
        for x in range(x0, x0 + w):
            st.set(x, y0, "#08111f"); st.set(x, y0 + h - 1, "#08111f")
        for y in range(y0, y0 + h):
            st.set(x0, y, "#08111f"); st.set(x0 + w - 1, y, "#08111f")
    st.rect(183, 94, 40, 1, "#d9eef9")
    st.rect(243, 94, 40, 1, "#d9eef9")

    anim = Layer()
    anim.rect(256, 80, 5, 3, CYAN)
    steam = Layer()
    for x, y in [(250, 81), (251, 80), (250, 79)]:
        steam.set(x, y, "#e9d7b5")

    # pegadas
    fp = Layer()
    for i in range(14):
        t = i / 13
        x = 112 + (226 - 112) * t
        y = 102 + (98 - 102) * t + (1 if i % 2 else -1)
        fp.rect(x, y, 2, 1, "#2b4f78" if t > .4 else "#1f3d63")

    # texto + digitação
    typed = "$ FULL STACK, GAME DEV & DESIGNER"
    ts = .625
    cw = 6 * ts
    seq = [i * cw for i in range(len(typed) + 1)]
    seq = seq + [seq[-1]] * 16 + [0]
    keys = ";".join(f"{i / (len(seq) - 1):.4f}" for i in range(len(seq)))
    vals = ";".join(f"{v:.2f}" for v in seq)
    curx = ";".join(f"{14 + v + .6:.2f}" for v in seq)

    snow_css, flakes = snow(W, H, 11)
    css = (
        "#tw{animation:tw 3s steps(2) infinite}@keyframes tw{50%{opacity:.15}}"
        ".sign{animation:fl 7s steps(1) infinite}@keyframes fl{0%,100%{opacity:1}61%{opacity:.3}62%{opacity:1}64%{opacity:.15}65%{opacity:1}}"
        ".open{animation:bl 2.4s steps(2) infinite}@keyframes bl{50%{opacity:.3}}"
        ".lamp{animation:lp 11s steps(1) infinite}@keyframes lp{0%,100%{opacity:1}83%{opacity:.35}84%{opacity:1}86%{opacity:.5}87%{opacity:1}}"
        ".br{animation:br 5s steps(5) infinite}@keyframes br{50%{opacity:.4}}"
        ".tr{animation:trl 6s steps(3) infinite alternate}@keyframes trl{to{transform:translate(2px,-1px);opacity:.08}}"
        ".cur{animation:cu 1s steps(1) infinite}@keyframes cu{50%{opacity:0}}"
        ".scr{animation:sc 3s steps(3) infinite}@keyframes sc{50%{opacity:.55}}"
        ".stm{animation:sm 2.4s steps(4) infinite}@keyframes sm{0%{transform:translateY(0);opacity:0}25%{opacity:.8}100%{transform:translateY(-4px);opacity:0}}"
        + snow_css
    )
    body = f"""
{L.svg()}{stars.svg()}{twinkle.svg(' id="tw"')}
<g class="lamp">{lamp.svg(' opacity=".5"')}<rect x="158" y="57" width="4" height="1" fill="{ICE}"/><rect x="157" y="58" width="6" height="1" fill="{SKY}" opacity=".5"/></g>
{st.svg()}
<g class="sign">{text("GHOST MART", 233, 52, 1, CYAN, "middle", neon=DEEP)}</g>
{text("24H", 274, 53, .5, WARM)}
<g class="open"><rect x="227" y="87" width="12" height="5" fill="#1a0f02"/>{text("OPEN", 233, 88.2, .45, WARM, "middle")}</g>
{anim.svg(' class="scr"')}{steam.svg(' class="stm"')}
{fp.svg()}
{ghost_layers(105, 100)}
{text("// NIGHT SHIFT · VACARIA, RS", 14, 12, .5, MUTED)}
{text("ISAAC GONÇALVES", 14, 20, 1.25, ICE, neon="#1d3b60")}
<clipPath id="tc"><rect x="14" y="36" height="7" width="0"><animate attributeName="width" values="{vals}" keyTimes="{keys}" dur="9s" repeatCount="indefinite" calcMode="discrete"/></rect></clipPath>
<g clip-path="url(#tc)">{text(typed, 14, 37, ts, SKY)}</g>
<rect class="cur" x="14" y="36" width="3" height="6" fill="{CYAN}"><animate attributeName="x" values="{curx}" keyTimes="{keys}" dur="9s" repeatCount="indefinite" calcMode="discrete"/></rect>
{flakes}"""
    (OUT / "header.svg").write_text(wrap(W, H, body, css, "isaac gonçalves — ghost mart (pixel)",
                                         "Isaac Gonçalves — loja de conveniência em pixel art numa noite de neve"), encoding="utf-8")


# ---------------------------------------------------------------------------
# PRATELEIRA   (EDITE AQUI — rótulos curtos, a fonte pixel ocupa espaço)
# ---------------------------------------------------------------------------
LANGS = [
    ("PHP", "PHP 8", "#8b93c9", "BACKEND·DAILY"),
    ("JS", "JAVASCRIPT", "#e8cf4a", "VANILLA,NO FW"),
    ("C#", "C#", "#a68be0", "UNITY GAMEPLAY"),
    ("GD", "GDSCRIPT", "#6ea8d8", "GODOT 4"),
    ("SQL", "MARIADB", "#4fa3b8", "MULTI-TENANT"),
    ("</>", "HTML+CSS", "#e58a6a", "PIXEL-PERFECT"),
]
TOOLS = [
    ("U6", "UNITY 6", "#cbd5e1", "SCRIPTABLE OBJ"),
    ("GO", "GODOT", "#6ea8d8", "+ TILED MAPS"),
    ("GIT", "GIT", "#e8795a", "SMALL COMMITS"),
    ("PW", "PLAYWRIGHT", "#5fb96f", "VISUAL TESTS"),
    ("FG", "FIGMA", "#c08ae8", "BEFORE CODE"),
    ("PX", "ASEPRITE", "#e0a5c4", "PIXEL ART"),
]


def shelf():
    W, H = 300, 118
    L = Layer()
    L.rect(0, 0, W, H, "#050a14")
    vgrad(L, 0, 0, W, H, ["#0a1426", "#070e1c", "#040811"])
    light = Layer()
    light.rect(75, 3, 150, 1, ICE)
    for y in range(5, 62):
        half = 75 + (y - 5) * 1.6
        for x in range(int(150 - half), int(150 + half)):
            if 0 <= x < W and bayer(x, y) < .22 * (1 - (y - 5) / 57) ** 2 and not (y < 16 and abs(x - 150) > 70):
                light.set(x, y, "#9cc7e6")
    tops = [56, 104]
    for t in tops:
        L.rect(4, t, W - 8, 1, "#3c6189")
        L.rect(4, t + 1, W - 8, 3, "#13243d")
        L.rect(4, t + 4, W - 8, 2, "#060c18")

    items = []
    for row, data in enumerate([LANGS, TOOLS]):
        top = tops[row]
        for i, (lab, name, color, tag) in enumerate(data):
            cx = 27 + i * 49
            P = Layer()
            if row == 0:
                w, h = 40, 30
                x0, y0 = cx - w // 2, top - h
                P.rect(x0, y0, w, h, "#0b1629")
                P.rect(x0, y0, w, 4, color)
                for x in range(x0, x0 + w):
                    P.set(x, y0 + h - 1, "#1d3b60")
                for y in range(y0, y0 + h):
                    P.set(x0, y, "#1d3b60"); P.set(x0 + w - 1, y, "#1d3b60")
                lbl = text(lab, cx, y0 + 10, 1, color, "middle", neon="#13243d")
                nm = text(name, cx, y0 + 22, .5, "#b9d6ee", "middle")
            else:
                w, h = 34, 26
                x0, y0 = cx - w // 2, top - h
                P.rect(x0 + 1, y0, w - 2, h, "#0b1629")
                P.rect(x0, y0 + 1, w, h - 2, "#0b1629")
                P.rect(x0 + 1, y0, w - 2, 2, "#1d3b60")
                for x in range(x0, x0 + w):
                    if (x + y0) % 2 == 0:
                        for y in range(y0 + 7, y0 + 18):
                            P.set(x, y, "#13243d")
                P.rect(x0, y0 + 7, w, 1, color)
                P.rect(x0, y0 + 17, w, 1, color)
                lbl = text(lab, cx, y0 + 9, .75, color, "middle")
                nm = text(name, cx, y0 + 20, .5, "#b9d6ee", "middle")
            tw = text_width(tag, .5) + 4
            tagr = f'<rect x="{cx - tw / 2:.1f}" y="{top + 7}" width="{tw:.1f}" height="5.5" fill="#dff3ff"/>'
            tagt = text(tag, cx, top + 8, .5, "#0a1a30", "middle")
            delay = (row * 6 + i) * .12
            items.append(f'<g class="on" style="animation-delay:{delay:.2f}s">{P.svg()}{lbl}{nm}{tagr}{tagt}</g>')

    css = (
        ".on{opacity:0;animation:on .8s steps(4) forwards}@keyframes on{0%{opacity:0}40%{opacity:.7}60%{opacity:.2}100%{opacity:1}}"
        ".tb{animation:tb 9s steps(1) infinite}@keyframes tb{0%,100%{opacity:1}71%{opacity:.3}72%{opacity:1}74%{opacity:.5}75%{opacity:1}}"
        "@media (prefers-reduced-motion: reduce){.on{opacity:1}}"
    )
    body = f"""{L.svg()}{light.svg(' class="tb" opacity=".35"')}
{text("AISLE 02", 8, 8, .5, MUTED)}{text("LANGUAGES & TOOLS", 8, 13, .75, ICE)}
{text("WHAT I ACTUALLY REACH FOR", W - 8, 8, .5, MUTED, "end")}{text("RESTOCKED NIGHTLY", W - 8, 13, .5, WARM, "end")}
{"".join(items)}"""
    (OUT / "shelf.svg").write_text(wrap(W, H, body, css, "aisle 02 — languages & tools (pixel)",
                                        "Linguagens: PHP, JavaScript, C#, GDScript, SQL, HTML/CSS. Ferramentas: Unity 6, Godot, Git, Playwright, Figma, Aseprite."), encoding="utf-8")


# ---------------------------------------------------------------------------
# CARDS DE PROJETO   (EDITE AQUI — linhas de até ~42 caracteres)
# ---------------------------------------------------------------------------
PROJECTS = [
    dict(file="project-ghostguard.svg", aisle="01", title="GHOSTGUARD MANAGER", status="active", label="ACTIVE DEV",
         lines=["MULTI-TENANT SAAS ERP FOR SMALL BUSINESS,", "BARBERSHOPS FIRST. CUSTOM MVC FRAMEWORK,", "TIERED BILLING, FULL TENANT ISOLATION."],
         stack=["PHP 8", "MARIADB", "CUSTOM MVC", "VANILLA JS"]),
    dict(file="project-towerdefense.svg", aisle="02", title="TOWER DEFENSE - ANIME ED.", status="wip", label="IN PROGRESS",
         lines=["2D TOWER DEFENSE IN UNITY 6 WITH A FULL", "SUMMON SYSTEM. SCRIPTABLEOBJECTS, EVENT-", "DRIVEN (RYAN HIPPLE), SOLID."],
         stack=["UNITY 6", "C#", "SCRIPTABLEOBJECTS"]),
    dict(file="project-pokedex.svg", aisle="03", title="INTERACTIVE POKÉDEX", status="done", label="COMPLETE",
         lines=["A PHYSICAL-DEVICE POKEDEX IN PURE HTML,", "CSS & JS: POKEAPI SPRITES, STORAGE AND", "FULL KEYBOARD & D-PAD NAVIGATION."],
         stack=["HTML", "CSS", "JAVASCRIPT", "POKEAPI"]),
    dict(file="project-minecraft.svg", aisle="04", title="MINECRAFT SESSION CHALLENGES", status="done", label="COMPLETE",
         lines=["GAMIFIED GROUP SESSIONS: TIMER, PENALTY", "SEVERITY, PER-SESSION BINGO, PIXEL UI,", "ALL SAVED IN LOCALSTORAGE."],
         stack=["HTML", "CSS", "JAVASCRIPT"]),
]
STATUS = {"active": CYAN, "wip": WARM, "done": "#86efac"}


def project_card(p):
    W, H = 145, 62
    rnd = random.Random(p["aisle"])
    color = STATUS[p["status"]]
    L = Layer()
    vgrad(L, 2, 3, W - 4, H - 5, ["#0c1a33", "#081227", "#050b17"])
    for x in range(2, W - 2):
        L.set(x, 3, "#1d3a5e"); L.set(x, H - 3, "#1d3a5e")
    for y in range(3, H - 2):
        L.set(2, y, "#1d3a5e"); L.set(W - 3, y, "#1d3a5e")
    # neve no topo do card
    for x in range(1, W - 1):
        L.set(x, 2, "#d9eef9")
        if x % 7 in (0, 1) or x % 13 == 3:
            L.set(x, 3, "#d9eef9")
        if x % 13 == 3:
            L.set(x, 4, "#a9cbe2")
    for x in range(2, W - 2, 3):
        L.set(x, 1, "#d9eef9")
    # halo pixelado da cor do status
    halo = Layer()
    for y in range(5, 30):
        for x in range(105, W - 3):
            dx, dy = (x - 128) / 20, (y - 14) / 12
            v = dx * dx + dy * dy
            if v < 1 and bayer(x, y) < (1 - v) * .5:
                halo.set(x, y, color)
    chips, cx = [], 7
    for s in p["stack"]:
        w = text_width(s, .5) + 5
        chips.append(f'<rect x="{cx}" y="{H - 13}" width="{w:.1f}" height="7" fill="#0f2140" stroke="#24476e" stroke-width=".5"/>'
                     + text(s, cx + w / 2, H - 11.2, .5, "#b9d6ee", "middle"))
        cx += w + 2
    bars = Layer()
    x = max(W - 38, int(cx) + 3)
    while x < W - 8:
        bw = rnd.choice([1, 1, 2])
        bars.rect(x, H - 13, bw, 7, ICE)
        x += bw + rnd.choice([1, 1, 2])
    lines = "".join(text(l, 7, 27 + i * 6, .5, "#a9c4dc") for i, l in enumerate(p["lines"]))
    snow_css, flakes = snow(W, H, int(p["aisle"]), layers=((18, 1, .35, 18), (6, 1, .6, 12)))
    css = ".dot{animation:dt 1.6s steps(2) infinite}@keyframes dt{50%{opacity:.2}}.hl{animation:hl 5s steps(4) infinite}@keyframes hl{50%{opacity:.08}}" + snow_css
    lw = text_width(p["label"], .5)
    body = f"""{L.svg()}{halo.svg(' class="hl" opacity=".25"')}
<clipPath id="cc"><rect x="3" y="5" width="{W - 6}" height="{H - 8}"/></clipPath><g clip-path="url(#cc)">{flakes}</g>
{text("AISLE " + p["aisle"], 7, 9, .5, MUTED)}
<rect class="dot" x="{W - 9 - lw - 4}" y="9" width="2" height="2" fill="{color}"/>
{text(p["label"], W - 8, 9, .5, color, "end")}
{text(p["title"], 7, 16, .75 if text_width(p["title"], 1) > 128 else 1, ICE, neon="#13243d")}
{lines}{"".join(chips)}{bars.svg(' opacity=".6"')}"""
    (OUT / p["file"]).write_text(wrap(W, H, body, css, p["title"].title(), p["title"] + " — " + " ".join(p["lines"]).lower()), encoding="utf-8")


# ---------------------------------------------------------------------------
# CUPOM   (EDITE AQUI)
# ---------------------------------------------------------------------------
LEARNING = [("ADV. PHP ARCHITECTURE", 8), ("SAAS SECURITY HARDENING", 6), ("UNITY ECS / DOTS", 5), ("GODOT 4 TILEMAPS", 4), ("CLOUD & DEVOPS", 3)]
BAG = [("1X HOT COFFEE", "ALWAYS"), ("1X ARCH. SKETCH", "FIRST"), ("1X PW SCREENSHOT", "PASS"), ("1X YESTERDAY'S BUG", "FIXED")]


def receipt():
    W = 105
    ink, soft = "#1b2a3d", "#4b5b70"
    items, y = [], 10
    paper = Layer()

    def t(s, x, sc=.5, fill=ink, anchor="start"):
        items.append(text(s, x, y, sc, fill, anchor))

    def dash():
        nonlocal y
        for x in range(8, W - 8, 3):
            items.append(f'<rect x="{x}" y="{y}" width="2" height=".5" fill="#7b8796"/>')
        y += 4

    t("GHOST MART", W / 2, 1, ink, "middle"); y += 10
    t("OPEN 24H · VACARIA, RS", W / 2, .5, soft, "middle"); y += 5
    t("TERMINAL 03 · 03:12 AM", W / 2, .5, soft, "middle"); y += 7
    dash()
    t("CURRENTLY LEARNING", 8, .5, soft); y += 6
    for name, lvl in LEARNING:
        t(name, 8); y += 5
        for i in range(10):
            items.append(f'<rect x="{8 + i * 5}" y="{y}" width="4" height="2.5" fill="{ink if i < lvl else "#c9d2dc"}"/>')
        t(f"{lvl * 10}%", W - 8, .5, soft, "end"); y += 6
    dash()
    t("IN THE BAG TONIGHT", 8, .5, soft); y += 6
    for a, b in BAG:
        t(a, 8); t(b, W - 8, .5, ink, "end"); y += 5.5
    y += 1
    dash()
    t("TOTAL", 8, .75); t("STILL LEARNING", W - 8, .5, ink, "end"); y += 10
    t("THANK YOU, COME BACK", W / 2, .5, soft, "middle"); y += 5
    t("AFTER MIDNIGHT.", W / 2, .5, soft, "middle"); y += 7
    rnd = random.Random(42)
    x = 18
    while x < W - 18:
        bw = rnd.choice([1, 1, 1, 2])
        items.append(f'<rect x="{x}" y="{y}" width="{bw}" height="10" fill="{ink}"/>')
        x += bw + 1
    y += 13
    t("ISAAC-GHOSTLOLP", W / 2, .5, soft, "middle"); y += 8
    H = int(y) + 3
    vgrad(paper, 4, 2, W - 8, H - 2, ["#eef6fb", "#e4eef6", "#dbe8f2"])
    for x in range(4, W - 4):  # serrilhado
        if (x // 2) % 2 == 0:
            paper.set(x, H, "#dbe8f2")
    shadow = Layer()
    for yy in range(3, H + 2):
        for xx in (W - 4, W - 3):
            if (xx + yy) % 2 == 0:
                shadow.set(xx, yy, CYAN)
    total = H + 4
    css = (f".roll{{transform:translateY(-{total}px);animation:roll 3.2s steps(30) .3s forwards}}@keyframes roll{{to{{transform:translateY(0)}}}}"
           "@media (prefers-reduced-motion: reduce){.roll{animation:none;transform:none}}")
    body = (f'<clipPath id="pr"><rect class="roll" x="0" y="0" width="{W}" height="{total}"/></clipPath>'
            f'<g clip-path="url(#pr)">{shadow.svg(" opacity=\".35\"")}{paper.svg()}{"".join(items)}</g>')
    (OUT / "receipt.svg").write_text(wrap(W, total, body, css, "receipt — currently learning (pixel)",
                                          "Cupom: aprendendo arquitetura PHP avançada, segurança SaaS, Unity DOTS, Godot 4 tilemaps, cloud e devops."), encoding="utf-8")


# ---------------------------------------------------------------------------
# DIVISOR e RODAPÉ
# ---------------------------------------------------------------------------
def divider():
    W, H = 300, 9
    L = Layer()
    for x in range(0, W, 2):
        d = abs(x - W / 2) / (W / 2)
        if bayer(x, 4) > d * 1.1:
            L.set(x, 4, SKY)
    fl = Layer()
    for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, -2), (2, 2), (2, -2), (-2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
        fl.set(150 + dx, 4 + dy, ICE)
    css = ".sp{animation:sp 4s steps(2) infinite;transform-origin:150.5px 4.5px}@keyframes sp{50%{opacity:.4}}"
    body = f'<rect width="{W}" height="{H}" fill="#03050b" opacity="0"/>{L.svg(" opacity=\".6\"")}{fl.svg(" class=\"sp\"")}'
    (OUT / "divider.svg").write_text(wrap(W, H, body, css, "divider", "divisor"), encoding="utf-8")


def footer():
    import math
    W, H = 300, 60
    L = Layer()
    vgrad(L, 0, 0, W, 44, ["#03050b", "#060c19", "#0b1a33"])
    for x in range(W):
        top = 44 + round(1.0 * math.sin(x / 37) + .5 * math.sin(x / 9))
        L.set(x, top, "#6f98bf")
        vgrad(L, x, top + 1, 1, H - top - 1, ["#1d3b60", "#0f2240", "#060d1c"])
    shop = Layer()
    shop.rect(141, 36, 18, 8, "#0b1628")
    shop.rect(140, 35, 20, 1, "#d9eef9")
    shop.rect(143, 39, 5, 4, "#d6f5ff"); shop.rect(149, 39, 2, 5, "#d6f5ff"); shop.rect(152, 39, 5, 4, "#d6f5ff")
    shop.rect(145, 37, 10, 1, CYAN)
    for x in range(126, 175):
        for y in range(44, 48):
            dx, dy = (x - 150) / 24, (y - 45) / 3
            if dx * dx + dy * dy < 1 and (x + y) % 2 == 0:
                shop.set(x, y, "#4a7aa8")
    fp = Layer()
    for i in range(12):
        fp.rect(140 - i * 10, 49 + i * .6 + (1 if i % 2 else 0), 2, 1, "#2b4f78")
    snow_css, flakes = snow(W, H, 21, layers=((40, 1, .5, 20), (14, 1, .85, 13)))
    css = ".sh{animation:sh 6s steps(3) infinite}@keyframes sh{50%{opacity:.65}}" + snow_css
    body = f'{L.svg()}{shop.svg(" class=\"sh\"")}{fp.svg()}{text("THE LIGHTS STAY ON · SEE YOU AFTER MIDNIGHT", W / 2, 53, .5, MUTED, "middle")}{flakes}'
    (OUT / "footer.svg").write_text(wrap(W, H, body, css, "the lights stay on (pixel)", "as luzes da loja continuam acesas ao longe"), encoding="utf-8")


if __name__ == "__main__":
    header()
    shelf()
    for p in PROJECTS:
        project_card(p)
    receipt()
    divider()
    footer()
    print("ok →", ", ".join(f"{f.name} {f.stat().st_size // 1024}KB" for f in sorted(OUT.glob("*.svg"))))
