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

def hero():
    """The loader (Model, System, Product sheets lift in turn), then the name on the stage,
    with the site's chrome ribbon turning behind it. Plays once; the ribbon keeps flowing."""
    H = 480
    d = Doc(W, H, f'{SITE["name"]}. {SITE["role"]}. {SITE["status"]}.')
    clip = f'<clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>'
    d.defs.append(clip)
    d.add('<g clip-path="url(#card)">')
    d.add(f'<rect width="{W}" height="{H}" fill="{STAGE}"/>')

    # Ribbon: 60 transparent frames, one shown at a time, 12 fps, seamless.
    frames = sorted((ROOT / 'src/ribbon').glob('*.webp'))
    box = json.loads((ROOT / 'src/ribbon/box.json').read_text())
    scale = 0.95
    rx, ry = 470 + box['x'] * scale, 40 + box['y'] * scale  # where the uncropped frame would sit
    n = len(frames)
    loop = n / 12
    d.css.append(f'@keyframes f{{0%,{100 / n:.4f}%{{opacity:1}}{100 / n + 0.0001:.4f}%,100%{{opacity:0}}}}'
                 f'.f{{opacity:0;animation:f {loop:.3f}s step-end infinite}}'
                 f'.f0{{opacity:1}}'
                 f'@keyframes ribbon{{from{{opacity:0;transform:translate(24px,40px) scale(.92)}}}}'
                 f'.ribbon{{transform-box:fill-box;transform-origin:50% 50%;animation:ribbon 1.6s {EASE_OUT} 2.5s both}}')
    imgs = []
    for i, f in enumerate(frames):
        data = base64.b64encode(f.read_bytes()).decode()
        imgs.append(f'<image class="f{" f0" if i == 0 else ""}" style="animation-delay:{i * loop / n - loop:.3f}s" '
                    f'width="{box["w"]}" height="{box["h"]}" href="data:image/webp;base64,{data}"/>')
    d.add(f'<g class="ribbon"><g transform="translate({rx} {ry}) scale({scale})">{"".join(imgs)}</g></g>')

    # Name: fitted to the width, letters rise from the middle outward.
    name = SITE['name']
    track = -0.055
    size = (W - 2 * PAD + 6) / (measure(name, 100, track) / 100)
    base = 40 + size * 0.72
    mid = (len(name) - 1) / 2
    d.css.append(rise_css('up', 1.1))
    d.defs.append(f'<clipPath id="namemask"><rect x="0" y="{base - size}" width="{W}" height="{size * 1.2:.0f}"/></clipPath>')
    d.text(name, PAD - 3, base, size, '#ffffff', track, attrs='clip-path="url(#namemask)"',
           each=lambda i, g: f'<g class="up" style="animation-delay:{2.45 + abs(i - mid) * 0.045:.3f}s">{g}</g>')

    # Role, bottom right; status, bottom left.
    d.css.append(f'@keyframes lift{{from{{opacity:0;transform:translateY(14px)}}}}'
                 f'.lift{{animation:lift .9s {EASE_OUT} both}}'
                 f'@keyframes ping{{75%,100%{{transform:scale(2.4);opacity:0}}}}'
                 f'.ping{{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.6s cubic-bezier(0,0,.2,1) infinite}}')
    rsize = 38
    for j, line in enumerate(SITE['role_lines']):
        d.text(line, W - PAD, H - PAD - (len(SITE['role_lines']) - 1 - j) * rsize * 1.02, rsize, '#ffffff', -0.03,
               anchor='end', attrs=f'class="lift" style="animation-delay:{2.85 + j * 0.08:.2f}s"')
    y = H - PAD - 2 * 24
    d.add(f'<g class="lift" style="animation-delay:3.05s"><circle cx="{PAD + 5}" cy="{y - 6}" r="5" fill="{LIVE}"/>'
          f'<circle class="ping" cx="{PAD + 5}" cy="{y - 6}" r="5" fill="{LIVE}"/></g>')
    d.text(SITE['status'], PAD + 20, y, 17, '#ffffff', attrs='class="lift" style="animation-delay:3.05s"')
    for j, line in enumerate(SITE['status_lines']):
        d.text(line, PAD, y + 24 * (j + 1), 17, 'rgba(255,255,255,0.55)', 0.01,
               attrs=f'class="lift" style="animation-delay:{3.13 + j * 0.08:.2f}s"')

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
    wsize = 104
    for k, (word, bg, fg, w_at, at, t) in reversed(list(enumerate(sheets))):
        d.defs.append(f'<clipPath id="wm{k}"><rect y="{H / 2 - wsize * 0.5:.0f}" width="{W}" height="{wsize * 1.12:.0f}"/></clipPath>')
        d.add(f'<g class="sheet" style="--at:{at}s;--t:{t}s">'
              f'<rect width="{W}" height="{H + 1}" fill="{bg}"/>'
              f'<path class="sag" style="--at:{at}s;--t:{t}s" fill="{bg}" d="{sag_path(W, 110, W * 0.54, 0)}" transform="translate(0 {H})"/>')
        d.text(word, W / 2, H / 2 + wsize * 0.36, wsize, fg, -0.045, anchor='middle',
               attrs=f'clip-path="url(#wm{k})"', each=lambda i, g, w=w_at: f'<g class="word" style="--w:{w}s">{g}</g>')
        d.add('</g>')
    d.add('</g>')
    d.save('hero')


def statement(theme):
    t = THEMES[theme]
    size, lh, track = 40, 1.12, -0.03
    lines = wrap(STATEMENT, size, W - 40, track)
    psize = 19
    plines = wrap_rich(PROOF, psize, 600)
    H = int(8 + len(lines) * size * lh + 40 + len(plines) * psize * 1.45 + 8)
    d = Doc(W, H, STATEMENT)
    # Words brighten in reading order, as they do with scroll on the site.
    d.css.append(f'@keyframes lit{{from{{opacity:.16}}}}.lit{{animation:lit .6s ease-out both}}')
    i = 0
    y = 8 + size * 0.8
    for line in lines:
        x = 0
        for word in line.split(' '):
            w = d.text(word, x, y, size, t['ink'], track, attrs=f'class="lit" style="animation-delay:{1.0 + i * 0.09:.2f}s"')
            x += w + measure(' ', size) + track * size
            i += 1
        y += size * lh
    y += 30
    draw_rich(d, plines, 0, y, psize, t, delay=1.0 + i * 0.09 + 0.2)
    d.save(f'statement-{theme}')


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
    t = THEMES[theme]
    col = (W - 2 * PAD - 2 * 28) / 3
    bsize = 15.5
    bodies = [wrap(s['body'], bsize, col - 6) for s in BUILD['steps']]
    H = 0  # set once the columns are laid out
    d = Doc(W, H, 'How I build. ' + ' '.join(f'{s["word"]}: {s["body"]}' for s in BUILD['steps']))
    d.css.append(rise_css('up', 1.1) +
                 f'@keyframes draw{{from{{transform:scaleX(0)}}}}.draw{{transform-box:fill-box;transform-origin:0 0;animation:draw 1.1s {EASE_OUT} both}}'
                 f'@keyframes lift{{from{{opacity:0;transform:translateY(10px)}}}}.lift{{animation:lift .9s {EASE_OUT} both}}')
    y = PAD + 30
    for j, line in enumerate(BUILD['heading']):
        d.defs.append(f'<clipPath id="h{j}"><rect y="{y - 34}" width="{W}" height="44"/></clipPath>')
        d.text(line, PAD, y, 34, t['ink'], -0.03, attrs=f'clip-path="url(#h{j})"',
               each=lambda i, g, j=j: f'<g class="up" style="animation-delay:{0.9 + j * 0.12:.2f}s">{g}</g>')
        y += 38
    top = y + 44
    for k, step in enumerate(BUILD['steps']):
        x = PAD + k * (col + 28)
        at = 1.3 + k * 0.15
        d.add(f'<rect class="draw" style="animation-delay:{at:.2f}s" x="{x}" y="{top}" width="{col:.1f}" height="1" fill="{t["rule"]}"/>')
        d.text(f'0{k + 1}', x, top + 30, 14, muted(t), 0.02, attrs=f'class="lift" style="animation-delay:{at + 0.1:.2f}s"')
        wy = top + 30 + 56
        d.defs.append(f'<clipPath id="w{k}"><rect x="{x - 4}" y="{wy - 46}" width="{col + 8:.0f}" height="58"/></clipPath>')
        d.text(step['word'], x, wy, 46, t['ink'], -0.04, attrs=f'clip-path="url(#w{k})"',
               each=lambda i, g, a=at: f'<g class="up" style="animation-delay:{a + 0.15 + i * 0.025:.3f}s">{g}</g>')
        by = wy + 34
        for line in bodies[k]:
            d.text(line, x, by, bsize, t['ink'], 0.005, attrs=f'class="lift" style="animation-delay:{at + 0.3:.2f}s"')
            by += bsize * 1.5
        d.text('  '.join(step['tools']), x, by + 14, 14, muted(t), 0.015,
               attrs=f'class="lift" style="animation-delay:{at + 0.4:.2f}s"')
        H = max(H, by + 14 + PAD)
    d.h = int(H)
    d.body.insert(0, f'<rect width="{W}" height="{d.h}" fill="{t["band"]}"/>')
    d.save(f'how-i-build-{theme}')


def stage_css():
    return (f'@keyframes lit{{0%,100%{{opacity:.22}}2%,23%{{opacity:1}}27%{{opacity:.22}}}}'
            f'.row{{animation:lit 12s ease-in-out infinite}}')


def selected_work(theme):
    """The stage between two sheets: the page sags into it, rows light one at a time as if
    read by scroll, and the page arches back over it at the end."""
    t = THEMES[theme]
    top_d, bot_d = 46, 40
    rows_y = 150
    rh = 108
    H = rows_y + rh * len(FLAGSHIPS) + 70
    d = Doc(W, H, 'Selected work: ' + '; '.join(f'{p["name"]}, {p["line"]}' for p in FLAGSHIPS))
    d.add(f'<rect width="{W}" height="{H}" fill="{t["stage"]}"/>')
    fg = t['on_stage']
    d.css.append(stage_css())
    q = 'rgba(255,255,255,0.5)' if fg == '#ffffff' else 'rgba(20,21,23,0.5)'
    d.text('Selected work', PAD, top_d + 70, 30, fg, -0.03)
    d.text(f'All {sum(len(c["items"]) for c in CATEGORIES)} on rudhresh.com/work ↗', W - PAD, top_d + 70, 15, q, 0.012, anchor='end')
    n = len(FLAGSHIPS)
    step = 12 / n
    for k, p in enumerate(FLAGSHIPS):
        y = rows_y + k * rh
        d.add(f'<g class="row" style="animation-delay:{k * step - 0.5:.2f}s">')
        d.add(f'<rect x="{PAD}" y="{y}" width="{W - 2 * PAD}" height="1" fill="{q}" opacity=".35"/>')
        d.text(p['name'], PAD - 3, y + 68, 68, fg, -0.045)
        d.text(p['line'], PAD, y + 94, 15.5, q, 0.012)
        d.text(p['label'], W - PAD, y + 40, 15.5, fg, 0.012, anchor='end')
        d.add('</g>')
    # Page sheet sagging in at the top, and arching back over at the bottom.
    anim, first = living(sag_path, w=W, depth=top_d - R, dur=9)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path>')
    anim, first = living(arch_path, w=W, depth=bot_d - R, dur=11, phase=0.4, bottom=H)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path>')
    d.save(f'selected-work-{theme}')


def category_head(theme, cat, index):
    t = THEMES[theme]
    H = 104
    d = Doc(W, H, f'{cat["name"]}: {cat["line"]}')
    d.css.append(rise_css('up', 1.1) + f'@keyframes lift{{from{{opacity:0;transform:translateY(8px)}}}}.lift{{animation:lift .9s {EASE_OUT} both}}')
    base = 62
    d.defs.append(f'<clipPath id="m"><rect y="{base - 40}" width="{W}" height="52"/></clipPath>')
    at = 0.6 + index * 0.1
    w = d.text(cat['name'], 0, base, 40, t['ink'], -0.035, attrs='clip-path="url(#m)"',
               each=lambda i, g: f'<g class="up" style="animation-delay:{at + i * 0.02:.3f}s">{g}</g>')
    if cat.get('items'):
        d.text(str(len(cat['items'])), w + 8, base - 22, 16, t['accent'], 0.01, attrs=f'class="lift" style="animation-delay:{at + 0.3:.2f}s"')
    d.text(cat['line'], W, base, 16, muted(t), 0.012, anchor='end', attrs=f'class="lift" style="animation-delay:{at + 0.2:.2f}s"')
    d.save(f'cat-{cat["id"]}-{theme}')


def project_row(theme, p, index, total):
    """One row of the index: name, claim under it, context and year on the right. A small
    accent arrow lights in a wave that runs down the whole list."""
    t = THEMES[theme]
    csize = 15.5
    claim = wrap(p['claim'], csize, 560, 0.01)
    H = int(26 + 30 + 10 + len(claim) * csize * 1.45 + 18)
    d = Doc(W, H, f'{p["name"]}. {p["claim"]} {p["context"]}, {p["year"]}.')
    period = max(total * 0.35 + 3, 8)
    d.css.append(f'@keyframes in{{from{{opacity:0;transform:translateY(12px)}}}}.in{{animation:in .9s {EASE_OUT} both}}'
                 f'@keyframes wave{{0%,100%{{opacity:.28;transform:translate(0,0)}}4%{{opacity:1;transform:translate(3px,-3px)}}12%{{opacity:.28;transform:translate(0,0)}}}}'
                 f'.wave{{animation:wave {period:.2f}s ease-in-out infinite}}')
    d.add(f'<rect width="{W}" height="1" fill="{t["rule"]}"/>')
    at = 0.8 + index * 0.05
    d.add(f'<g class="in" style="animation-delay:{at:.2f}s">')
    y = 26 + 26
    w = d.text(p['name'], 0, y, 30, t['ink'], -0.03)
    d.text('↗', w + 10, y - 2, 20, t['accent'], attrs=f'class="wave" style="animation-delay:{2 + index * 0.35 - period:.2f}s"')
    cy = y + 30
    for line in claim:
        d.text(line, 0, cy, csize, muted(t), 0.01)
        cy += csize * 1.45
    d.text(p['context'], W, y - 8, csize, t['ink'], 0.01, anchor='end')
    d.text(p['year'], W, y + 16, csize, muted(t), 0.01, anchor='end')
    d.add('</g>')
    d.save(f'p-{p["id"]}-{theme}')


def marquee(theme):
    """The stack, drifting in two directions at display size."""
    t = THEMES[theme]
    H = 150
    d = Doc(W, H, 'Stack: ' + ', '.join(STACK[0] + STACK[1]))
    size = 44
    d.defs.append('<linearGradient id="fade"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                  '<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  f'<mask id="edge"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    d.add('<g mask="url(#edge)">')
    for j, words in enumerate(STACK):
        sep = '   /   '
        line = sep.join(words) + sep
        width = measure(line, size, -0.03)
        reps = math.ceil(W / width) + 1
        dur = width / 26
        d.css.append(f'@keyframes m{j}{{from{{transform:translateX({0 if j == 0 else -width:.1f}px)}}to{{transform:translateX({-width if j == 0 else 0:.1f}px)}}}}'
                     f'.m{j}{{animation:m{j} {dur:.1f}s linear infinite}}')
        y = 56 + j * 64
        d.add(f'<g class="m{j}" style="transform:translateX({-width / 3 if j == 0 else -width * 2 / 3:.1f}px)">')
        for r in range(reps):
            d.text(line, r * width, y, size, t['ink'] if j == 0 else muted(t), -0.03)
        d.add('</g>')
    d.add('</g>')
    d.save(f'stack-{theme}')


def along(theme):
    """Recognition, leadership and one line off the keyboard, as one flush ledger."""
    t = THEMES[theme]
    rh = 58
    groups = ALONG
    H = sum(34 + len(g['rows']) * rh + 30 for g in groups)
    d = Doc(W, H, '; '.join(f'{g["name"]}: ' + ', '.join(f'{a} ({b})' for a, b in g['rows']) for g in groups))
    d.css.append(f'@keyframes in{{from{{opacity:0;transform:translateY(10px)}}}}.in{{animation:in .9s {EASE_OUT} both}}')
    y = 0
    k = 0
    for g in groups:
        d.text(g['name'], 0, y + 20, 15.5, muted(t), 0.012)
        y += 34
        for a, b in g['rows']:
            d.add(f'<g class="in" style="animation-delay:{1 + k * 0.06:.2f}s">')
            d.add(f'<rect y="{y}" width="{W}" height="1" fill="{t["rule"]}"/>')
            d.text(a, 0, y + 37, 21, t['ink'], -0.015)
            d.text(b, W, y + 37, 15.5, muted(t), 0.01, anchor='end')
            d.add('</g>')
            y += rh
            k += 1
        y += 30
    d.save(f'along-{theme}')


def footer(theme):
    """The footer stage: the page's lip sags over it, one closing line, quiet utility."""
    t = THEMES[theme]
    H = 420
    fg = t['on_stage']
    q = 'rgba(255,255,255,0.5)' if fg == '#ffffff' else 'rgba(20,21,23,0.5)'
    d = Doc(W, H, 'Start a conversation: ' + SITE['email'])
    d.defs.append(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>')
    d.add(f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t["stage"]}"/>')
    d.css.append(rise_css('up', 1.1) +
                 '@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(8px)}}'
                 '.nudge{animation:nudge 2.4s ease-in-out infinite}'
                 f'@keyframes ping{{75%,100%{{transform:scale(2.4);opacity:0}}}}'
                 f'.ping{{transform-box:fill-box;transform-origin:50% 50%;animation:ping 1.6s cubic-bezier(0,0,.2,1) infinite}}'
                 # Brand roll: "Code by Rudy" rolls up and the full name rolls in under it, now and then.
                 '@keyframes roll{0%,40%{transform:translateY(0)}48%,90%{transform:translateY(-19px)}98%,100%{transform:translateY(-38px)}}'
                 '.roll{animation:roll 9s cubic-bezier(.65,0,.35,1) infinite}')
    size = 84
    y1 = 150
    for j, line in enumerate(['Start a', 'conversation']):
        yy = y1 + j * size * 0.98
        d.defs.append(f'<clipPath id="c{j}"><rect y="{yy - size * 0.82:.0f}" width="{W}" height="{size * 1.04:.0f}"/></clipPath>')
        w = d.text(line, PAD - 3, yy, size, fg, -0.045, attrs=f'clip-path="url(#c{j})"',
                   each=lambda i, g, j=j: f'<g class="up" style="animation-delay:{1.2 + j * 0.12 + i * 0.02:.3f}s">{g}</g>')
    d.text('→', PAD - 3 + w + 22, yy, size * 0.8, fg, attrs='class="nudge"')
    ly = H - 96
    d.add(f'<rect x="{PAD}" y="{ly}" width="{W - 2 * PAD}" height="1" fill="{q}" opacity=".45"/>')
    x = PAD
    for label in SITE['links']:
        x += d.text(label, x, ly + 34, 15.5, fg, 0.012) + 26
    status = f'{SITE["status"]}, {SITE["focus"]}'
    sw = d.text(status, W - PAD, ly + 34, 15.5, q, 0.012, anchor='end')
    cx = W - PAD - sw - 14
    d.add(f'<circle cx="{cx}" cy="{ly + 29}" r="4.5" fill="{LIVE}"/><circle class="ping" cx="{cx}" cy="{ly + 29}" r="4.5" fill="{LIVE}"/>')
    by = H - 26
    d.defs.append(f'<clipPath id="roll"><rect x="{PAD - 2}" y="{by - 14}" width="300" height="19"/></clipPath>')
    d.add(f'<g clip-path="url(#roll)"><g class="roll">')
    for j, s in enumerate(['Code by Rudy', SITE['full_name'], 'Code by Rudy']):
        d.text(s, PAD, by + j * 19, 13, q, 0.012)
    d.add('</g></g>')
    d.text(SITE['motto'], W - PAD, by, 13, q, 0.012, anchor='end')
    anim, first = living(sag_path, w=W, depth=34, dur=10)
    d.add(f'<path fill="{t["page"]}" d="{first}">{anim}</path>')
    d.add('</g>')
    d.save(f'footer-{theme}')


def pic(name, alt, href=None):
    """A themed image: GitHub picks the variant from the viewer's colour scheme."""
    img = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">'
           f'<img src="assets/{name}-light.svg" width="100%" alt="{esc(alt)}"></picture>')
    return f'<a href="{href}">{img}</a>' if href else img


def readme():
    blocks = [
        f'<a href="{SITE["url"]}"><img src="assets/hero.svg" width="100%" '
        f'alt="{esc(SITE["name"] + ", " + SITE["role"] + ". " + SITE["status"] + ". " + ". ".join(SITE["status_lines"]))}."></a>',
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
    readme()
    hero()
    total = sum(len(c['items']) for c in CATEGORIES)
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
