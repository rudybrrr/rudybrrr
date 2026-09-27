"""Builds README.md and the few animated figures in assets/ for the profile.

The README is a model card (the Hugging Face kind), mostly plain markdown. The figures are the
machine's voice: Martian Mono turned into outlines, tokenizer-chip colours, GitHub's own ink so
they sit with the text around them. Each comes light/dark x wide/phone; <picture> picks one.

Run: npm i && python3 src/build.py   (needs fonttools, brotli, uharfbuzz)
"""

import io
import math
import re
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from content import *  # noqa: F403 (it's all copy)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
FONT = ROOT / 'node_modules/@fontsource-variable/martian-mono/files/martian-mono-latin-standard-normal.woff2'

EASE = 'cubic-bezier(0.16, 1, 0.3, 1)'
THEMES = {
    'light': {'ink': '#1f2328', 'muted': '#59636e', 'rule': '#d1d9e0', 'live': '#1a7f37',
              'chip': ['#e4dcfb', '#cdeed7', '#fbe8b0', '#fbd6cf', '#d3e4fb'],
              'deep': ['#6e56cf', '#2f9e5a', '#b98900', '#d4523f', '#3b7de0']},
    'dark': {'ink': '#f0f6fc', 'muted': '#9198a1', 'rule': '#3d444d', 'live': '#3fb950',
             'chip': ['#3b2f66', '#1c4a32', '#54440f', '#5c2828', '#1c3a61'],
             'deep': ['#a48bfa', '#56d38a', '#e7c14a', '#f28b7a', '#78a9ff']},
}

# --- type: Martian Mono at a few points of its weight/width axes ---------------------------

STYLES = {'display': {'wght': 560, 'wdth': 112.5}, 'body': {'wght': 400, 'wdth': 100},
          'label': {'wght': 430, 'wdth': 87.5}}
_tt = TTFont(FONT)
_tt.flavor = None  # HarfBuzz reads TTF, not WOFF2
_ttf = io.BytesIO()
_tt.save(_ttf)
_upem = _tt['head'].unitsPerEm
_order = _tt.getGlyphOrder()
_blob = hb.Blob(_ttf.getvalue())
_sets, _hb, _paths = {}, {}, {}


def _style(s):
    if s not in _sets:
        _sets[s] = _tt.getGlyphSet(location=STYLES[s])
        f = hb.Font(hb.Face(_blob))
        f.set_variations(STYLES[s])
        _hb[s] = f
    return _sets[s], _hb[s]


def glyph_path(s, gid):
    if (s, gid) not in _paths:
        pen = SVGPathPen(_style(s)[0])
        _style(s)[0][_order[gid]].draw(pen)
        _paths[s, gid] = pen.getCommands()
    return _paths[s, gid]


def shape(text, size, s='body'):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(_style(s)[1], buf)
    k, x, out = size / _upem, 0.0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((info.codepoint, x + pos.x_offset * k))
        x += pos.x_advance * k
    return out, x


def measure(text, size, s='body'):
    return shape(text, size, s)[1]


def wrap(text, size, width, s='body'):
    lines, line = [], ''
    for word in text.split(' '):
        test = f'{line} {word}'.strip()
        if line and measure(test, size, s) > width:
            lines.append(line)
            line = word
        else:
            line = test
    return lines + [line] if line else lines


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


class Doc:
    """One SVG. Glyphs are defined once and placed with <use>."""

    def __init__(self, w, title):
        self.w, self.h, self.title = w, 0, title
        self.used, self.css, self.defs, self.body = set(), [], [], []

    def text(self, s, x, y, size, fill, style='body', anchor='start', attrs=''):
        run, width = shape(s, size, style)
        x -= {'start': 0, 'middle': width / 2, 'end': width}[anchor]
        k = size / _upem
        uses = []
        for gid, gx in run:
            if glyph_path(style, gid):
                self.used.add((style, gid))
                uses.append(f'<use href="#{style[0]}{gid}" x="{(x + gx) / k:.1f}"/>')
        self.body.append(f'<g fill="{fill}" transform="translate(0 {y:.2f}) scale({k:.5f} {-k:.5f})" {attrs}>{"".join(uses)}</g>')
        return width

    def add(self, svg):
        self.body.append(svg)

    def save(self, name):
        glyphs = ''.join(f'<path id="{s[0]}{g}" d="{glyph_path(s, g)}"/>' for s, g in sorted(self.used))
        css = ''.join(self.css) + '@media (prefers-reduced-motion:reduce){*{animation:none!important}}'
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h:.0f}" viewBox="0 0 {self.w} {self.h:.0f}" '
               f'role="img"><title>{esc(self.title)}</title><style>{css}</style><defs>{glyphs}{"".join(self.defs)}</defs>'
               f'{"".join(self.body)}</svg>')
        ASSETS.mkdir(exist_ok=True)
        (ASSETS / f'{name}.svg').write_text(svg)


FADE = f'@keyframes in{{from{{opacity:0;transform:translateY(6px)}}}}.in{{animation:in .7s {EASE} both}}'
PING = ('@keyframes ping{75%,100%{transform:scale(2.6);opacity:0}}'
        '.ping{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.8s cubic-bezier(0,0,.2,1) infinite}')


def at(t):
    return f'class="in" style="animation-delay:{t:.2f}s"'


def live_dot(d, cx, cy, color, r=4):
    d.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>'
          f'<circle class="ping" cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>')


# --- figures ----------------------------------------------------------------------------

def hero(th, W):
    """An inference widget: the name split into tokens, then one line streamed out token by token."""
    t = THEMES[th]
    narrow = W < 600
    pad = 20 if narrow else 30
    d = Doc(W, f'Rudhresh R., tokenized. Asked "{PROMPT}", the card answers: {ANSWER}')
    d.css += [FADE, PING,
              f'@keyframes chip{{from{{opacity:0;transform:scale(.86)}}}}.chip{{transform-box:fill-box;transform-origin:50% 60%;animation:chip .5s {EASE} both}}',
              '@keyframes tok{from{opacity:0}}.tok{animation:tok .12s linear both}',
              '@keyframes flash{0%{opacity:.95}100%{opacity:0}}.flash{opacity:0;animation:flash .7s ease-out both}',
              '@keyframes blink{0%,50%{opacity:1}50.01%,100%{opacity:0}}.caret{animation:blink 1.05s step-end infinite}']

    # Header: repo id left, status right.
    y = 30
    d.text('rudybrrr/rudy', pad, y, 12.5, t['muted'], 'label', attrs=at(0))
    sw = d.text('open to internships', W - pad, y, 12.5, t['muted'], 'label', 'end', attrs=at(0))
    live_dot(d, W - pad - sw - 12, y - 4.2, t['live'])
    d.add(f'<rect x="0" y="{y + 14}" width="{W}" height="1" fill="{t["rule"]}"/>')

    # The name, as tokens. The leading space of " R" stays inside its chip, as a tokenizer shows it.
    gap = 6 if narrow else 8
    padx = 0.12
    widths = [measure(tok, 100, 'display') for tok, _ in NAME_TOKENS]
    size = (W - 2 * pad - gap * (len(NAME_TOKENS) - 1)) / (sum(widths) / 100 + 2 * padx * len(NAME_TOKENS))
    top = y + (40 if narrow else 48)
    ch = size * 1.12
    x = pad
    for i, (tok, tid) in enumerate(NAME_TOKENS):
        w = widths[i] * size / 100 + 2 * padx * size
        a = 0.25 + i * 0.16
        d.add(f'<g class="chip" style="animation-delay:{a:.2f}s">'
              f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{ch:.1f}" rx="{size * 0.14:.1f}" fill="{t["chip"][i % 5]}"/>')
        d.text(tok, x + padx * size, top + ch * 0.74, size, t['ink'], 'display')
        d.add('</g>')
        d.text(str(tid), x + 2, top + ch + 20, 11.5, t['muted'], 'label', attrs=at(a + 0.25))
        x += w + gap

    # Prompt, then the answer streamed.
    y = top + ch + (62 if narrow else 72)
    d.text('>', pad, y, 13.5, t['deep'][0], 'label', attrs=at(1.1))
    d.text(PROMPT, pad + 18, y, 13.5, t['muted'], 'label', attrs=at(1.1))
    asize = 16 if narrow else 20.5
    lh = asize * 1.55
    y += lh + 4
    tokens = re.findall(r' ?[\w&-]+|[^\w\s]', ANSWER)
    x, start, step = pad, 1.6, 0.075
    for i, tok in enumerate(tokens):
        w = measure(tok, asize)
        if x + w > W - pad and tok.startswith(' '):
            x, y, tok = pad, y + lh, tok[1:]
            w = measure(tok, asize)
        a = start + i * step
        lead = measure(' ', asize) if tok.startswith(' ') else 0
        d.add(f'<rect class="flash" style="animation-delay:{a:.3f}s" x="{x + lead - 1:.1f}" y="{y - asize * 0.95:.1f}" '
              f'width="{w - lead + 2:.1f}" height="{asize * 1.3:.1f}" rx="3" fill="{t["chip"][i % 5]}"/>')
        d.text(tok, x, y, asize, t['ink'], attrs=f'class="tok" style="animation-delay:{a:.3f}s"')
        x += w
    end = start + len(tokens) * step
    d.add(f'<rect class="caret" style="animation-delay:{end:.2f}s" x="{x + 3:.1f}" y="{y - asize * 0.85:.1f}" '
          f'width="{asize * 0.5:.1f}" height="{asize * 1.1:.1f}" fill="{t["ink"]}" opacity=".85"/>')

    # Footer: what the model is doing today, and the token count.
    y += 46 if narrow else 54
    d.add(f'<rect x="0" y="{y - 26}" width="{W}" height="1" fill="{t["rule"]}"/>')
    if narrow:
        for j, m in enumerate(META):
            d.text(m, pad, y + j * 18, 11.5, t['muted'], 'label', attrs=at(end + 0.2))
        d.text(f'{len(tokens)} tokens', W - pad, y, 11.5, t['muted'], 'label', 'end', attrs=at(end + 0.3))
        y += 18
    else:
        d.text('     '.join(META), pad, y, 12, t['muted'], 'label', attrs=at(end + 0.2))
        d.text(f'{len(tokens)} tokens, streamed', W - pad, y, 12, t['muted'], 'label', 'end', attrs=at(end + 0.3))
    d.h = y + 18
    d.body.insert(0, f'<rect x=".5" y=".5" width="{W - 1}" height="{d.h - 1:.0f}" rx="14" fill="none" stroke="{t["rule"]}"/>')
    d.save(f'hero-{th}' + ('-m' if narrow else ''))


def months(y, m):
    return (y - 2025) * 12 + (m - 5)  # 0 = May 2025


def loss(m, val=False):
    """Illustrative: a decaying curve, a little noise, and the game-jam spike in June 2026."""
    base = 0.2 + 0.72 * math.exp(-m / 6.5)
    spike = 0.2 * math.exp(-((m - 13.3) / 0.35) ** 2)
    if val:
        return base + 0.05 + 0.04 * math.exp(-m / 9) + spike * 0.8
    noise = 0.022 * math.sin(m * 7.1) + 0.014 * math.sin(m * 13.7 + 1) + 0.01 * math.sin(m * 29.3 + 2)
    return base + noise + spike


MONTHS = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def training(th, W):
    t = THEMES[th]
    narrow = W < 600
    L, R, T, B = 8, W - 8, 34, (250 if narrow else 340)
    lo = -0.1 if narrow else -0.62  # headroom under the curve for the label lane
    span = months(2026, 9)
    X = lambda m: L + (R - L) * m / span  # noqa: E731
    Y = lambda v: B - (B - T) * (v - lo) / (1.05 - lo)  # noqa: E731
    d = Doc(W, 'Fig. 1. Training loss, May 2025 to now, illustrative. Checkpoints: '
            + '; '.join(f'{MONTHS[c[1]]} {c[0]}: {c[2]}' for c in CHECKPOINTS))
    dur = 3.4
    d.css += [FADE, PING,
              f'@keyframes reveal{{from{{transform:scaleX(0)}}}}.reveal{{transform-box:fill-box;transform-origin:0 0;animation:reveal {dur}s cubic-bezier(.45,0,.25,1) .3s both}}']
    for v in (0.25, 0.5, 0.75, 1.0) if narrow else (0.4, 0.7, 1.0):
        d.add(f'<line x1="{L}" x2="{R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{t["rule"]}" stroke-dasharray="2 5"/>')
    d.add(f'<line x1="{L}" x2="{R}" y1="{B}" y2="{B}" stroke="{t["rule"]}"/>')
    d.text('loss', L, T - 14, 11.5, t['muted'], 'label')
    lx = R
    for label, dash in (('val', '5 4'), ('train', '')):
        w = d.text(label, lx, T - 14, 11.5, t['muted'], 'label', 'end')
        col = t['muted'] if dash else t['deep'][0]
        d.add(f'<line x1="{lx - w - 30:.1f}" x2="{lx - w - 8:.1f}" y1="{T - 18}" y2="{T - 18}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>')
        lx -= w + 46
    ticks = [(2025, 6, 'Jun 2025'), (2025, 12, 'Dec'), (2026, 6, 'Jun 2026'), (2026, 9, 'now')] if narrow else \
        [(2025, 6, 'Jun 2025'), (2025, 9, 'Sep'), (2025, 12, 'Dec'), (2026, 3, 'Mar 2026'), (2026, 6, 'Jun'), (2026, 9, 'now')]
    for y, m, lab in ticks:
        d.text(lab, min(max(X(months(y, m)), L + 30), R - 14), B + 20, 11, t['muted'], 'label', 'middle')

    def path(val):
        pts = [(X(i / 10), Y(loss(i / 10, val))) for i in range(int(span * 10) + 1)]
        return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)

    d.defs.append(f'<clipPath id="draw"><rect class="reveal" x="{L}" y="0" width="{R - L + 4}" height="{B + 4}"/></clipPath>')
    d.add(f'<g clip-path="url(#draw)"><path d="{path(True)}" fill="none" stroke="{t["muted"]}" stroke-width="1.5" stroke-dasharray="5 4" opacity=".7"/>'
          f'<path d="{path(False)}" fill="none" stroke="{t["deep"][0]}" stroke-width="2.2" stroke-linejoin="round"/></g>')

    # Checkpoints appear as the line reaches them.
    lsize = 11.5
    for k, (yy, mo, label, row) in enumerate(CHECKPOINTS):
        m = months(yy, mo) + 0.5
        cx, cy = X(m), Y(loss(m))
        a = 0.3 + dur * (m / span) ** 0.9
        col = t['deep'][(k + 1) % 5]
        d.add(f'<g {at(a)}><circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{col}"/>')
        if narrow:
            d.text(str(k + 1), cx, cy + 20 if row < 0 else cy - 10, 11, t['ink'], 'label', 'middle')
        else:
            lines = wrap(label, lsize, 150, 'label')
            anchor = 'end' if cx > R - 150 else 'start'
            tx = cx + (-8 if anchor == 'end' else 8)
            if row >= 0:
                ty = Y(0.08) + row * 56
                d.add(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{cy + 7:.1f}" y2="{ty + 4 + len(lines) * 15:.1f}" stroke="{col}" stroke-dasharray="1 3"/>')
            else:
                ty = cy - 22 - len(lines) * 15
                d.add(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{ty - 12:.1f}" y2="{cy - 7:.1f}" stroke="{col}" stroke-dasharray="1 3"/>')
            d.text(f'{MONTHS[mo]} {yy}', tx, ty, 10.5, t['muted'], 'label', anchor)
            for j, line in enumerate(lines):
                d.text(line, tx, ty + 15 * (j + 1), lsize, t['ink'], 'label', anchor)
        d.add('</g>')
    ex, ey = X(span), Y(loss(span))
    d.add(f'<g {at(0.3 + dur)}>')
    live_dot(d, ex - 2, ey, t['deep'][0], 4)
    d.add('</g>')

    y = B + 50
    if narrow:
        for k, (yy, mo, label, _) in enumerate(CHECKPOINTS):
            d.text(f'{k + 1}  {MONTHS[mo]} {yy}', 0, y, 11, t['muted'], 'label')
            for line in wrap(label, 12, W - 120, 'label'):
                d.text(line, 112, y, 12, t['ink'], 'label')
                y += 17
            y += 6
        y += 12
    for line in wrap('Fig. 1. Training loss, May 2025 to now. Illustrative; nobody measured it.', 12, W, 'label'):
        d.text(line, 0, y, 12, t['muted'], 'label')
        y += 18
    d.h = y
    d.save(f'training-{th}' + ('-m' if narrow else ''))


def embedding(th, W):
    """The toolbox as a hand-placed 2D embedding: four clusters that drift, and a point for Rudy."""
    t = THEMES[th]
    narrow = W < 600
    d = Doc(W, 'Fig. 2. Toolbox embedding. ' + '; '.join(f'{k}: {", ".join(v[2])}' for k, v in EMBEDDING.items()))
    d.css += [FADE, PING] + [
        f'@keyframes f{i}{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate({dx}px,{dy}px)}}}}'
        for i, (dx, dy) in enumerate([(3, -4), (-4, 2), (2, 4), (-3, -3)])] + [
        '@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}'
        '.hull{transform-box:fill-box;transform-origin:50% 50%;animation:breathe 7s ease-in-out infinite}']
    rowh = 27
    H = 0
    hulls = []
    for k, (name, (cx, cy, tools)) in enumerate(EMBEDDING.items()):
        if narrow:
            ox, oy, cols = 14 + (k % 2) * W / 2, 40 + (k // 2) * 260, 1
        else:
            ox, oy, cols = cx * W - 150, cy * 420 - 60, 2
        rows = math.ceil(len(tools) / cols)
        bw, bh = (W / 2 - 34 if narrow else 300), rows * rowh + 34
        d.add(f'<rect class="hull" style="animation-delay:{-k * 1.7:.1f}s" x="{ox - 14:.1f}" y="{oy - 30:.1f}" width="{bw:.1f}" '
              f'height="{bh:.1f}" rx="22" fill="{t["chip"][k]}" opacity=".55"/>')
        d.text(name, ox, oy - 8, 11.5, t['muted'], 'label', attrs=at(0.3 + k * 0.1))
        for i, tool in enumerate(tools):
            px = ox + (i % cols) * 150 + (0 if narrow else (i // cols % 2) * 10)
            py = oy + 18 + (i // cols) * rowh + (0 if narrow else (i % cols) * 8)
            d.add(f'<g style="animation:f{(i + k) % 4} {6 + (i * 1.3 + k) % 4:.1f}s ease-in-out {-i * 0.9:.1f}s infinite">'
                  f'<g {at(0.4 + k * 0.1 + i * 0.05)}><circle cx="{px:.1f}" cy="{py - 4:.1f}" r="4" fill="{t["deep"][k]}"/>')
            d.text(tool, px + 11, py, 12.5, t['ink'])
            d.add('</g></g>')
        H = max(H, oy - 30 + bh)
        hulls.append((ox - 14 + bw / 2, oy - 30 + bh / 2, t['deep'][k]))
    # Rudy sits between the clusters (the full-stack part), attending to all four.
    rx, ry = (W / 2 - 24, H + 36) if narrow else (W * 0.44, 420 * 0.52 - 14)
    d.css.append('@keyframes march{to{stroke-dashoffset:-16}}.att{animation:march 1.6s linear infinite}')
    if not narrow:
        lines = ''.join(f'<g {at(1.3 + k * 0.1)}><line class="att" x1="{rx:.1f}" y1="{ry:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" '
                        f'stroke="{col}" stroke-width="1.2" stroke-dasharray="2 6" opacity=".7"/></g>'
                        for k, (hx, hy, col) in enumerate(hulls))
        d.body.insert(0, lines)  # under the hulls
    d.add(f'<g {at(1.2)}>')
    live_dot(d, rx, ry, t['ink'], 5)
    d.text('rudy', rx + 12, ry + 4.5, 13.5, t['ink'], 'display')
    d.add('</g>')
    y = max(H, ry) + 44
    for line in wrap('Fig. 2. Toolbox embedding. Hand-placed, not t-SNE; distances are vibes.', 12, W, 'label'):
        d.text(line, 0, y, 12, t['muted'], 'label')
        y += 18
    d.h = y
    d.save(f'embedding-{th}' + ('-m' if narrow else ''))


def endoftext(th, W):
    t = THEMES[th]
    d = Doc(W, '<|endoftext|>')
    d.css += ['@keyframes blink{0%,50%{opacity:1}50.01%,100%{opacity:0}}.caret{animation:blink 1.05s step-end infinite}']
    tok = '<|endoftext|>'
    w = measure(tok, 15, 'label')
    d.add(f'<rect x="1" y="8" width="{w + 20:.1f}" height="30" rx="6" fill="{t["chip"][0]}"/>')
    d.text(tok, 11, 28, 15, t['ink'], 'label')
    d.add(f'<rect class="caret" x="{w + 30:.1f}" y="12" width="9" height="22" fill="{t["ink"]}" opacity=".85"/>')
    d.w = int(w + 44)
    d.h = 46
    d.save(f'eot-{th}' + ('-m' if W < 600 else ''))


# --- README -------------------------------------------------------------------------------

PHONE = '(max-width: 600px)'


def pic(name, alt, width='100%'):
    return (f'<picture>'
            f'<source media="{PHONE} and (prefers-color-scheme: dark)" srcset="assets/{name}-dark-m.svg">'
            f'<source media="{PHONE}" srcset="assets/{name}-light-m.svg">'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
            f'<img src="assets/{name}-light.svg" width="{width}" alt="{esc(alt)}"></picture>')


def table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(r) + ' |' for r in rows])


def readme():
    out = [
        f'<a href="{URL}">{pic("hero", f"rudybrrr/rudy. Rudhresh R., tokenized. {ANSWER}")}</a>',
        '## Model details',
        '\n'.join(f'- **{k}:** {v}' for k, v in DETAILS),
        '## Training',
        pic('training', 'Fig. 1. An illustrative training-loss curve from May 2025 to now, with checkpoints: '
            + '; '.join(c[2] for c in CHECKPOINTS)),
        '**Training data**\n\n' + '\n'.join(f'- {x}' for x in TRAINING_DATA),
        '## Evaluation',
        table(['Benchmark', 'Result'], [(f'{b}<br><sub>{n}</sub>', r) for b, r, n in EVALUATION]),
        '## Deployments',
        table(['Where', 'What it had to do'], [(f'[**{n}**]({h})<br><sub>{r}</sub>', c) for n, h, r, c in DEPLOYMENTS]),
        '## Downstream tasks',
        'Every project, grouped. Names open the case study; *code* opens the repo.',
    ]
    for name, line, is_open, tasks in TASKS:
        rows = [(f'[**{x["name"]}**]({x["href"]})' + (f'<br><sub>[code]({x["repo"]})</sub>' if x['repo'] else ''),
                 f'{x["claim"]}<br><sub>{x["setting"]}</sub>') for x in tasks]
        out.append(f'<details{" open" if is_open else ""}>\n<summary><b>{name}</b> &nbsp;{len(tasks)} &nbsp;<i>{line}</i></summary>\n\n'
                   + table(['Task', 'What it does'], rows) + '\n\n</details>')
    out += [
        '## Toolbox',
        pic('embedding', 'Fig. 2. Toolbox embedding: ' + '; '.join(f'{k}: {", ".join(v[2])}' for k, v in EMBEDDING.items())),
        '## Intended use',
        '\n'.join(f'- {x}' for x in INTENDED),
        '**Out of scope**\n\n' + '\n'.join(f'- {x}' for x in OUT_OF_SCOPE),
        '## Limitations and biases',
        '\n'.join(f'- {x}' for x in LIMITATIONS),
        '## How to use',
        f'```python\nfrom rudy import Rudy\n\nrudy = Rudy.from_pretrained("rudybrrr/rudy")\n'
        f'rudy.contact(email="{EMAIL}")  # also LinkedIn, Telegram\n```',
        f'[Email](mailto:{EMAIL}) &nbsp;·&nbsp; [LinkedIn]({LINKEDIN}) &nbsp;·&nbsp; [Telegram]({TELEGRAM}) &nbsp;·&nbsp; [rudhresh.com]({URL})',
        '## Citation',
        '```bibtex\n@misc{ravichandran2026rudy,\n  author = {Ravichandran, Agne Rudhresh},\n'
        '  title  = {Rudy: a full-stack AI engineer},\n  year   = {2026},\n'
        f'  note   = {{Open to internships}},\n  url    = {{{URL}}}\n}}\n```',
        pic('eot', '<|endoftext|>', 'auto'),
    ]
    (ROOT / 'README.md').write_text('<!-- Generated by src/build.py from src/content.py. Edit those, not this. -->\n\n'
                                    + '\n\n'.join(out) + '\n')


if __name__ == '__main__':
    for f in ASSETS.glob('*.svg'):
        f.unlink()
    for th in THEMES:
        for W in (880, 440):
            hero(th, W)
            training(th, W)
            embedding(th, W)
            endoftext(th, W)
    readme()
    print(f'built {len(list(ASSETS.glob("*.svg")))} svgs')
