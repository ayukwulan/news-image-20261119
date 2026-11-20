#!/usr/bin/env python3
"""Draw the front page for news-image-20261119.

Renders entry.png (1024x1024): a dense broadsheet front page — masthead
with a story count, 3 big leads, a numbered 6-story grid with REGION x BEAT
tags, a BY THE NUMBERS strip, a dotted world map with numbered pins, and
16 one-line briefs continuing the numbering (25 stories in total).
Everything is drawn with PIL shapes; no photographs, no network.
Run: python3 draw.py  (writes entry.png next to this file)
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (253, 251, 243)      # warm off-white
INK = (17, 17, 17)           # near-black
RED = (176, 30, 30)          # middle east
BLUE = (31, 80, 150)         # europe
GREEN = (27, 120, 70)        # asia
ORANGE = (198, 102, 18)      # americas
BROWN = (120, 72, 40)        # africa
TEAL = (14, 120, 120)        # oceania
PURPLE = (110, 60, 150)      # global
GREY = (90, 90, 88)
SEA = (186, 211, 228)
LAND = (232, 220, 192)
LAND_LINE = (150, 135, 100)
BOX = (242, 238, 228)        # number-strip box fill

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MX = 32                      # side margin
RW = W - 2 * MX              # content width (960)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, path, start, max_w):
    """Largest font size (<= start) at which text fits max_w."""
    size = start
    while size > 8:
        fnt = ImageFont.truetype(path, size)
        if fnt.getlength(text) <= max_w:
            return fnt
        size -= 1
    return ImageFont.truetype(path, 8)


def draw_para(d, x, y, lines, fnt, fill=INK, leading=None):
    """Draw wrapped lines; returns y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(text, path, start, max_w, max_lines):
    """Largest font size (<= start) at which text wraps to <= max_lines."""
    size = start
    while size > 8:
        fnt = ImageFont.truetype(path, size)
        if len(wrap(text, fnt, max_w)) <= max_lines:
            return fnt
        size -= 1
    return ImageFont.truetype(path, 8)


def burst(d, cx, cy, r, fill=RED):
    """8-point starburst (explosion marker)."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=INK)


def label(d, x, y, text, fnt, fill=INK, halo=(255, 255, 255)):
    """Small label with a white halo so it stays legible over art."""
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((x + dx, y + dy), text, font=fnt, fill=halo)
    d.text((x, y), text, font=fnt, fill=fill)


# ------------------------------------------------------------------ icons
def icon_scales(d, x, y, s=28):
    """Scales of justice."""
    d.line([(x + s // 2, y + 2), (x + s // 2, y + s - 4)], fill=INK, width=2)
    d.line([(x + 3, y + 6), (x + s - 3, y + 6)], fill=INK, width=2)
    d.ellipse([x + s // 2 - 3, y + 1, x + s // 2 + 3, y + 7], fill=INK)
    for cx in (x + 4, x + s - 4):
        d.line([(cx, y + 6), (cx - 5, y + 16)], fill=INK, width=1)
        d.line([(cx, y + 6), (cx + 5, y + 16)], fill=INK, width=1)
        d.arc([cx - 6, y + 14, cx + 6, y + 24], 0, 180, fill=INK, width=2)
    d.line([(x + 4, y + s - 2), (x + s - 4, y + s - 2)], fill=INK, width=2)


def icon_capitol(d, x, y, s=28):
    d.polygon([(x + s // 2, y + 1), (x + 4, y + 8), (x + s - 4, y + 8)],
              outline=INK, width=2)
    d.arc([x + s // 2 - 5, y + 1, x + s // 2 + 5, y + 10], 180, 360,
          fill=INK, width=2)
    for cx in (x + 6, x + s // 2, x + s - 6):
        d.line([(cx, y + 10), (cx, y + s - 6)], fill=INK, width=2)
    d.line([(x + 1, y + s - 4), (x + s - 1, y + s - 4)], fill=INK, width=2)


def icon_bridge(d, x, y, s=28):
    d.line([(x + 4, y + 20), (x + 4, y + 4)], fill=INK, width=2)
    d.line([(x + s - 4, y + 20), (x + s - 4, y + 4)], fill=INK, width=2)
    d.line([(x + 4, y + 8), (x + s // 2 - 3, y + 8)], fill=INK, width=2)
    d.line([(x + s // 2 + 3, y + 12), (x + s - 4, y + 9)], fill=INK,
           width=2)
    d.line([(x + 2, y + 20), (x + s - 2, y + 20)], fill=INK, width=2)
    burst(d, x + s // 2, y + 10, 5)


def icon_satellite(d, x, y, s=28):
    d.rectangle([x + 10, y + 10, x + 18, y + 18], fill=INK)
    d.rectangle([x + 1, y + 8, x + 9, y + 20], outline=INK, width=2)
    d.rectangle([x + 19, y + 8, x + 27, y + 20], outline=INK, width=2)
    d.line([(x + 14, y + 18), (x + 20, y + 26)], fill=INK, width=2)
    d.line([(x + 20, y + 26), (x + 26, y + 22)], fill=INK, width=2)


def icon_controller(d, x, y, s=28):
    d.rounded_rectangle([x + 1, y + 6, x + s - 1, y + s - 6], radius=6,
                        outline=INK, width=2)
    d.line([(x + 7, y + 13), (x + 11, y + 13)], fill=INK, width=2)
    d.line([(x + 9, y + 11), (x + 9, y + 15)], fill=INK, width=2)
    d.ellipse([x + 17, y + 11, x + 20, y + 14], fill=RED)
    d.ellipse([x + 21, y + 15, x + 24, y + 18], fill=INK)


def icon_cyclone(d, x, y, s=28):
    d.arc([x + 2, y + 2, x + s - 2, y + s - 2], 0, 300, fill=INK, width=2)
    d.arc([x + 7, y + 7, x + s - 7, y + s - 7], 120, 420, fill=INK, width=2)
    d.ellipse([x + s // 2 - 3, y + s // 2 - 3, x + s // 2 + 3,
               y + s // 2 + 3], fill=RED)


# ------------------------------------------------------- lead illustrations
def ill_gulf(d, x, y, w, h):
    """Schematic Strait of Hormuz: sea, two shores, three bursts."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=INK, width=2)
    # northern shore (Iran / Qeshm)
    d.polygon([(x, y), (x + w, y), (x + w, y + 24), (x + 252, y + 34),
               (x + 172, y + 26), (x + 82, y + 38), (x, y + 30)],
              fill=LAND, outline=LAND_LINE)
    # southern shore (Arabian peninsula)
    d.polygon([(x, y + h), (x, y + 60), (x + 56, y + 52), (x + 102, y + 64),
               (x + 120, y + h)],
              fill=LAND, outline=LAND_LINE)
    # Qeshm island + Bahrain islet
    d.ellipse([x + 228, y + 36, x + 262, y + 46], fill=LAND,
              outline=LAND_LINE)
    d.ellipse([x + 148, y + 50, x + 160, y + 60], fill=LAND,
              outline=LAND_LINE)
    burst(d, x + 245, y + 41, 8)
    burst(d, x + 62, y + 58, 7)
    burst(d, x + 154, y + 55, 7)
    lab = font(F_SANS_B, 10)
    label(d, x + 252, y + 24, "QESHM", lab)
    label(d, x + 6, y + 44, "KUWAIT", lab)
    label(d, x + 162, y + 42, "BAHRAIN", lab)


def ill_summit(d, x, y, w, h):
    """Three leaders at a summit table: US, China, Russia flags."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=2)
    # three figures: heads + shoulders
    cols = [(40, 60, 90), (176, 30, 30), (90, 40, 40)]
    for i, col in enumerate(cols):
        cx = x + 52 + i * 100
        d.ellipse([cx - 15, y + 8, cx + 15, y + 38],
                  fill=(222, 190, 160), outline=INK, width=2)
        d.pieslice([cx - 29, y + 36, cx + 29, y + 66], 180, 360,
                   fill=col, outline=INK, width=2)
    # table
    d.rectangle([x + 20, y + 52, x + w - 20, y + 62], fill=(150, 110, 70),
                outline=INK, width=2)
    # three small flags on the table: USA, China, Russia
    fx = x + w // 2 - 45
    d.rectangle([fx, y + 26, fx + 26, y + 42], fill=(255, 255, 255),
                outline=INK, width=1)
    for yy in range(y + 27, y + 42, 4):
        d.line([(fx + 1, yy), (fx + 25, yy)], fill=(200, 30, 30), width=1)
    d.rectangle([fx, y + 26, fx + 11, y + 33], fill=(40, 60, 140))
    fx = x + w // 2 - 13
    d.rectangle([fx, y + 26, fx + 26, y + 42], fill=(222, 30, 30),
                outline=INK, width=1)
    d.text((fx + 5, y + 29), "\u2605", font=font(F_SANS, 9),
           fill=(255, 220, 0))
    fx = x + w // 2 + 19
    d.rectangle([fx, y + 26, fx + 26, y + 42], outline=INK, width=1)
    d.rectangle([fx, y + 26, fx + 26, y + 31], fill=(255, 255, 255))
    d.rectangle([fx, y + 31, fx + 26, y + 36], fill=(0, 60, 180))
    d.rectangle([fx, y + 36, fx + 26, y + 42], fill=(220, 30, 30))
    lab = font(F_SANS_B, 10)
    label(d, x + 8, y + 64, "KYLIN VILLA · SHENZHEN", lab)


def ill_ipo(d, x, y, w, h):
    """A share-price chart rocketing up, with the ANT ticker box."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=2)
    # grid
    for gy in (y + 18, y + 38, y + 58):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(210, 205, 195), width=1)
    # rising line: flat, then a steep climb
    pts = [(x + 14, y + 62), (x + 70, y + 58), (x + 120, y + 56),
           (x + 160, y + 44), (x + 200, y + 30), (x + 240, y + 16),
           (x + 282, y + 8)]
    d.line(pts, fill=GREEN, width=4)
    # arrowhead
    d.polygon([(x + 282, y + 8), (x + 268, y + 6), (x + 276, y + 20)],
              fill=GREEN)
    # ticker box
    d.rectangle([x + 14, y + 10, x + 76, y + 30], fill=INK)
    d.text((x + 45, y + 20), "ANT", font=font(F_SANS_B, 14),
           fill=(255, 255, 255), anchor="mm")
    lab = font(F_SANS_B, 10)
    label(d, x + 196, y + 60, "$81.3bn", lab, fill=GREEN)


# ------------------------------------------------------------- world map
def point_in_poly(px, py, poly):
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (
                px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# Simplified continent outlines in a 608 x 124 map box.
CONTINENTS = [
    # North America
    [(18, 18), (95, 8), (150, 14), (168, 34), (150, 62), (118, 74),
     (80, 72), (38, 52), (14, 34)],
    # Greenland
    [(150, 6), (172, 4), (178, 12), (160, 16)],
    # South America
    [(168, 78), (205, 72), (228, 92), (216, 118), (190, 122), (172, 100)],
    # Europe
    [(300, 14), (338, 8), (356, 22), (344, 44), (312, 48), (294, 30)],
    # Africa
    [(300, 52), (348, 46), (372, 68), (356, 104), (322, 112), (298, 84)],
    # Asia
    [(360, 8), (540, 4), (590, 18), (586, 44), (540, 60), (492, 66),
     (448, 58), (404, 44), (366, 30)],
    # SE Asia islands
    [(470, 66), (490, 62), (500, 74), (480, 78)],
    # Australia
    [(492, 88), (556, 84), (572, 100), (540, 116), (498, 112)],
]


def draw_world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 244, 248), outline=INK,
                width=2)
    step = 7
    for gx in range(4, w - 2, step):
        for gy in range(4, h - 2, step):
            if any(point_in_poly(gx, gy, poly) for poly in CONTINENTS):
                d.ellipse([x + gx - 2, y + gy - 2, x + gx + 2, y + gy + 2],
                          fill=(70, 70, 70))
    # pins: (number, local x, local y, colour)
    pins = [
        (1, 522, 54, GREEN),    # Shenzhen
        (2, 470, 42, RED),      # Gulf
        (3, 126, 28, ORANGE),   # New York
        (4, 308, 28, BLUE),     # The Hague
        (5, 146, 46, ORANGE),   # Washington
        (6, 352, 32, BLUE),     # Kerch
        (9, 478, 64, GREEN),    # Gopalpur / Odisha
    ]
    nf = font(F_SANS_B, 11)
    for num, px, py, col in pins:
        d.ellipse([x + px - 9, y + py - 9, x + px + 9, y + py + 9],
                  fill=col, outline=INK, width=1)
        d.text((x + px, y + py), str(num), font=nf, fill=(255, 255, 255),
               anchor="mm")


# ------------------------------------------------------------------ page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.text((W // 2, 8), "THE WORLD TODAY", font=font(F_SERIF_B, 54),
           fill=INK, anchor="ma")
    d.text((W // 2, 66), "25 STORIES \u00b7 6 CONTINENTS \u00b7 ONE PAGE",
           font=font(F_SANS_B, 20), fill=RED, anchor="ma")
    d.text((W // 2, 90),
           "Everything on this page happened, or was first reported, on "
           "Thursday 19 November 2026.",
           font=font(F_SERIF, 15), fill=GREY, anchor="ma")
    d.line([(MX, 110), (W - MX, 110)], fill=INK, width=3)
    d.line([(MX, 115), (W - MX, 115)], fill=INK, width=1)

    # ---- black date band ----------------------------------------------
    d.rectangle([MX, 122, W - MX, 148], fill=INK)
    d.text((W // 2, 135), "THURSDAY 19 NOVEMBER 2026",
           font=font(F_SANS_B, 21), fill=(255, 255, 255), anchor="mm")

    # ---- 3 leads -------------------------------------------------------
    lead_xs = [MX, MX + 304 + 24, MX + 2 * (304 + 24)]
    leads = [
        ("ASIA \u00b7 SUMMIT", GREEN, "THREE POWERS, ONE PEACE PLEDGE",
         ill_summit,
         "First trio meeting \u2014 90 minutes at Kylin Villa. A "
         "four-point \u201cDeclaration Towards Peace\u201d: no nuclear "
         "war, nuclear-risk talks, more oil, UN reform, an ICC "
         "warning. No Ukraine deal."),
        ("MIDDLE EAST \u00b7 GULF WAR", RED, "IRAN WIDENS GULF ATTACKS",
         ill_gulf,
         "Iran\u2019s drones hit Ali Al Salem in Kuwait and Bahrain "
         "again \u2014 both intercepted. An ADNOC tanker was hit in "
         "Hormuz: one missing, 11 hurt. 3 US carriers in the "
         "region."),
        ("BUSINESS \u00b7 TECH IPO", PURPLE, "ANTHROPIC\u2019S $81.3BN DEBUT",
         ill_ipo,
         "The Claude-maker prices the biggest IPO in history \u2014 "
         "980m shares at $83, raising $81.3bn. Shares open Thursday "
         "as ANT at $111.50, valuing it at about $1.5tn."),
    ]
    for i, (tag, col, head, ill, summ) in enumerate(leads):
        lx = lead_xs[i]
        d.text((lx, 156), tag, font=font(F_SANS_B, 13), fill=col)
        hf = fit_lines(head, F_SERIF_B, 26, 304, 2)
        hlines = wrap(head, hf, 304)
        hy = 176
        for ln in hlines:
            d.text((lx, hy), ln, font=hf, fill=INK)
            hy += 28
        ill(d, lx, 232, 304, 76)
        slines = wrap(summ, font(F_SERIF, 13), 304)
        draw_para(d, lx, 314, slines, font(F_SERIF, 13), leading=15)

    d.line([(MX, 376), (W - MX, 376)], fill=INK, width=2)

    # ---- numbered grid, stories 4-9 -----------------------------------
    stories = [
        (4, "ASIA \u00b7 JUSTICE", GREEN, "MYANMAR GUILTY OF GENOCIDE",
         icon_scales,
         "ICJ finds Myanmar guilty of genocide \u2014 the first state "
         "ever convicted. 2017 crackdown: ~10,000 killed, 800,000 "
         "fled."),
        (5, "NORTH AMERICA \u00b7 POLITICS", ORANGE,
         "JEFFRIES FOR SPEAKER",
         icon_capitol,
         "House Democrats vote 251-11; first Black Speaker nominee. "
         "Floor vote Jan 3. Lieu is the first Asian American caucus "
         "chair."),
        (6, "EUROPE \u00b7 UKRAINE WAR", BLUE, "KERCH BRIDGE HIT AGAIN",
         icon_bridge,
         "Neptune missiles hit the rail section \u2014 third strike "
         "in four days. Rail halted, one track reopened; EU offers "
         "\u20ac45bn."),
        (7, "GLOBAL \u00b7 SCIENCE", PURPLE, "VOYAGER 1, ONE LIGHT-DAY OUT",
         icon_satellite,
         "First object one light-day from Earth \u2014 25.9bn km. "
         "Crossed Wed 5:16am EST; its signal takes 24 hours to "
         "arrive."),
        (8, "GLOBAL \u00b7 CULTURE", PURPLE, "GTA VI LANDS TODAY",
         icon_controller,
         "Launches today on PS5 and Xbox at $79.99. Back to Vice "
         "City with Jason and Lucia; ~14.9m pre-orders worth "
         "$1.45bn."),
        (9, "ASIA \u00b7 WEATHER", GREEN, "CYCLONE AKVAN BEARS DOWN",
         icon_cyclone,
         "Severe cyclone in the Bay of Bengal. Landfall near "
         "Gopalpur around noon Fri; winds 90-100 km/h. 72,000 "
         "evacuated."),
    ]
    cell_w, cell_h = 304, 97
    for i, (num, tag, col, head, icon, summ) in enumerate(stories):
        cx = lead_xs[i % 3]
        cy = 384 + (i // 3) * (cell_h + 8)
        # number badge
        d.ellipse([cx, cy, cx + 24, cy + 24], fill=col, outline=INK,
                  width=1)
        d.text((cx + 12, cy + 12), str(num), font=font(F_SANS_B, 13),
               fill=(255, 255, 255), anchor="mm")
        d.text((cx + 30, cy + 4), tag, font=font(F_SANS_B, 11), fill=col)
        # headline, fitted to the space left of the icon
        hf = fit_font(head, F_SERIF_B, 17, 264)
        d.text((cx, cy + 28), head, font=hf, fill=INK)
        icon(d, cx + 272, cy + 26, 28)
        slines = wrap(summ, font(F_SERIF, 12), 304)
        draw_para(d, cx, cy + 52, slines[:3], font(F_SERIF, 12),
                  leading=15)

    d.line([(MX, 590), (W - MX, 590)], fill=INK, width=1)

    # ---- BY THE NUMBERS strip -----------------------------------------
    box_w, box_h = 228, 60
    numbers = [
        ("$81.3bn", "ANTHROPIC IPO, BIGGEST EVER"),
        ("9\u20136", "ICJ VOTE: MYANMAR GUILTY"),
        ("25.9bn km", "VOYAGER 1 FROM EARTH"),
        ("$190.4m", "VAN GOGH AUCTION RECORD"),
    ]
    for i, (big, small) in enumerate(numbers):
        bx = MX + i * (228 + 16)
        d.rectangle([bx, 598, bx + box_w, 598 + box_h], fill=BOX,
                    outline=INK, width=2)
        bf = fit_font(big, F_SERIF_B, 28, box_w - 16)
        d.text((bx + box_w // 2, 606), big, font=bf, fill=INK, anchor="ma")
        d.text((bx + box_w // 2, 636), small, font=font(F_SANS_B, 11),
               fill=GREY, anchor="ma")

    # ---- WHERE IT HAPPENED map + legend --------------------------------
    d.text((MX, 664), "WHERE IT HAPPENED", font=font(F_SANS_B, 16),
           fill=INK)
    d.text((W - MX, 664), "PINS MARK STORIES 1\u20136, 9",
           font=font(F_SANS_B, 11), fill=GREY, anchor="ra")
    draw_world_map(d, MX, 686, 608, 122)
    # legend
    lx = 656
    d.text((lx, 686), "REGIONS", font=font(F_SANS_B, 13), fill=INK)
    legend = [
        (RED, "MIDDLE EAST \u2014 2"),
        (BLUE, "EUROPE \u2014 4, 6"),
        (GREEN, "ASIA \u2014 1, 9"),
        (ORANGE, "AMERICAS \u2014 3, 5"),
        (BROWN, "AFRICA \u2014 briefs 23, 24"),
        (TEAL, "OCEANIA \u2014 brief 20"),
        (PURPLE, "GLOBAL \u2014 7, 8 (no pin)"),
    ]
    ly = 702
    for col, txt in legend:
        d.rectangle([lx, ly + 1, lx + 12, ly + 13], fill=col, outline=INK,
                    width=1)
        d.text((lx + 18, ly), txt, font=font(F_SANS_B, 12), fill=INK)
        ly += 16

    d.line([(MX, 818), (W - MX, 818)], fill=INK, width=1)

    # ---- briefs 10-25 ---------------------------------------------------
    d.text((MX, 824), "ALSO ON THURSDAY 19 NOVEMBER \u2014 16 MORE STORIES",
           font=font(F_SANS_B, 15), fill=INK)
    briefs = [
        (10, "GAZA", "Israel ends Gaza raid across the Yellow Line; 3 killed."),
        (11, "NEW YORK", "Van Gogh sells for a record $190.4m at Sotheby\u2019s."),
        (12, "BERLIN", "Coalition of the Willing backs Europe\u2019s seat at peace talks."),
        (13, "UKRAINE", "US Patriot deliveries cut 3-4x; UK pledges \u00a3260m in aid."),
        (14, "OIL", "Brent $92.12: Hormuz mines and Houthi missiles vs surplus."),
        (15, "WASHINGTON", "Fed minutes: more hikes likely; 50bp Dec move eyed."),
        (16, "GLOBAL", "Pew: Islam to pass Christianity as largest faith by 2035."),
        (17, "TOKYO", "India and Japan deepen defence ties at 2+2 talks."),
        (18, "TAIPEI", "TSMC, Samsung halt some chip shipments to China."),
        (19, "OTTAWA", "Carney plays the China card; US deal \u201cnot there yet\u201d."),
        (20, "WELLINGTON", "Court: pay-equity overhaul breached women\u2019s rights."),
        (21, "KYIV", "Russian barrage damages Austrian and Dutch missions."),
        (22, "MIAMI", "Trump invites Putin to the December G20 summit."),
        (23, "NAIROBI", "US group wins huge Kenya mining deal over China."),
        (24, "KHARTOUM", "Sudan court gives Hemedti a 2nd death sentence."),
        (25, "NASDAQ", "Anthropic opens $111.50, +34%, briefly past $2tn."),
    ]
    bf_num = font(F_SANS_B, 12)
    bf_place = font(F_SERIF_B, 12)
    bf_txt = font(F_SERIF, 12)
    by = 846
    for j, (num, place, txt) in enumerate(briefs):
        bx = MX if j < 8 else MX + 492
        row = j % 8
        yy = by + row * 19
        d.text((bx, yy), "%d." % num, font=bf_num, fill=RED)
        d.text((bx + 26, yy), place + " \u2014 ", font=bf_place, fill=INK)
        pw = bf_place.getlength(place + " \u2014 ")
        d.text((bx + 26 + pw, yy), txt, font=bf_txt, fill=INK)

    # ---- foot ----------------------------------------------------------
    d.line([(MX, 994), (W - MX, 994)], fill=INK, width=1)
    d.text((W // 2, 1002),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera "
           "\u00b7 CNN \u00b7 Bloomberg \u00b7 IMD \u00b7 NASA",
           font=font(F_SERIF, 13), fill=GREY, anchor="ma")

    img.save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
