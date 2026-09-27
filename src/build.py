"""Builds every image in assets/ for the profile README.

Type is Neue Montreal (the portfolio's face) turned into outlines, so the SVGs look the
same everywhere and ship no font file. Colour and motion follow rudhresh.com: the #141517
stage, the #E9EAEB band, #455CE9 only as punctuation, the living sheet edge, lit rows.

Run: python3 src/build.py   (needs fonttools + uharfbuzz; FONT= overrides the font path)
Content lives in content.py next to this file.
"""

import base64
import json
import math
import os
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from content import (ALONG, BUILD, CATEGORIES, FLAGSHIPS, PROOF, SITE, STACK,
                     STATEMENT)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
FONT = os.environ.get('FONT', str(Path.home() / 'Documents/Projects/portfolio-site/app/_fonts/neue-montreal/regular/index.ttf'))

W = 880
PAD = 36
STAGE = '#141517'
BAND = '#E9EAEB'
ACCENT = '#455CE9'
LIVE = '#28c840'
EASE_OUT = 'cubic-bezier(0.16, 1, 0.3, 1)'  # expo.out
EASE_IN_OUT = 'cubic-bezier(0.76, 0, 0.24, 1)'  # power4.inOut, near enough

# GitHub's own page colours, so a "sheet" drawn in an image is the page itself.
THEMES = {
    'light': {'page': '#ffffff', 'ink': '#141517', 'rule': 'rgba(20,21,23,0.12)', 'band': BAND,
              'accent': ACCENT, 'stage': STAGE, 'on_stage': '#ffffff'},
    'dark': {'page': '#0d1117', 'ink': '#e6edf3', 'rule': 'rgba(230,237,243,0.14)', 'band': '#161b22',
             'accent': '#7d8cf5', 'stage': BAND, 'on_stage': STAGE},
}


# --- type -------------------------------------------------------------------------------

_tt = TTFont(FONT)
_upem = _tt['head'].unitsPerEm
_glyphs = _tt.getGlyphSet()
_order = _tt.getGlyphOrder()
_hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(FONT)))
_paths = {}


def glyph_path(gid):
    if gid not in _paths:
        pen = SVGPathPen(_glyphs)
        _glyphs[_order[gid]].draw(pen)
        _paths[gid] = pen.getCommands()
    return _paths[gid]


def shape(text, size, track=0.0):
    """[(gid, x)] in px plus the run's width. track is in em, like CSS letter-spacing."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(_hbfont, buf, {'kern': True, 'liga': True})
    k = size / _upem
    x, out = 0.0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((info.codepoint, x + pos.x_offset * k))
        x += pos.x_advance * k + track * size
    return out, x - (track * size if out else 0)


def measure(text, size, track=0.0):
    return shape(text, size, track)[1]


def wrap(text, size, width, track=0.0):
    lines, line = [], ''
    for word in text.split(' '):
        test = f'{line} {word}'.strip()
        if line and measure(test, size, track) > width:
            lines.append(line)
            line = word
        else:
            line = test
    return lines + [line] if line else lines


class Doc:
    """One SVG: glyphs are defined once and placed with <use>."""

    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.used, self.css, self.defs, self.body = set(), [], [], []

    def text(self, s, x, y, size, fill, track=0.0, anchor='start', attrs='', each=None):
        """Draws s with its baseline at y. each(i, glyph_svg) wraps single glyphs for per-letter motion."""
        run, width = shape(s, size, track)
        if anchor == 'end':
            x -= width
        elif anchor == 'middle':
            x -= width / 2
        k = size / _upem
        parts = []
        for i, (gid, gx) in enumerate(run):
            if not glyph_path(gid):
                continue
            self.used.add(gid)
            g = f'<use href="#g{gid}" transform="translate({x + gx:.2f} {y:.2f}) scale({k:.5f} {-k:.5f})"/>'
            parts.append(each(i, g) if each else g)
        self.body.append(f'<g fill="{fill}" {attrs}>{"".join(parts)}</g>')
        return width

    def add(self, svg):
        self.body.append(svg)

    def render(self):
        glyphs = ''.join(f'<path id="g{g}" d="{glyph_path(g)}"/>' for g in sorted(self.used))
        css = ''.join(self.css) + '@media (prefers-reduced-motion: reduce){*{animation:none!important}}'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img"><title>{esc(self.title)}</title>'
                f'<style>{css}</style><defs>{glyphs}{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')

    def save(self, name):
        ASSETS.mkdir(exist_ok=True)
        (ASSETS / f'{name}.svg').write_text(self.render())


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rise_css(name='rise', dist=1.05):
    """A letter or line snapping up out of its mask."""
    return (f'@keyframes {name}{{from{{transform:translateY({dist * 100:.0f}%)}}}}'
            f'.{name}{{transform-box:fill-box;animation:{name} .7s {EASE_OUT} both}}')


# --- the sheet edge (rudhresh.com app/_layout/sheet-curve.js) ----------------------------

R = 20  # the site's 1.25rem soft corner


def sag_path(w, depth, apex, top=0):
    """A sheet's bottom edge at y=top: rounded corners, then a sag whose low point sits at x=apex."""
    r, h = R, R + depth
    right, left = w - r - apex, apex - r
    return (f'M0 {top}H{w}V{top}A{r} {r} 0 0 1 {w - r} {top + r}'
            f'C{w - r - right * 0.5:.1f} {top + r} {apex + right * 0.5:.1f} {top + h:.1f} {apex:.1f} {top + h:.1f}'
            f'C{apex - left * 0.5:.1f} {top + h:.1f} {r + left * 0.5:.1f} {top + r} {r} {top + r}'
            f'A{r} {r} 0 0 1 0 {top}Z')


def arch_path(w, depth, apex, bottom):
    """A sheet's top edge ending at y=bottom: an arch whose high point sits at x=apex."""
    r = R
    base = bottom - r  # where the corners start
    top = base - depth
    left, right = apex - r, w - r - apex
    return (f'M0 {bottom}V{base + r}A{r} {r} 0 0 1 {r} {base}'
            f'C{r + left * 0.5:.1f} {base} {apex - left * 0.5:.1f} {top:.1f} {apex:.1f} {top:.1f}'
            f'C{apex + right * 0.5:.1f} {top:.1f} {w - r - right * 0.5:.1f} {base} {w - r} {base}'
            f'A{r} {r} 0 0 1 {w} {base + r}V{bottom}Z')


def living(path_fn, *, w, depth, dur, phase=0.0, **kw):
    """SMIL values for an edge whose low/high point drifts across the middle 30-70%, as if
    following a pointer, while its depth breathes. Samples loop back onto the first."""
    n = 36
    values = []
    for i in range(n + 1):
        a = 2 * math.pi * (i / n + phase)
        apex = w * (0.5 + 0.2 * math.sin(a) * (0.85 + 0.15 * math.cos(3 * a)))
        d = depth * (0.72 + 0.28 * math.sin(2 * a + 0.8))
        values.append(path_fn(w, d, apex, **kw))
    return f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(values)}"/>', values[0]


# --- pieces -------------------------------------------------------------------------------
# Every piece is drawn twice: wide (880, desktop) and narrow (440, phones, NARROW=True).
# GitHub picks one per viewer with <picture> media queries, so phones get re-set type
# instead of the desktop art shrunk to 40%.

NARROW = False
SUFFIX = ''


def layout(narrow):
    global W, PAD, NARROW, SUFFIX
    NARROW = narrow
    W, PAD, SUFFIX = (440, 22, '-m') if narrow else (880, 36, '')


def lift_css(dist=12):
    return f'@keyframes lift{{from{{opacity:0;transform:translateY({dist}px)}}}}.lift{{animation:lift .9s {EASE_OUT} both}}'


PING_CSS = ('@keyframes ping{75%,100%{transform:scale(2.4);opacity:0}}'
            '.ping{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.6s cubic-bezier(0,0,.2,1) infinite}')


def live_dot(d, cx, cy, r=5):
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LIVE}"/><circle class="ping" cx="{cx}" cy="{cy}" r="{r}" fill="{LIVE}"/>')


def delayed(at):
    return f'class="lift" style="animation-delay:{at:.2f}s"'


def hero():
    """The loader (Model, System, Product sheets lift in turn), then the name on the stage,
    with the site's chrome ribbon turning behind it. Plays once; the ribbon keeps flowing."""
    H = 560 if NARROW else 480
    d = Doc(W, H, f'{SITE["name"]}. {SITE["role"]}. {SITE["status"]}.')
    d.defs.append(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>')
    d.add(f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{STAGE}"/>')

    # Name: fitted to the width.
    name = SITE['name']
    track = -0.055
    size = (W - 2 * PAD + 6) / (measure(name, 100, track) / 100)
    base = (26 if NARROW else 40) + size * 0.72

    # Ribbon: transparent frames, one shown at a time at 12 fps, looping seamlessly.
    frames = sorted((ROOT / 'src/ribbon').glob('*.webp'))
    box = json.loads((ROOT / 'src/ribbon/box.json').read_text())
    if NARROW:
        scale = 0.92
        rx, ry = W - box['w'] * scale + 40, base + 4  # bleeds off the right edge
    else:
        scale = 0.95
        rx, ry = 470 + box['x'] * scale, 40 + box['y'] * scale
    n = len(frames)
    loop = n / 12
    d.css.append(f'@keyframes f{{0%,{100 / n:.4f}%{{opacity:1}}{100 / n + 0.0001:.4f}%,100%{{opacity:0}}}}'
                 f'.f{{opacity:0;animation:f {loop:.3f}s step-end infinite}}.f0{{opacity:1}}'
                 f'@keyframes ribbon{{from{{opacity:0;transform:translate(24px,40px) scale(.92)}}}}'
                 f'.ribbon{{transform-box:fill-box;transform-origin:50% 50%;animation:ribbon 1.6s {EASE_OUT} 2.5s both}}')
    imgs = []
    for i, f in enumerate(frames):
        data = base64.b64encode(f.read_bytes()).decode()
        imgs.append(f'<image class="f{" f0" if i == 0 else ""}" style="animation-delay:{i * loop / n - loop:.3f}s" '
                    f'width="{box["w"]}" height="{box["h"]}" href="data:image/webp;base64,{data}"/>')
    d.add(f'<g class="ribbon"><g transform="translate({rx:.1f} {ry:.1f}) scale({scale})">{"".join(imgs)}</g></g>')

    # Letters rise from the middle outward.
    mid = (len(name) - 1) / 2
    d.css.append(rise_css('up', 1.1) + lift_css(14) + PING_CSS)
    d.defs.append(f'<clipPath id="namemask"><rect y="{base - size:.0f}" width="{W}" height="{size * 1.2:.0f}"/></clipPath>')
    d.text(name, PAD - 3 * size / 170, base, size, '#ffffff', track, attrs='clip-path="url(#namemask)"',
           each=lambda i, g: f'<g class="up" style="animation-delay:{2.45 + abs(i - mid) * 0.045:.3f}s">{g}</g>')

    # Role and status. Wide: role bottom right, status bottom left. Narrow: role under the name.
    rsize = 30 if NARROW else 38
    ssize = 14.5 if NARROW else 17
    for j, line in enumerate(SITE['role_lines']):
        if NARROW:
            d.text(line, PAD, base + 58 + j * rsize * 1.04, rsize, '#ffffff', -0.03, attrs=delayed(2.85 + j * 0.08))
        else:
            d.text(line, W - PAD, H - PAD - (1 - j) * rsize * 1.02, rsize, '#ffffff', -0.03, anchor='end',
                   attrs=delayed(2.85 + j * 0.08))
    lh = ssize * 1.42
    y = H - PAD - 2 * lh
    d.add(f'<g {delayed(3.05)}>')
    live_dot(d, PAD + 5, y - ssize * 0.34, 4.5 if NARROW else 5)
    d.add('</g>')
    d.text(SITE['status'], PAD + ssize + 4, y, ssize, '#ffffff', attrs=delayed(3.05))
    for j, line in enumerate(SITE['status_lines']):
        d.text(line, PAD, y + lh * (j + 1), ssize, 'rgba(255,255,255,0.55)', 0.01, attrs=delayed(3.13 + j * 0.08))

    # The loader's three sheets, top one first. Each word snaps up, then its sheet lifts away,
    # its lower edge sagging as it goes. At rest (and under reduced motion) they're gone.
    sheets = [('Model', STAGE, '#ffffff', 0.15, 0.55, 0.62),
              ('System', BAND, STAGE, 0.95, 1.35, 0.56),
              ('Product', '#ffffff', STAGE, 1.7, 2.05, 0.52)]
    d.css.append(f'@keyframes sheet{{from{{transform:translateY(0)}}to{{transform:translateY(-{H + 140}px)}}}}'
                 f'.sheet{{transform:translateY(-{H + 140}px);animation:sheet var(--t) {EASE_IN_OUT} var(--at) backwards}}'
                 f'@keyframes sag{{0%{{transform:scaleY(0)}}45%{{transform:scaleY(1)}}100%{{transform:scaleY(.15)}}}}'
                 f'.sag{{transform-box:fill-box;transform-origin:50% 0;transform:scaleY(0);animation:sag var(--t) ease-in-out var(--at) backwards}}'
                 f'@keyframes word{{from{{transform:translateY(105%)}}}}'
                 f'.word{{transform-box:fill-box;animation:word .26s {EASE_OUT} var(--w) both}}')
    wsize = 76 if NARROW else 104
    for k, (word, bg, fg, w_at, at, t) in reversed(list(enumerate(sheets))):
        d.defs.append(f'<clipPath id="wm{k}"><rect y="{H / 2 - wsize * 0.5:.0f}" width="{W}" height="{wsize * 1.12:.0f}"/></clipPath>')
        d.add(f'<g class="sheet" style="--at:{at}s;--t:{t}s"><rect width="{W}" height="{H + 1}" fill="{bg}"/>'
              f'<path class="sag" style="--at:{at}s;--t:{t}s" fill="{bg}" d="{sag_path(W, 110 if not NARROW else 80, W * 0.54, 0)}" transform="translate(0 {H})"/>')
        d.text(word, W / 2, H / 2 + wsize * 0.36, wsize, fg, -0.045, anchor='middle',
               attrs=f'clip-path="url(#wm{k})"', each=lambda i, g, w=w_at: f'<g class="word" style="--w:{w}s">{g}</g>')
        d.add('</g>')
    d.add('</g>')
    d.save(f'hero{SUFFIX}')


def statement(theme):
    t = THEMES[theme]
    size, lh, track = (29, 1.14, -0.025) if NARROW else (40, 1.12, -0.03)
    lines = wrap(STATEMENT, size, W - (0 if NARROW else 40), track)
    psize = 16 if NARROW else 19
    plines = wrap_rich(PROOF, psize, min(600, W))
    H = int(8 + len(lines) * size * lh + 40 + len(plines) * psize * 1.45 + 8)
    d = Doc(W, H, STATEMENT)
    # Words brighten in reading order, as they do with scroll on the site.
    d.css.append('@keyframes lit{from{opacity:.16}}.lit{animation:lit .6s ease-out both}')
    i = 0
    y = 8 + size * 0.8
    for line in lines:
        x = 0
        for word in line.split(' '):
            w = d.text(word, x, y, size, t['ink'], track, attrs=f'class="lit" style="animation-delay:{0.6 + i * 0.09:.2f}s"')
            x += w + measure(' ', size) + track * size
            i += 1
        y += size * lh
    draw_rich(d, plines, 0, y + 30, psize, t, delay=0.6 + i * 0.09 + 0.2)
    d.save(f'statement{SUFFIX}-{theme}')


def wrap_rich(spans, size, width):
    """spans: [(text, strong)]. Wraps word by word, keeping each word's weight."""
    words = [(w, strong) for text, strong in spans for w in text.split(' ') if w]
    lines, line, lw = [], [], 0.0
    space = measure(' ', size)
    for w, strong in words:
        ww = measure(w, size, 0.01)
        if line and lw + space + ww > width:
            lines.append(line)
            line, lw = [], 0.0
        lw += (space if line else 0) + ww
        line.append((w, strong))
    return lines + [line] if line else lines


def draw_rich(d, lines, x0, y, size, t, delay):
    space = measure(' ', size)
    k = 0
    for line in lines:
        x = x0
        for w, strong in line:
            fill = t['ink'] if strong else muted(t)
            cls = f'class="lit" style="animation-delay:{delay + k * 0.05:.2f}s"' if strong else ''
            x += d.text(w, x, y, size, fill, 0.01, attrs=cls) + space
            k += 1
        y += size * 1.45
    return y


def muted(t):
    return 'rgba(20,21,23,0.52)' if t['ink'] == '#141517' else 'rgba(230,237,243,0.55)'


def how_i_build(theme):
    """The gray band: the lead, then Model, System, Product (a real sequence, so numbered).
    Three columns wide, stacked on phones."""
    t = THEMES[theme]
    gap = 28
    col = W - 2 * PAD if NARROW else (W - 2 * PAD - 2 * gap) / 3
    bsize = 15.5
    d = Doc(W, 0, 'How I build. ' + ' '.join(f'{s["word"]}: {s["body"]}' for s in BUILD['steps']))
    d.css.append(rise_css('up', 1.1) + lift_css(10) +
                 f'@keyframes draw{{from{{transform:scaleX(0)}}}}.draw{{transform-box:fill-box;transform-origin:0 0;animation:draw 1.1s {EASE_OUT} both}}')
    hsize = 27 if NARROW else 34
    y = PAD + hsize * 0.88
    for j, line in enumerate(BUILD['heading']):
        d.defs.append(f'<clipPath id="h{j}"><rect y="{y - hsize:.0f}" width="{W}" height="{hsize * 1.3:.0f}"/></clipPath>')
        d.text(line, PAD, y, hsize, t['ink'], -0.03, attrs=f'clip-path="url(#h{j})"',
               each=lambda i, g, j=j: f'<g class="up" style="animation-delay:{0.5 + j * 0.12:.2f}s">{g}</g>')
        y += hsize * 1.12
    top = y + (24 if NARROW else 44)
    H = 0
    for k, step in enumerate(BUILD['steps']):
        x = PAD if NARROW else PAD + k * (col + gap)
        at = 0.9 + k * 0.15
        d.add(f'<rect class="draw" style="animation-delay:{at:.2f}s" x="{x}" y="{top:.1f}" width="{col:.1f}" height="1" fill="{t["rule"]}"/>')
        d.text(f'0{k + 1}', x, top + 30, 14, muted(t), 0.02, attrs=delayed(at + 0.1))
        wy = top + 30 + (48 if NARROW else 56)
        wsize = 40 if NARROW else 46
        d.defs.append(f'<clipPath id="w{k}"><rect x="{x - 4}" y="{wy - wsize:.0f}" width="{col + 8:.0f}" height="{wsize * 1.26:.0f}"/></clipPath>')
        d.text(step['word'], x, wy, wsize, t['ink'], -0.04, attrs=f'clip-path="url(#w{k})"',
               each=lambda i, g, a=at: f'<g class="up" style="animation-delay:{a + 0.15 + i * 0.025:.3f}s">{g}</g>')
        by = wy + 34
        for line in wrap(step['body'], bsize, col - 6):
            d.text(line, x, by, bsize, t['ink'], 0.005, attrs=delayed(at + 0.3))
            by += bsize * 1.5
        d.text('  '.join(step['tools']), x, by + 14, 14, muted(t), 0.015, attrs=delayed(at + 0.4))
        if NARROW:
            top = by + 14 + 34
        H = max(H, by + 14 + PAD)
    d.h = int(H)
    d.body.insert(0, f'<rect width="{W}" height="{d.h}" fill="{t["band"]}"/>')
    d.save(f'how-i-build{SUFFIX}-{theme}')


def selected_work(theme):
    """The stage between two sheets: the page sags into it, rows light one at a time as if
    read by scroll, and the page arches back over it at the end."""
    t = THEMES[theme]
    fg = t['on_stage']
    q = 'rgba(255,255,255,0.5)' if fg == '#ffffff' else 'rgba(20,21,23,0.5)'
    top_d, bot_d = (34, 30) if NARROW else (46, 40)
    nsize = 50 if NARROW else 68
    lsize = 14.5 if NARROW else 15.5
    total = sum(len(c['items']) for c in CATEGORIES)
    d = Doc(W, 0, 'Selected work: ' + '; '.join(f'{p["name"]}, {p["line"]}' for p in FLAGSHIPS))
    d.css.append('@keyframes lit{0%,100%{opacity:.22}2%,23%{opacity:1}27%{opacity:.22}}.row{animation:lit 12s ease-in-out infinite}')
    hy = top_d + (56 if NARROW else 70)
    d.text('Selected work', PAD, hy, 26 if NARROW else 30, fg, -0.03)
    d.text(f'All {total} ↗' if NARROW else f'All {total} on rudhresh.com/work ↗', W - PAD, hy, lsize, q, 0.012, anchor='end')
    y = hy + (26 if NARROW else 34)
    step = 12 / len(FLAGSHIPS)
    for k, p in enumerate(FLAGSHIPS):
        d.add(f'<g class="row" style="animation-delay:{k * step - 12.5:.2f}s">')  # negative: already mid-cycle on first paint
        d.add(f'<rect x="{PAD}" y="{y:.1f}" width="{W - 2 * PAD}" height="1" fill="{q}" opacity=".35"/>')
        if NARROW:
            d.text(p['label'], PAD, y + 26, 13.5, fg, 0.012)
            ny = y + 26 + nsize * 0.9
        else:
            d.text(p['label'], W - PAD, y + 40, lsize, fg, 0.012, anchor='end')
            ny = y + 68
        d.text(p['name'], PAD - 3, ny, nsize, fg, -0.045)
        ly = ny + 26
        for line in wrap(p['line'], lsize, W - 2 * PAD, 0.012):
            d.text(line, PAD, ly, lsize, q, 0.012)
            ly += lsize * 1.45
        d.add('</g>')
        y = ly + (4 if NARROW else 0) - lsize * 1.45 + 14
    H = int(y + 26 + bot_d)
    d.h = H
    d.body.insert(0, f'<rect width="{W}" height="{H}" fill="{t["stage"]}"/>')
    # The page sagging in at the top, and arching back over at the bottom.
    anim, first = living(sag_path, w=W, depth=top_d - R, dur=9)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path>')
    anim, first = living(arch_path, w=W, depth=bot_d - R, dur=11, phase=0.4, bottom=H)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path>')
    d.save(f'selected-work{SUFFIX}-{theme}')


def category_head(theme, cat, index):
    t = THEMES[theme]
    size = 34 if NARROW else 40
    base = 58 if NARROW else 62
    H = 108 if NARROW else 104
    d = Doc(W, H, f'{cat["name"]}: {cat["line"]}')
    d.css.append(rise_css('up', 1.1) + lift_css(8))
    d.defs.append(f'<clipPath id="m"><rect y="{base - size:.0f}" width="{W}" height="{size * 1.3:.0f}"/></clipPath>')
    at = 0.4 + index * 0.05
    w = d.text(cat['name'], 0, base, size, t['ink'], -0.035, attrs='clip-path="url(#m)"',
               each=lambda i, g: f'<g class="up" style="animation-delay:{at + i * 0.02:.3f}s">{g}</g>')
    if cat.get('items'):
        d.text(str(len(cat['items'])), w + 7, base - size * 0.55, 15, t['accent'], 0.01, attrs=delayed(at + 0.3))
    if NARROW:
        d.text(cat['line'], 0, base + 28, 14.5, muted(t), 0.012, attrs=delayed(at + 0.2))
    else:
        d.text(cat['line'], W, base, 16, muted(t), 0.012, anchor='end', attrs=delayed(at + 0.2))
    d.save(f'cat-{cat["id"]}{SUFFIX}-{theme}')


def project_row(theme, p, index, total):
    """One row of the index: name, claim under it, context and year on the right (under the
    claim on phones). A small accent arrow lights in a wave that runs down the whole list."""
    t = THEMES[theme]
    csize = 14.5 if NARROW else 15.5
    claim = wrap(p['claim'], csize, W if NARROW else 560, 0.01)
    period = total * 0.35 + 3
    d = Doc(W, 0, f'{p["name"]}. {p["claim"]} {p["context"]}, {p["year"]}.')
    d.css.append(lift_css(12) +
                 '@keyframes wave{0%,100%{opacity:.28;transform:translate(0,0)}4%{opacity:1;transform:translate(3px,-3px)}12%{opacity:.28;transform:translate(0,0)}}'
                 f'.wave{{animation:wave {period:.2f}s ease-in-out infinite}}')
    d.add(f'<rect width="{W}" height="1" fill="{t["rule"]}"/>')
    d.add(f'<g {delayed(0.3 + (index % 6) * 0.06)}>')
    nsize = 26 if NARROW else 30
    y = 50
    w = d.text(p['name'], 0, y, nsize, t['ink'], -0.03)
    d.text('↗', w + 9, y - 2, nsize * 0.66, t['accent'], attrs=f'class="wave" style="animation-delay:{2 + index * 0.35 - period:.2f}s"')
    cy = y + 28
    for line in claim:
        d.text(line, 0, cy, csize, muted(t), 0.01)
        cy += csize * 1.45
    if NARROW:
        cw = d.text(p['context'], 0, cy + 6, 13.5, t['ink'], 0.012)
        d.text(p['year'], cw + 10, cy + 6, 13.5, muted(t), 0.012)
        cy += 6 + 13.5 * 1.45
    else:
        d.text(p['context'], W, y - 8, csize, t['ink'], 0.01, anchor='end')
        d.text(p['year'], W, y + 16, csize, muted(t), 0.01, anchor='end')
    d.add('</g>')
    d.h = int(cy - csize * 1.45 + 30)
    d.save(f'p-{p["id"]}{SUFFIX}-{theme}')


def marquee(theme):
    """The stack, drifting in two directions at display size."""
    t = THEMES[theme]
    size = 34 if NARROW else 44
    H = int(size * 3.4)
    d = Doc(W, H, 'Stack: ' + ', '.join(STACK[0] + STACK[1]))
    d.defs.append('<linearGradient id="fade"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                  '<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  f'<mask id="edge"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    d.add('<g mask="url(#edge)">')
    for j, words in enumerate(STACK):
        sep = '   /   '
        line = sep.join(words) + sep
        width = measure(line, size, -0.03)
        dur = width / 26
        d.css.append(f'@keyframes m{j}{{from{{transform:translateX({0 if j == 0 else -width:.1f}px)}}to{{transform:translateX({-width if j == 0 else 0:.1f}px)}}}}'
                     f'.m{j}{{animation:m{j} {dur:.1f}s linear infinite}}')
        d.add(f'<g class="m{j}" style="transform:translateX({-width / 3 if j == 0 else -width * 2 / 3:.1f}px)">')
        for r in range(math.ceil(W / width) + 1):
            d.text(line, r * width, size * 1.28 + j * size * 1.45, size, t['ink'] if j == 0 else muted(t), -0.03)
        d.add('</g>')
    d.add('</g>')
    d.save(f'stack{SUFFIX}-{theme}')


def along(theme):
    """Recognition, leadership and one line off the keyboard, as one flush ledger."""
    t = THEMES[theme]
    rh = 68 if NARROW else 58
    H = sum(34 + len(g['rows']) * rh + 30 for g in ALONG)
    d = Doc(W, H, '; '.join(f'{g["name"]}: ' + ', '.join(f'{a} ({b})' for a, b in g['rows']) for g in ALONG))
    d.css.append(lift_css(10))
    y, k = 0, 0
    for g in ALONG:
        d.text(g['name'], 0, y + 20, 14.5 if NARROW else 15.5, muted(t), 0.012)
        y += 34
        for a, b in g['rows']:
            d.add(f'<g {delayed(0.4 + k * 0.06)}><rect y="{y}" width="{W}" height="1" fill="{t["rule"]}"/>')
            if NARROW:
                d.text(a, 0, y + 30, 18.5, t['ink'], -0.015)
                d.text(b, 0, y + 53, 14, muted(t), 0.01)
            else:
                d.text(a, 0, y + 37, 21, t['ink'], -0.015)
                d.text(b, W, y + 37, 15.5, muted(t), 0.01, anchor='end')
            d.add('</g>')
            y += rh
            k += 1
        y += 30
    d.save(f'along{SUFFIX}-{theme}')


def footer(theme):
    """The footer stage: the page's lip sags over it, one closing line, quiet utility."""
    t = THEMES[theme]
    fg = t['on_stage']
    q = 'rgba(255,255,255,0.5)' if fg == '#ffffff' else 'rgba(20,21,23,0.5)'
    H = 470 if NARROW else 420
    d = Doc(W, H, 'Start a conversation: ' + SITE['email'])
    d.defs.append(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>')
    d.add(f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t["stage"]}"/>')
    d.css.append(rise_css('up', 1.1) + PING_CSS +
                 '@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(8px)}}'
                 '.nudge{animation:nudge 2.4s ease-in-out infinite}'
                 # Brand roll: "Code by Rudy" rolls up and the full name rolls in under it, now and then.
                 '@keyframes roll{0%,40%{transform:translateY(0)}48%,90%{transform:translateY(-19px)}98%,100%{transform:translateY(-38px)}}'
                 '.roll{animation:roll 9s cubic-bezier(.65,0,.35,1) infinite}')
    size = 56 if NARROW else 84
    y1 = 120 if NARROW else 150
    for j, line in enumerate(['Start a', 'conversation']):
        yy = y1 + j * size * 0.98
        d.defs.append(f'<clipPath id="c{j}"><rect y="{yy - size * 0.82:.0f}" width="{W}" height="{size * 1.04:.0f}"/></clipPath>')
        w = d.text(line, PAD - 3, yy, size, fg, -0.045, attrs=f'clip-path="url(#c{j})"',
                   each=lambda i, g, j=j: f'<g class="up" style="animation-delay:{0.6 + j * 0.12 + i * 0.02:.3f}s">{g}</g>')
    if NARROW:
        d.text('→', PAD - 3, yy + size * 0.95, size * 0.8, fg, attrs='class="nudge"')
    else:
        d.text('→', PAD - 3 + w + 22, yy, size * 0.8, fg, attrs='class="nudge"')
    fsize = 14.5 if NARROW else 15.5
    ly = H - (190 if NARROW else 96)
    d.add(f'<rect x="{PAD}" y="{ly}" width="{W - 2 * PAD}" height="1" fill="{q}" opacity=".45"/>')
    status = f'{SITE["status"]}, {SITE["focus"]}'
    if NARROW:
        rows = [[SITE['links'][0]], SITE['links'][1:]]
        yy = ly + 32
        for row in rows:
            x = PAD
            for label in row:
                x += d.text(label, x, yy, fsize, fg, 0.012) + 22
            yy += 28
        live_dot(d, PAD + 4, yy - 5, 4)
        d.text(status, PAD + 16, yy, fsize, q, 0.012)
        my = yy + 36
        for line in wrap(SITE['motto'], 12.5, W - 2 * PAD, 0.012):
            d.text(line, PAD, my, 12.5, q, 0.012)
            my += 18
    else:
        x = PAD
        for label in SITE['links']:
            x += d.text(label, x, ly + 34, fsize, fg, 0.012) + 26
        sw = d.text(status, W - PAD, ly + 34, fsize, q, 0.012, anchor='end')
        live_dot(d, W - PAD - sw - 14, ly + 29, 4.5)
        d.text(SITE['motto'], W - PAD, H - 26, 13, q, 0.012, anchor='end')
    by = H - 26
    d.defs.append(f'<clipPath id="roll"><rect x="{PAD - 2}" y="{by - 14}" width="300" height="19"/></clipPath>')
    d.add('<g clip-path="url(#roll)"><g class="roll">')
    for j, s in enumerate(['Code by Rudy', SITE['full_name'], 'Code by Rudy']):
        d.text(s, PAD, by + j * 19, 13, q, 0.012)
    d.add('</g></g>')
    anim, first = living(sag_path, w=W, depth=24 if NARROW else 34, dur=10)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path></g>')
    d.save(f'footer{SUFFIX}-{theme}')


# --- README -------------------------------------------------------------------------------

PHONE = '(max-width: 600px)'


def pic(name, alt, href=None):
    """A themed, responsive image: GitHub picks the variant from the viewer's width and scheme."""
    img = (f'<picture>'
           f'<source media="{PHONE} and (prefers-color-scheme: dark)" srcset="assets/{name}-m-dark.svg">'
           f'<source media="{PHONE}" srcset="assets/{name}-m-light.svg">'
           f'<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
           f'<img src="assets/{name}-light.svg" width="100%" alt="{esc(alt)}"></picture>')
    return f'<a href="{href}">{img}</a>' if href else img


def readme():
    hero_alt = esc(f'{SITE["name"]}, {SITE["role"]}. {SITE["status"]}. ' + '. '.join(SITE['status_lines']) + '.')
    blocks = [
        f'<a href="{SITE["url"]}"><picture><source media="{PHONE}" srcset="assets/hero-m.svg">'
        f'<img src="assets/hero.svg" width="100%" alt="{hero_alt}"></picture></a>',
        pic('statement', STATEMENT + ' ' + ' '.join(t for t, _ in PROOF)),
        pic('how-i-build', 'How I build: ' + ' '.join(f'{s["word"]}. {s["body"]}' for s in BUILD['steps'])),
        pic('selected-work', 'Selected work: ' + '; '.join(f'{p["name"]}, {p["line"]}' for p in FLAGSHIPS),
            SITE['url'] + '/work'),
    ]
    for cat in CATEGORIES:
        rows = '\n'.join(pic(f'p-{p["id"]}', f'{p["name"]}: {p["claim"]} ({p["context"]}, {p["year"]})', p['href'])
                         for p in cat['items'])
        blocks.append(pic(f'cat-{cat["id"]}', f'{cat["name"]}: {cat["line"]}') + '\n' + rows)
        code = [p for p in cat['items'] if p['repo'] and p['href'] != p['repo']]
        if code:
            blocks.append('<sub>Code: ' + ', '.join(f'<a href="{p["repo"]}">{p["name"]}</a>' for p in code) + '</sub>')
    blocks += [
        pic('cat-stack', 'Stack: what these were built with') + '\n' + pic('stack', 'Stack: ' + ', '.join(STACK[0] + STACK[1])),
        pic('along', '; '.join(f'{g["name"]}: ' + ', '.join(f'{a} ({b})' for a, b in g['rows']) for g in ALONG)),
        pic('footer', 'Start a conversation', SITE['url'] + '/contact'),
        f'Write to <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>, or find me on '
        f'<a href="{SITE["linkedin"]}">LinkedIn</a> and <a href="{SITE["telegram"]}">Telegram</a>. '
        f'Case studies live at <a href="{SITE["url"]}">rudhresh.com</a>.',
    ]
    (ROOT / 'README.md').write_text('<!-- Generated by src/build.py from src/content.py. Edit those, not this. -->\n\n'
                                    + '\n\n'.join(blocks) + '\n')


if __name__ == '__main__':
    for f in ASSETS.glob('*.svg'):
        f.unlink()
    readme()
    total = sum(len(c['items']) for c in CATEGORIES)
    for narrow in (False, True):
        layout(narrow)
        hero()
        for theme in THEMES:
            statement(theme)
            how_i_build(theme)
            selected_work(theme)
            marquee(theme)
            category_head(theme, {'id': 'stack', 'name': 'Stack', 'line': 'What these were built with.'}, 0)
            along(theme)
            footer(theme)
            i = 0
            for ci, cat in enumerate(CATEGORIES):
                category_head(theme, cat, ci)
                for p in cat['items']:
                    project_row(theme, p, i, total)
                    i += 1
    print(f'built {len(list(ASSETS.glob("*.svg")))} svgs')
