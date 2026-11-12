#!/usr/bin/env python3
"""
Ghost Mart — gerador dos SVGs animados do perfil.

Tudo é SVG puro com animação em CSS/SMIL, então funciona dentro de <img> no GitHub
(sem JS, sem fontes externas). Para mudar textos, projetos ou linguagens, edite os
dados nas seções marcadas com "EDITE AQUI" e rode:

    python3 assets/generate.py
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent
FONT = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

# paleta (tirada da foto de perfil: azul-ciano frio + um toque quente de café)
BG0 = "#03050b"
BG1 = "#081226"
ICE = "#e0f7ff"
CYAN = "#67e8f9"
SKY = "#7dd3fc"
DEEP = "#38bdf8"
MUTED = "#5b7a99"
WARM = "#fbbf24"

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# neve: camadas que descem em loop contínuo (duas cópias empilhadas)
# ---------------------------------------------------------------------------
def snow_layers(w, h, seed, layers=((70, 1.0, 1.6, 0.55, 26), (45, 1.6, 2.4, 0.75, 17), (18, 2.4, 3.4, 0.9, 11))):
    rnd = random.Random(seed)
    css, out = [], []
    for i, (count, rmin, rmax, op, dur) in enumerate(layers):
        flakes = "".join(
            f'<circle cx="{rnd.uniform(0, w):.1f}" cy="{rnd.uniform(0, h):.1f}" r="{rnd.uniform(rmin, rmax):.2f}"/>'
            for _ in range(count)
        )
        css.append(
            f".s{i}{{animation:fall{i} {dur}s linear infinite}}"
            f"@keyframes fall{i}{{from{{transform:translateY(-{h}px)}}to{{transform:translateY(0)}}}}"
            f".w{i}{{animation:sway{i} {dur * 0.6:.1f}s ease-in-out infinite alternate}}"
            f"@keyframes sway{i}{{from{{transform:translateX(-{6 + i * 4}px)}}to{{transform:translateX({6 + i * 4}px)}}}}"
        )
        out.append(
            f'<g class="w{i}" fill="{ICE}" opacity="{op}"><g class="s{i}">'
            f'<g>{flakes}</g><g transform="translate(0 {h})">{flakes}</g></g></g>'
        )
    return "".join(css), "".join(out)


def glow_filter(fid, std):
    return (
        f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="{std}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )


def blur_filter(fid, std):
    return f'<filter id="{fid}" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="{std}"/></filter>'


# silhueta (pés em 0,0, altura ~150) — o "fantasma" da foto de perfil
GHOST_BODY = (
    '<ellipse cx="0" cy="-138" rx="11" ry="13"/>'
    '<rect x="-4" y="-128" width="8" height="10"/>'
    '<path d="M-18,-120 C-26,-119 -27,-112 -27,-104 L-29,-64 C-29,-60 -23,-60 -23,-64 L-21,-96 '
    'L-20,-70 L-17,-2 C-17,1 -8,1 -8,-2 L-2,-66 L2,-66 L8,-2 C8,1 17,1 17,-2 L20,-70 L21,-96 '
    'L23,-64 C23,-60 29,-60 29,-64 L27,-104 C27,-112 26,-119 18,-120 Z"/>'
)


def ghost(x, y, scale=1.0):
    return f"""
<g transform="translate({x} {y}) scale({scale})">
  <ellipse cx="0" cy="4" rx="70" ry="12" fill="{CYAN}" opacity=".35" filter="url(#blur12)" class="breath"/>
  <g class="trail" fill="{DEEP}" opacity=".28" filter="url(#blur10)">
    <g transform="translate(26 -18) skewX(-14)">{GHOST_BODY}</g>
  </g>
  <g fill="{DEEP}" opacity=".75" filter="url(#blur18)" class="breath">{GHOST_BODY}</g>
  <g fill="#a5f3fc" opacity=".9" filter="url(#blur5)">{GHOST_BODY}</g>
  <g fill="#f4feff" filter="url(#blur1)">{GHOST_BODY}</g>
</g>"""


# ---------------------------------------------------------------------------
# HEADER — a loja de conveniência na neve
# ---------------------------------------------------------------------------
def header():
    W, H = 1200, 460
    rnd = random.Random(7)
    snow_css, snow = snow_layers(W, H, 11)

    stars = "".join(
        f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, 300):.0f}" r="{rnd.uniform(.4, 1.1):.2f}" '
        f'opacity="{rnd.uniform(.15, .6):.2f}"{" class=\"tw\" style=\"animation-delay:-" + str(rnd.randint(0, 6)) + "s\"" if rnd.random() < .25 else ""}/>'
        for _ in range(90)
    )
    # luzes distantes no horizonte (como na foto)
    far_lights = "".join(
        f'<circle cx="{x}" cy="{rnd.uniform(349, 353):.1f}" r="{r}" fill="{c}"/>'
        for x, r, c in [(30, 1.4, ICE), (52, 1.2, SKY), (88, 2.2, "#fde68a"), (96, 3, "#fff7d6"), (104, 2, "#fde68a"),
                        (150, 1.2, SKY), (176, 1.5, ICE), (230, 1, SKY), (262, 1.3, ICE)]
    )
    # pinheiros
    def pine(x, base, h, s=1.0):
        w = h * .42
        return (
            f'<g transform="translate({x} {base})">'
            f'<path d="M0,{-h} L{w * .55},{-h * .55} L{w * .3},{-h * .55} L{w * .75},{-h * .15} L{w * .4},{-h * .15} '
            f'L{w * .5},0 L{-w * .5},0 L{-w * .4},{-h * .15} L{-w * .75},{-h * .15} L{-w * .3},{-h * .55} L{-w * .55},{-h * .55} Z" fill="#0a1830"/>'
            f'<path d="M0,{-h} L{w * .28},{-h * .78} L{-w * .28},{-h * .78} Z" fill="#9cc7e6" opacity=".35"/>'
            f'</g>'
        )
    pines = "".join(pine(x, b, h) for x, b, h in [(690, 372, 120), (1150, 372, 140), (1185, 376, 96), (655, 375, 80)])

    # produtos nas prateleiras da vitrine
    def shelf_products(x0, x1, ys):
        g = []
        for y in ys:
            x = x0 + 4
            while x < x1 - 12:
                w = rnd.choice([7, 9, 11, 13])
                h = rnd.choice([10, 13, 16])
                c = rnd.choice(["#2b5f8a", "#3b82a6", "#1e4f7a", "#7aa7c7", "#c99a3b", "#4f7f9f"])
                g.append(f'<rect x="{x}" y="{y - h}" width="{w}" height="{h}" rx="1.5" fill="{c}" opacity=".55"/>')
                x += w + rnd.choice([2, 3, 4])
            g.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="3" fill="#1b3a5c" opacity=".6"/>')
        return "".join(g)

    footprints = []
    for i in range(16):
        t = i / 15
        x = 455 + (890 - 455) * t
        y = 418 + (398 - 418) * t + (3 if i % 2 else -3)
        footprints.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="4.5" ry="2" fill="#1a3557" opacity="{.35 + .4 * t:.2f}"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Isaac Gonçalves — uma loja de conveniência acesa numa noite de neve">
<title>isaac gonçalves — ghost mart, open 24h</title>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG0}"/><stop offset=".6" stop-color="#060d1d"/><stop offset="1" stop-color="#0b1a33"/>
  </linearGradient>
  <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#16304f"/><stop offset=".25" stop-color="#0d2038"/><stop offset="1" stop-color="#050b16"/>
  </linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#eafcff"/><stop offset="1" stop-color="#a9def3"/>
  </linearGradient>
  <linearGradient id="cone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{ICE}" stop-opacity=".35"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="spill" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#bff4ff" stop-opacity=".45"/><stop offset="1" stop-color="#bff4ff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vig" cx=".5" cy=".45" r=".75">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/>
  </radialGradient>
  {glow_filter("neon", 3)}{glow_filter("soft", 1.5)}
  {blur_filter("blur1", 1.2)}{blur_filter("blur5", 5)}{blur_filter("blur10", 10)}{blur_filter("blur12", 12)}{blur_filter("blur18", 18)}
  <clipPath id="typeclip"><rect x="60" y="168" height="30" width="0">
    <animate attributeName="width" values="0;520;520;0" keyTimes="0;.45;.92;1" dur="9s" repeatCount="indefinite" calcMode="discrete"/>
  </rect></clipPath>
</defs>
<style>
  text{{font-family:{FONT}}}
  .tw{{animation:tw 4s ease-in-out infinite}}@keyframes tw{{50%{{opacity:.05}}}}
  .sign{{animation:flick 7s steps(1) infinite}}
  @keyframes flick{{0%,100%{{opacity:1}}61%{{opacity:.35}}62%{{opacity:1}}64%{{opacity:.2}}65%{{opacity:1}}}}
  .open{{animation:blink 2.4s ease-in-out infinite}}@keyframes blink{{50%{{opacity:.35}}}}
  .lamp{{animation:lamp 11s steps(1) infinite}}@keyframes lamp{{0%,100%{{opacity:1}}83%{{opacity:.4}}84%{{opacity:1}}86%{{opacity:.55}}87%{{opacity:1}}}}
  .breath{{animation:breath 5s ease-in-out infinite}}@keyframes breath{{50%{{opacity:.45}}}}
  .trail{{animation:trail 6s ease-in-out infinite alternate}}@keyframes trail{{to{{transform:translate(10px,-6px);opacity:.12}}}}
  .cur{{animation:cur 1s steps(1) infinite}}@keyframes cur{{50%{{opacity:0}}}}
  .steam{{animation:steam 3.5s ease-out infinite}}@keyframes steam{{0%{{transform:translateY(0);opacity:0}}30%{{opacity:.6}}100%{{transform:translateY(-14px);opacity:0}}}}
  .screen{{animation:screen 3s ease-in-out infinite}}@keyframes screen{{50%{{opacity:.7}}}}
  {snow_css}
  {REDUCED}
</style>

<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g fill="{ICE}">{stars}</g>

<!-- horizonte -->
<path d="M0,352 C160,344 300,350 460,346 C620,342 760,350 900,345 C1020,341 1120,348 1200,344 L1200,362 L0,362 Z" fill="#060c19"/>
<g filter="url(#soft)">{far_lights}</g>
<ellipse cx="96" cy="351" rx="40" ry="5" fill="#fde68a" opacity=".12" filter="url(#blur5)"/>

{pines}

<!-- chão de neve -->
<path d="M0,372 C200,362 420,370 640,366 C860,362 1010,370 1200,364 L1200,{H} L0,{H} Z" fill="url(#ground)"/>
<path d="M0,372 C200,362 420,370 640,366 C860,362 1010,370 1200,364" fill="none" stroke="#9cc7e6" stroke-opacity=".25" stroke-width="1.5"/>

<!-- poste -->
<g>
  <polygon points="626,240 652,240 730,420 548,420" fill="url(#cone)" class="lamp"/>
  <rect x="604" y="236" width="5" height="160" fill="#0a1424"/>
  <path d="M606,238 Q610,226 640,228" fill="none" stroke="#0a1424" stroke-width="4"/>
  <rect x="628" y="226" width="24" height="8" rx="2" fill="#0a1424"/>
  <ellipse cx="640" cy="236" rx="10" ry="3" fill="{ICE}" filter="url(#neon)" class="lamp"/>
  <ellipse cx="640" cy="414" rx="80" ry="10" fill="{ICE}" opacity=".12" filter="url(#blur10)" class="lamp"/>
</g>

<!-- luz da loja sobre a neve -->
<ellipse cx="925" cy="408" rx="330" ry="46" fill="url(#spill)"/>

<!-- loja -->
<g>
  <rect x="720" y="190" width="410" height="204" fill="#0a1426"/>
  <rect x="720" y="190" width="410" height="204" fill="#0e1d36" opacity=".6"/>
  <rect x="708" y="180" width="434" height="14" rx="2" fill="#070f1e"/>
  <path d="M706,182 C706,170 1144,170 1144,182 L1144,186 C1120,186 1118,196 1110,196 C1102,196 1100,186 1060,186
           C1040,186 1040,192 1032,192 C1024,192 1024,186 940,186 C900,186 898,198 890,198 C882,198 880,186 800,186
           C770,186 768,193 760,193 C752,193 750,186 706,186 Z" fill="#d9eef9"/>

  <!-- letreiro -->
  <rect x="790" y="204" width="270" height="44" rx="4" fill="#050b16" stroke="#123a5c"/>
  <g class="sign">
    <text x="925" y="234" text-anchor="middle" font-size="24" font-weight="700" letter-spacing="6" fill="{CYAN}" filter="url(#neon)">GHOST MART</text>
  </g>
  <text x="1080" y="232" font-size="11" fill="{WARM}" opacity=".85" filter="url(#soft)">24h</text>

  <!-- vitrine esquerda -->
  <rect x="738" y="262" width="146" height="112" fill="url(#glass)"/>
  {shelf_products(742, 880, [292, 322, 352])}
  <rect x="738" y="262" width="146" height="112" fill="none" stroke="#08111f" stroke-width="5"/>
  <line x1="811" y1="262" x2="811" y2="374" stroke="#08111f" stroke-width="3"/>
  <rect x="734" y="372" width="154" height="5" rx="2" fill="#d9eef9"/>

  <!-- porta -->
  <rect x="896" y="262" width="62" height="132" fill="url(#glass)"/>
  {shelf_products(900, 954, [300, 336])}
  <rect x="896" y="262" width="62" height="132" fill="none" stroke="#08111f" stroke-width="5"/>
  <rect x="946" y="320" width="3" height="18" fill="#08111f"/>
  <g class="open"><rect x="904" y="350" width="36" height="14" rx="2" fill="#1a0f02"/>
  <text x="922" y="360.5" text-anchor="middle" font-size="9" font-weight="700" fill="{WARM}" filter="url(#soft)">OPEN</text></g>

  <!-- vitrine direita: o caixa (o programador do turno da noite) -->
  <rect x="970" y="262" width="146" height="112" fill="url(#glass)"/>
  {shelf_products(974, 1112, [292])}
  <circle cx="1068" cy="318" r="9" fill="#0b1830"/>
  <path d="M1052,346 C1052,330 1084,330 1084,346 Z" fill="#0b1830"/>
  <rect x="970" y="344" width="146" height="30" fill="#0b1830"/>
  <path d="M1030,344 L1036,330 L1060,330 L1056,344 Z" fill="#132a4a"/>
  <rect x="1036" y="331" width="22" height="12" fill="{CYAN}" opacity=".9" class="screen" filter="url(#soft)"/>
  <rect x="1004" y="336" width="8" height="8" rx="1" fill="#e9d7b5"/>
  <path d="M1006,333 q2,-4 0,-8 M1010,333 q2,-4 0,-8" stroke="#e9d7b5" stroke-width="1" fill="none" class="steam"/>
  <rect x="970" y="262" width="146" height="112" fill="none" stroke="#08111f" stroke-width="5"/>
  <line x1="1043" y1="262" x2="1043" y2="330" stroke="#08111f" stroke-width="3"/>
  <rect x="966" y="372" width="154" height="5" rx="2" fill="#d9eef9"/>

  <!-- brilho das vitrines -->
  <rect x="738" y="262" width="378" height="112" fill="#bff4ff" opacity=".18" filter="url(#blur18)"/>
</g>

<!-- pegadas da porta até o fantasma -->
<g>{"".join(footprints)}</g>

{ghost(430, 420, .95)}

<!-- texto -->
<g>
  <text x="60" y="96" font-size="15" fill="{MUTED}" letter-spacing="3">// night shift · vacaria, rs</text>
  <text x="58" y="146" font-size="46" font-weight="700" fill="{ICE}" filter="url(#soft)">isaac gonçalves</text>
  <g clip-path="url(#typeclip)">
    <text x="60" y="188" font-size="17" fill="{SKY}"><tspan fill="{CYAN}">$</tspan> full stack, game dev &amp; designer — building at night</text>
  </g>
  <rect x="60" y="174" width="10" height="18" fill="{CYAN}" class="cur" opacity=".8">
    <animate attributeName="x" values="60;580;580;60" keyTimes="0;.45;.92;1" dur="9s" repeatCount="indefinite" calcMode="discrete"/>
  </rect>
</g>

{snow}
<rect width="{W}" height="{H}" fill="url(#vig)" pointer-events="none"/>
</svg>"""
    # a animação "discrete" acima não digita letra por letra; substitui por uma versão em passos
    chars = len("$ full stack, game dev & designer — building at night")
    cw = 17 * 0.6
    vals = [f"{i * cw:.1f}" for i in range(chars + 1)]
    n = len(vals)
    hold = 14
    seq = vals + [vals[-1]] * hold + ["0"]
    keys = ";".join(f"{i / (len(seq) - 1):.4f}" for i in range(len(seq)))
    svg = svg.replace(
        'values="0;520;520;0" keyTimes="0;.45;.92;1" dur="9s" repeatCount="indefinite" calcMode="discrete"/>\n  </rect></clipPath>',
        f'values="{";".join(seq)}" keyTimes="{keys}" dur="9s" repeatCount="indefinite" calcMode="discrete"/>\n  </rect></clipPath>',
    )
    xs = [f"{60 + float(v) + 2:.1f}" for v in seq]
    svg = svg.replace(
        'values="60;580;580;60" keyTimes="0;.45;.92;1"',
        f'values="{";".join(xs)}" keyTimes="{keys}"',
    )
    (OUT / "header.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# PRATELEIRA — linguagens e ferramentas   (EDITE AQUI)
# ---------------------------------------------------------------------------
LANGS = [
    # (rótulo grande, nome, cor, etiqueta de preço)
    ("PHP", "php 8", "#8b93c9", "backend · daily"),
    ("JS", "javascript", "#e8cf4a", "vanilla, no fw"),
    ("C#", "c#", "#a68be0", "gameplay · unity"),
    ("TS", "typescript", "#4f8fd6", "electron · react"),
    ("SQL", "mariadb/mysql", "#4fa3b8", "multi-tenant data"),
    ("</>", "html + css", "#e58a6a", "pixel-perfect UI"),
]
TOOLS = [
    ("U6", "unity 6", "#cbd5e1", "scriptableobjects"),
    ("GO", "godot", "#6ea8d8", "+ tiled maps"),
    ("GIT", "git", "#e8795a", "small commits"),
    ("PW", "playwright", "#5fb96f", "screenshot tests"),
    ("FG", "figma", "#c08ae8", "before code"),
    ("PX", "aseprite", "#e0a5c4", "pixel art"),
]


def shelf():
    W, H = 1200, 470
    rnd = random.Random(3)
    snow_css, _ = snow_layers(W, H, 5)
    items = []

    def product(i, row, label, name, color, tag, top):
        cx = 120 + i * 192
        delay = (row * 6 + i) * .12
        if row == 0:  # caixas
            w, h = 112, 118
            x, y = cx - w / 2, top - h
            body = (
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0b1629" stroke="{color}" stroke-opacity=".55"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="6" fill="{color}" opacity=".85"/>'
                f'<rect x="{x}" y="{y + 12}" width="{w}" height="6" fill="{color}" opacity=".85"/>'
                f'<text x="{cx}" y="{y + 13}" text-anchor="middle" font-size="9" fill="#06101f" font-weight="700" letter-spacing="1.5">GHOST MART</text>'
                f'<text x="{cx}" y="{y + 70}" text-anchor="middle" font-size="32" font-weight="700" fill="{color}" filter="url(#soft)">{esc(label)}</text>'
                f'<text x="{cx}" y="{y + 98}" text-anchor="middle" font-size="12" fill="#b9d6ee">{esc(name)}</text>'
            )
        else:  # latas
            w, h = 96, 104
            x, y = cx - w / 2, top - h
            body = (
                f'<rect x="{x}" y="{y + 6}" width="{w}" height="{h - 6}" rx="8" fill="#0b1629" stroke="{color}" stroke-opacity=".5"/>'
                f'<ellipse cx="{cx}" cy="{y + 7}" rx="{w / 2}" ry="7" fill="#132744" stroke="{color}" stroke-opacity=".5"/>'
                f'<rect x="{x}" y="{y + 32}" width="{w}" height="44" fill="{color}" opacity=".16"/>'
                f'<text x="{cx}" y="{y + 63}" text-anchor="middle" font-size="24" font-weight="700" fill="{color}" filter="url(#soft)">{esc(label)}</text>'
                f'<text x="{cx}" y="{y + 94}" text-anchor="middle" font-size="12" fill="#b9d6ee">{esc(name)}</text>'
            )
        glow = f'<ellipse cx="{cx}" cy="{top - 40}" rx="70" ry="50" fill="{color}" opacity=".10" filter="url(#blur18)"/>'
        tagw = max(96, len(tag) * 7 + 16)
        tagel = (
            f'<rect x="{cx - tagw / 2}" y="{top + 16}" width="{tagw}" height="20" rx="3" fill="#dff3ff" opacity=".92"/>'
            f'<text x="{cx}" y="{top + 30}" text-anchor="middle" font-size="11" fill="#0a1a30">{esc(tag)}</text>'
        )
        items.append(f'<g class="on" style="animation-delay:{delay:.2f}s">{glow}<g class="bob" style="animation-delay:-{rnd.uniform(0, 6):.1f}s">{body}</g>{tagel}</g>')

    tops = [222, 412]
    for i, p in enumerate(LANGS):
        product(i, 0, *p, tops[0])
    for i, p in enumerate(TOOLS):
        product(i, 1, *p, tops[1])

    boards = "".join(
        f'<rect x="20" y="{t}" width="{W - 40}" height="14" fill="#13243d"/>'
        f'<rect x="20" y="{t}" width="{W - 40}" height="3" fill="#2d4f75"/>'
        f'<rect x="20" y="{t + 14}" width="{W - 40}" height="10" fill="#060c18"/>'
        for t in tops
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Linguagens: PHP, JavaScript, C#, GDScript, SQL, HTML/CSS. Ferramentas: Unity 6, Godot, Git, Playwright, Figma, Aseprite.">
<title>aisle 02 — languages &amp; tools</title>
<defs>
  <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1426"/><stop offset="1" stop-color="#040811"/></linearGradient>
  <linearGradient id="tube" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ICE}" stop-opacity=".22"/><stop offset="1" stop-color="{ICE}" stop-opacity="0"/></linearGradient>
  {glow_filter("soft", 1.4)}{glow_filter("neon", 3)}{blur_filter("blur18", 18)}
</defs>
<style>
  text{{font-family:{FONT}}}
  .on{{opacity:0;animation:on .9s steps(3) forwards}}@keyframes on{{0%{{opacity:0}}40%{{opacity:.6}}55%{{opacity:.15}}100%{{opacity:1}}}}
  .bob{{animation:bob 6s ease-in-out infinite}}@keyframes bob{{50%{{transform:translateY(-2px)}}}}
  .tubeL{{animation:tube 9s steps(1) infinite}}@keyframes tube{{0%,100%{{opacity:1}}71%{{opacity:.3}}72%{{opacity:1}}74%{{opacity:.5}}75%{{opacity:1}}}}
  {REDUCED}
  @media (prefers-reduced-motion: reduce){{.on{{opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="url(#wall)"/>
<g class="tubeL">
  <rect x="300" y="14" width="600" height="5" rx="2.5" fill="{ICE}" filter="url(#neon)"/>
  <polygon points="300,19 900,19 1100,250 100,250" fill="url(#tube)"/>
</g>
<text x="40" y="44" font-size="13" fill="{MUTED}" letter-spacing="2">AISLE 02</text>
<text x="40" y="66" font-size="18" fill="{ICE}" font-weight="700">languages &amp; tools</text>
<text x="{W - 40}" y="44" font-size="12" fill="{MUTED}" text-anchor="end">what I actually reach for</text>
<text x="{W - 40}" y="66" font-size="12" fill="{WARM}" opacity=".8" text-anchor="end">restocked nightly</text>
{boards}
{"".join(items)}
</svg>"""
    (OUT / "shelf.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# CARDS DE PROJETO   (EDITE AQUI)
# ---------------------------------------------------------------------------
PROJECTS = [
    dict(
        file="project-harmony.svg", aisle="01", title="Harmony", status="done", label="RELEASED · OPEN SOURCE",
        wide=True, eq=True,
        lines=["An offline music player with a cinematic live-stage visualizer — six Show Packs,",
               "a custom Web Audio engine (10-band EQ, crossfade, gapless) and synced + karaoke lyrics.",
               "Open source (MIT). Runs on Windows and Linux."],
        stack=["TypeScript", "Electron", "React", "Web Audio", "SQLite"],
    ),
    dict(
        file="project-ghostguard.svg", aisle="02", title="GhostGuard Manager", status="active", label="ACTIVE DEVELOPMENT",
        lines=["Multi-tenant SaaS ERP for small businesses —",
               "barbershops first. Custom MVC framework,",
               "tiered billing, full tenant isolation."],
        stack=["PHP 8", "MariaDB", "Custom MVC", "Vanilla JS"],
    ),
    dict(
        file="project-towerdefense.svg", aisle="03", title="Tower Defense — Anime Ed.", status="wip", label="IN PROGRESS",
        lines=["2D tower defense in Unity 6 with a full summon",
               "system. ScriptableObjects, event-driven",
               "architecture (Ryan Hipple), SOLID."],
        stack=["Unity 6", "C#", "ScriptableObjects"],
    ),
    dict(
        file="project-pokedex.svg", aisle="04", title="Interactive Pokédex", status="done", label="COMPLETE",
        lines=["A physical-device Pokédex in pure HTML/CSS/JS:",
               "animated sprites via PokéAPI, storage, and",
               "full keyboard & D-pad navigation."],
        stack=["HTML", "CSS", "JavaScript", "PokéAPI"],
    ),
    dict(
        file="project-minecraft.svg", aisle="05", title="Minecraft Session Challenges", status="done", label="COMPLETE",
        lines=["Gamified group sessions: countdown timer,",
               "severity-based penalties, per-session bingo,",
               "pixel-art UI, all saved in localStorage."],
        stack=["HTML", "CSS", "JavaScript"],
    ),
]
STATUS_COLOR = {"active": CYAN, "wip": WARM, "done": "#86efac"}


def eq_bars(x0, base, w, h, rnd):
    """equalizador animado (o visualizer do Harmony)"""
    n, out = 24, []
    bw = w / n
    for i in range(n):
        hh = h * rnd.uniform(.45, 1)
        out.append(
            f'<rect class="eq" x="{x0 + i * bw:.1f}" y="{base - hh:.1f}" width="{bw * .62:.1f}" height="{hh:.1f}" rx="2" '
            f'fill="url(#eqg)" style="animation-duration:{rnd.uniform(.45, 1.3):.2f}s;animation-delay:-{rnd.uniform(0, 1.3):.2f}s"/>'
        )
    return (f'<defs><linearGradient id="eqg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{DEEP}"/>'
            f'<stop offset=".7" stop-color="{CYAN}"/><stop offset="1" stop-color="{ICE}"/></linearGradient></defs>'
            f'<g filter="url(#soft)" opacity=".9">{"".join(out)}</g>')


def project_card(p):
    W, H = (1180 if p.get("wide") else 580), 250
    rnd = random.Random(p["aisle"])
    color = STATUS_COLOR[p["status"]]
    bars = []
    x = W - 150
    while x < W - 34 and not p.get("eq"):
        bw = rnd.choice([1, 1, 2, 3])
        bars.append(f'<rect x="{x}" y="{H - 52}" width="{bw}" height="26" fill="{ICE}" opacity=".55"/>')
        x += bw + rnd.choice([1, 2, 2, 3])
    chips, cx = [], 30
    for s in p["stack"]:
        w = len(s) * 7.2 + 18
        chips.append(
            f'<rect x="{cx}" y="{H - 50}" width="{w:.0f}" height="22" rx="11" fill="#0f2140" stroke="#24476e"/>'
            f'<text x="{cx + w / 2:.0f}" y="{H - 35}" text-anchor="middle" font-size="11.5" fill="#b9d6ee">{esc(s)}</text>'
        )
        cx += w + 8
    lines = "".join(
        f'<text x="30" y="{122 + i * 22}" font-size="14" fill="#a9c4dc">{esc(l)}</text>' for i, l in enumerate(p["lines"])
    )
    cap = (
        f'M8,14 C8,4 {W - 8},4 {W - 8},14 L{W - 8},17 C{W - 40},17 {W - 44},26 {W - 52},26 C{W - 60},26 {W - 62},17 {W * .6:.0f},17 '
        f'C{W * .45:.0f},17 {W * .44:.0f},23 {W * .42:.0f},23 C{W * .40:.0f},23 {W * .39:.0f},17 120,17 C90,17 88,24 80,24 C72,24 70,17 8,17 Z'
    )
    snow_css, snow = snow_layers(W, H, int(p["aisle"]), layers=((22, .8, 1.4, .35, 18), (8, 1.4, 2.0, .5, 12)))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(p['title'])} — {esc(' '.join(p['lines']))}">
<title>{esc(p['title'])}</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1730"/><stop offset="1" stop-color="#040913"/></linearGradient>
  {glow_filter("soft", 1.5)}<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <clipPath id="c"><rect x="8" y="10" width="{W - 16}" height="{H - 18}" rx="12"/></clipPath>
</defs>
<style>
  text{{font-family:{FONT}}}
  .dot{{animation:pulse 2.2s ease-in-out infinite}}@keyframes pulse{{50%{{opacity:.25}}}}
  .halo{{animation:halo 5s ease-in-out infinite}}@keyframes halo{{50%{{opacity:.05}}}}
  .eq{{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1s ease-in-out infinite alternate}}
  @keyframes eq{{0%{{transform:scaleY(.15)}}100%{{transform:scaleY(1)}}}}
  {snow_css}
  {REDUCED}
</style>
<rect x="8" y="10" width="{W - 16}" height="{H - 18}" rx="12" fill="url(#bg)" stroke="#1d3a5e"/>
<g clip-path="url(#c)">
  <circle cx="{W - 70}" cy="50" r="70" fill="{color}" opacity=".12" filter="url(#bl)" class="halo"/>
  {snow}
</g>
<path d="{cap}" fill="#d9eef9" opacity=".9"/>
<text x="30" y="56" font-size="12" fill="{MUTED}" letter-spacing="2">AISLE {p['aisle']}</text>
<circle cx="{W - 30 - len(p['label']) * 7.6 - 12:.0f}" cy="52" r="4" fill="{color}" class="dot" filter="url(#soft)"/>
<text x="{W - 30}" y="56" font-size="11" fill="{color}" letter-spacing="1" text-anchor="end">{p['label']}</text>
<text x="30" y="88" font-size="23" font-weight="700" fill="{ICE}" filter="url(#soft)">{esc(p['title'])}</text>
{lines}
{"".join(chips)}
{"".join(bars)}
{eq_bars(W - 290, H - 28, 250, 120, rnd) if p.get("eq") else ""}
</svg>"""
    (OUT / p["file"]).write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# CUPOM FISCAL — o que estou aprendendo / o que tem na sacola   (EDITE AQUI)
# ---------------------------------------------------------------------------
RECEIPT_LEARNING = [
    ("adv. php architecture", 8),
    ("saas security hardening", 6),
    ("unity ecs / dots", 5),
    ("godot 4 tilemaps", 4),
    ("cloud & devops", 3),
]
RECEIPT_BAG = [
    ("1x hot coffee", "always"),
    ("1x architecture sketch", "first"),
    ("1x playwright screenshot", "pass"),
    ("1x bug from yesterday", "fixed"),
]


def receipt():
    W = 420
    rows = []
    y = 70

    def line(txt, size=13, fill="#1b2a3d", anchor="start", x=None, weight="400"):
        nonlocal y
        xx = x if x is not None else (W / 2 if anchor == "middle" else 36)
        rows.append(f'<text x="{xx}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(txt)}</text>')

    def dash():
        nonlocal y
        rows.append(f'<line x1="36" y1="{y}" x2="{W - 36}" y2="{y}" stroke="#7b8796" stroke-dasharray="4 4"/>')
        y += 24

    line("GHOST MART", 20, anchor="middle", weight="700"); y += 20
    line("open 24h · vacaria, rs", 12, "#4b5b70", "middle"); y += 18
    line("terminal 03 · 03:12 AM", 12, "#4b5b70", "middle"); y += 20
    dash()
    line("CURRENTLY LEARNING", 12, "#4b5b70", weight="700"); y += 24
    for name, lvl in RECEIPT_LEARNING:
        line(name, 13); y += 16
        bar = "".join(
            f'<rect x="{36 + i * 18}" y="{y - 10}" width="14" height="8" fill="{"#1b2a3d" if i < lvl else "#c9d2dc"}"/>'
            for i in range(10)
        )
        rows.append(bar)
        line(f"{lvl * 10}%", 12, "#4b5b70", "end", x=W - 36); y += 22
    dash()
    line("IN THE BAG TONIGHT", 12, "#4b5b70", weight="700"); y += 24
    for a, b in RECEIPT_BAG:
        line(a, 13); line(b, 13, anchor="end", x=W - 36); y += 22
    dash()
    line("TOTAL", 15, weight="700"); line("still learning", 15, anchor="end", x=W - 36, weight="700"); y += 34
    line("thank you, come back", 12, "#4b5b70", "middle"); y += 18
    line("after midnight.", 12, "#4b5b70", "middle"); y += 22
    rnd = random.Random(42)
    x = 70
    bars = []
    while x < W - 70:
        bw = rnd.choice([1, 2, 2, 3, 4])
        bars.append(f'<rect x="{x}" y="{y}" width="{bw}" height="40" fill="#1b2a3d"/>')
        x += bw + rnd.choice([1, 2, 3])
    rows.append("".join(bars))
    y += 58
    line("isaac-ghostlolp", 11, "#4b5b70", "middle"); y += 26

    H = y
    # borda serrilhada
    teeth = " ".join(f"L{x},{H - (6 if (x // 10) % 2 else 0)}" for x in range(W - 20, 19, -10))
    paper = f"M20,14 L{W - 20},14 L{W - 20},{H} {teeth} L20,{H} Z"
    total = H + 30
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total}" width="{W}" height="{total}" role="img" aria-label="Cupom: aprendendo arquitetura PHP avançada, segurança SaaS, Unity DOTS, Godot 4 tilemaps, cloud e devops.">
<title>receipt — currently learning</title>
<defs>
  <linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef6fb"/><stop offset="1" stop-color="#dbe8f2"/></linearGradient>
  <filter id="sh" x="-20%" y="-10%" width="140%" height="130%"><feGaussianBlur stdDeviation="10"/></filter>
  <clipPath id="print"><rect x="0" y="0" width="{W}" height="{total}" class="roll"/></clipPath>
</defs>
<style>
  text{{font-family:{FONT}}}
  .roll{{transform:translateY(-{total}px);animation:roll 3.2s steps(40) .3s forwards}}
  @keyframes roll{{to{{transform:translateY(0)}}}}
  @media (prefers-reduced-motion: reduce){{.roll{{animation:none;transform:none}}}}
</style>
<g clip-path="url(#print)">
  <path d="{paper}" fill="{CYAN}" opacity=".18" filter="url(#sh)"/>
  <path d="{paper}" fill="url(#p)"/>
  {"".join(rows)}
</g>
</svg>"""
    (OUT / "receipt.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------------------
# DIVISOR e RODAPÉ
# ---------------------------------------------------------------------------
def divider():
    W, H = 1200, 40
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="divisor">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset=".5" stop-color="{SKY}" stop-opacity=".55"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient>
{glow_filter("g", 3)}</defs>
<style>.f{{animation:f 7s ease-in-out infinite}}@keyframes f{{50%{{transform:translateY(5px);opacity:.3}}}}{REDUCED}</style>
<rect x="0" y="{H / 2}" width="{W}" height="1" fill="url(#l)"/>
<circle cx="{W / 2}" cy="{H / 2 + .5}" r="2.5" fill="{ICE}" filter="url(#g)"/>
<g fill="{ICE}"><circle class="f" cx="{W / 2 - 60}" cy="12" r="1.3" opacity=".6"/><circle class="f" style="animation-delay:-2s" cx="{W / 2 + 48}" cy="10" r="1" opacity=".5"/><circle class="f" style="animation-delay:-4s" cx="{W / 2 + 120}" cy="14" r="1.4" opacity=".4"/></g>
</svg>"""
    (OUT / "divider.svg").write_text(svg, encoding="utf-8")


def footer():
    W, H = 1200, 240
    snow_css, snow = snow_layers(W, H, 21, layers=((50, .8, 1.5, .5, 20), (20, 1.5, 2.4, .8, 13)))
    prints = "".join(
        f'<ellipse cx="{560 - i * 38}" cy="{196 + i * 3 + (3 if i % 2 else -3)}" rx="{4.5 + i * .3:.1f}" ry="2.2" fill="#1a3557" opacity="{.6 - i * .04:.2f}"/>'
        for i in range(12)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="as luzes da loja continuam acesas ao longe">
<title>the lights stay on</title>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="#0b1a33"/></linearGradient>
  <linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16304f"/><stop offset="1" stop-color="#050b16"/></linearGradient>
  {glow_filter("soft", 1.5)}<filter id="b" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8"/></filter>
</defs>
<style>
  text{{font-family:{FONT}}}
  .shop{{animation:shop 6s ease-in-out infinite}}@keyframes shop{{50%{{opacity:.7}}}}
  {snow_css}{REDUCED}
</style>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<path d="M0,176 C300,168 600,178 900,170 C1020,167 1120,172 1200,170 L1200,{H} L0,{H} Z" fill="url(#gr)"/>
<path d="M0,176 C300,168 600,178 900,170 C1020,167 1120,172 1200,170" fill="none" stroke="#9cc7e6" stroke-opacity=".22"/>
<!-- a loja, pequena, ao longe -->
<g class="shop" transform="translate(600 172)">
  <ellipse cx="0" cy="2" rx="90" ry="10" fill="#bff4ff" opacity=".25" filter="url(#b)"/>
  <rect x="-34" y="-30" width="68" height="30" fill="#0a1426"/>
  <rect x="-36" y="-33" width="72" height="4" fill="#d9eef9"/>
  <rect x="-28" y="-18" width="22" height="15" fill="#d6f5ff"/><rect x="-3" y="-18" width="8" height="18" fill="#d6f5ff"/><rect x="8" y="-18" width="20" height="15" fill="#d6f5ff"/>
  <rect x="-20" y="-28" width="40" height="7" fill="{CYAN}" opacity=".9" filter="url(#soft)"/>
</g>
{prints}
<text x="{W / 2}" y="222" text-anchor="middle" font-size="13" fill="{MUTED}" letter-spacing="2">the lights stay on · see you after midnight</text>
{snow}
</svg>"""
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    header()
    shelf()
    for p in PROJECTS:
        project_card(p)
    receipt()
    divider()
    footer()
    print("ok →", ", ".join(sorted(f.name for f in OUT.glob("*.svg"))))
