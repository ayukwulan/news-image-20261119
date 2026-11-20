#!/usr/bin/env python3
"""Draw the 19 November 2026 front page: THE WORLD TODAY.

Fresh implementation. Renders a 1024x1024 newspaper front page with a
masthead, three illustrated lead stories, six second-tier stories, a
BY THE NUMBERS strip, a dotted world map with numbered pins, and a
two-column briefs list covering stories 10-25.
"""

import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 244, 236)
INK = (17, 17, 17)
GREY = (110, 108, 100)
RED = (176, 30, 36)
RULE = (60, 60, 60)
BOX = (232, 228, 218)
SKY = (214, 230, 240)
SAND = (238, 226, 196)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, leading, fill=INK):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centre(draw, cx, y, text, fnt, fill=INK):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def hline(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def dot_grid_land(cx, cy, rx, ry, gx, gy):
    """True when grid point (gx, gy) falls inside the ellipse."""
    if rx <= 0 or ry <= 0:
        return False
    return ((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2 <= 1.0


# Region colours.
C_MIDEAST = (192, 57, 43)
C_EUROPE = (44, 90, 160)
C_ASIA = (30, 125, 70)
C_AMERICAS = (211, 84, 0)
C_AFRICA = (139, 90, 43)
C_OCEANIA = (14, 124, 123)
C_GLOBAL = (125, 60, 152)

LEADS = [
    {
        "num": 1, "tag": "ASIA · SUMMIT", "colour": C_ASIA,
        "head": "THREE POWERS,\nONE PEACE PLEDGE",
        "art": "summit",
        "body": ("First trio meeting \u2014 90 minutes at Kylin Villa. "
                 "A four-point \u201cDeclaration Towards Peace\u201d: no "
                 "nuclear war, nuclear-risk talks, more oil, UN reform. "
                 "No Ukraine deal."),
    },
    {
        "num": 2, "tag": "MIDDLE EAST · GULF WAR", "colour": C_MIDEAST,
        "head": "IRAN WIDENS GULF\nATTACKS",
        "art": "gulf",
        "body": ("Iran\u2019s drones hit Ali Al Salem in Kuwait and "
                 "Bahrain again \u2014 both intercepted. An ADNOC tanker "
                 "was hit in Hormuz: one missing, 11 hurt. "
                 "3 US carriers in the region."),
    },
    {
        "num": 3, "tag": "BUSINESS · TECH IPO", "colour": C_GLOBAL,
        "head": "ANTHROPIC\u2019S\n$81.3bn DEBUT",
        "art": "chart",
        "body": ("The Claude-maker prices the biggest IPO in history "
                 "\u2014 980m shares at $83, raising $81.3bn. Shares open "
                 "Thursday as ANT at $111.50, valuing it near $1.5tn."),
    },
]

SECOND = [
    {
        "num": 4, "tag": "ASIA · JUSTICE", "colour": C_ASIA,
        "head": "MYANMAR GUILTY OF GENOCIDE",
        "icon": "scales",
        "body": ("ICJ finds Myanmar guilty of genocide \u2014 the first "
                 "state ever convicted. 2017 crackdown: ~10,000 killed, "
                 "800,000 fled."),
    },
    {
        "num": 5, "tag": "NORTH AMERICA · POLITICS", "colour": C_AMERICAS,
        "head": "JEFFRIES FOR SPEAKER",
        "icon": "dome",
        "body": ("House Democrats vote 251\u201311; first Black Speaker "
                 "nominee. Floor vote Jan 3. Lieu is the first Asian "
                 "American caucus chair."),
    },
    {
        "num": 6, "tag": "EUROPE · UKRAINE WAR", "colour": C_EUROPE,
        "head": "KERCH BRIDGE HIT AGAIN",
        "icon": "bridge",
        "body": ("Neptune missiles hit the rail section \u2014 third "
                 "strike in four days. Rail halted, one track reopened; "
                 "EU offers \u20ac45bn."),
    },
    {
        "num": 7, "tag": "GLOBAL · SCIENCE", "colour": C_GLOBAL,
        "head": "VOYAGER 1, ONE LIGHT-DAY OUT",
        "icon": "rocket",
        "body": ("First object one light-day from Earth \u2014 25.9bn km. "
                 "Crossed Wed 5:16am EST; its signal takes 24 hours to "
                 "arrive."),
    },
    {
        "num": 8, "tag": "GLOBAL · CULTURE", "colour": C_GLOBAL,
        "head": "GTA VI LANDS TODAY",
        "icon": "pad",
        "body": ("Launches today on PS5 and Xbox at $79.99. Back to Vice "
                 "City with Jason and Lucia; ~14.9m pre-orders worth "
                 "$1.45bn."),
    },
    {
        "num": 9, "tag": "ASIA · WEATHER", "colour": C_ASIA,
        "head": "CYCLONE AKVAN BEARS DOWN",
        "icon": "storm",
        "body": ("Severe cyclone in the Bay of Bengal. Landfall near "
                 "Gopalpur around noon Fri; winds 90\u2013100 km/h, "
                 "72,000 evacuated."),
    },
]

BRIEFS = [
    (10, "GAZA", "Israel ends Gaza raid across the Yellow Line; 3 killed."),
    (11, "NEW YORK", "Van Gogh sells for a record $190.4m at Sotheby\u2019s."),
    (12, "BERLIN", "Coalition of the Willing backs Europe\u2019s seat at talks."),
    (13, "UKRAINE", "US Patriot deliveries cut 3\u20134x; UK pledges \u00a3260m."),
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

NUMBERS = [
    ("$81.3bn", "ANTHROPIC IPO, BIGGEST EVER"),
    ("9\u20136", "ICJ VOTE: MYANMAR GUILTY"),
    ("25.9bn km", "VOYAGER 1 FROM EARTH"),
    ("$190.4m", "VAN GOGH AUCTION RECORD"),
]

# Landmasses for the dotted map, as ellipses in map-local coordinates.
LAND = [
    (95, 28, 88, 21),    # North America
    (28, 20, 26, 12),    # Alaska
    (152, 10, 20, 10),   # Greenland
    (148, 84, 34, 32),   # South America
    (330, 25, 36, 18),   # Europe
    (342, 72, 42, 37),   # Africa
    (468, 34, 112, 28),  # Asia
    (522, 67, 30, 16),   # SE Asia
    (452, 64, 18, 19),   # India
    (560, 95, 36, 14),   # Australia
    (596, 105, 14, 8),   # New Zealand
]

# (story number, map x, map y, colour) — pins for stories 1-6 and 9.
PINS = [
    (1, 505, 46, C_ASIA),
    (2, 418, 52, C_MIDEAST),
    (3, 105, 33, C_AMERICAS),
    (4, 326, 25, C_EUROPE),
    (5, 135, 51, C_AMERICAS),
    (6, 356, 28, C_EUROPE),
    (9, 470, 62, C_ASIA),
]

LEGEND = [
    ("MIDDLE EAST \u2014 2", C_MIDEAST),
    ("EUROPE \u2014 4, 6", C_EUROPE),
    ("ASIA \u2014 1, 9", C_ASIA),
    ("AMERICAS \u2014 3, 5", C_AMERICAS),
    ("AFRICA \u2014 briefs 23, 24", C_AFRICA),
    ("OCEANIA \u2014 brief 20", C_OCEANIA),
    ("GLOBAL \u2014 7, 8 (no pin)", C_GLOBAL),
]


def draw_badge(draw, cx, cy, num, colour, r=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    label = str(num)
    fnt = font(SANS_B, 13 if num < 10 else 11)
    tw = draw.textlength(label, font=fnt)
    draw.text((cx - tw / 2, cy - r + 2), label, font=fnt, fill=(255, 255, 255))


def draw_summit(draw, x, y, w, h):
    """Three leaders seated at a table, three small flags between them."""
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    table_y = y + h - 22
    # Figures: head + shoulders.
    for fx, suit in ((x + 38, (30, 60, 120)), (x + w - 38, (90, 40, 40))):
        draw.ellipse([fx - 15, y + 14, fx + 15, y + 44], fill=(232, 190, 150))
        draw.pieslice([fx - 26, y + 42, fx + 26, y + 78], 180, 360, fill=suit)
    # Table.
    draw.rectangle([x + 8, table_y, x + w - 8, table_y + 7], fill=(120, 84, 50))
    # Three flags on the table: US, China, Russia.
    flags = [
        ((200, 40, 50), (255, 255, 255)),
        ((222, 30, 30), (255, 215, 0)),
        ((255, 255, 255), (0, 60, 160)),
    ]
    fx = x + w // 2 - 33
    for c1, c2 in flags:
        draw.rectangle([fx, table_y - 16, fx + 18, table_y - 4], fill=c1)
        draw.rectangle([fx, table_y - 10, fx + 18, table_y - 4], fill=c2)
        fx += 24
    draw.text((x + 8, y + h - 14), "KYLIN VILLA \u00b7 SHENZHEN",
              font=font(SANS_B, 10), fill=INK)


def draw_gulf(draw, x, y, w, h):
    """Stylised Gulf: sand above, sea below, blast marks, labels."""
    draw.rectangle([x, y, x + w, y + h], fill=SAND)
    draw.polygon([(x, y + 34), (x + w, y + 22), (x + w, y + h), (x, y + h)],
                 fill=SKY)
    draw.line([(x, y + 34), (x + w, y + 22)], fill=(120, 140, 160), width=2)
    for bx, by in ((x + 72, y + 60), (x + 158, y + 54), (x + 252, y + 44)):
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            draw.line([(bx, by),
                       (bx + 11 * math.cos(rad), by + 11 * math.sin(rad))],
                      fill=(200, 40, 30), width=2)
        draw.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(200, 40, 30))
    fnt = font(SANS_B, 11)
    draw.text((x + 10, y + 42), "KUWAIT", font=fnt, fill=INK)
    draw.text((x + 175, y + 58), "BAHRAIN", font=fnt, fill=INK)
    draw.text((x + 238, y + 26), "QESHM", font=fnt, fill=INK)


def draw_chart(draw, x, y, w, h):
    """Rising IPO line chart with an ANT label and a value tag."""
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    base = y + h - 26
    pts = [(x + 12, base - 6), (x + 70, base - 10), (x + 130, base - 12),
           (x + 180, base - 34), (x + 235, base - 52), (x + 285, base - 66)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(20, 120, 60), width=3)
    ex, ey = pts[-1]
    draw.polygon([(ex - 2, ey - 12), (ex + 12, ey - 2), (ex - 2, ey + 2)],
                 fill=(20, 120, 60))
    draw.rectangle([x + 12, y + 10, x + 66, y + 32], fill=INK)
    draw.text((x + 20, y + 14), "ANT", font=font(SANS_B, 14),
              fill=(255, 255, 255))
    draw.text((x + w - 62, y + h - 18), "$81.3bn",
              font=font(SANS_B, 12), fill=(20, 120, 60))


def draw_icon(draw, kind, x, y, size=30):
    """Small glyph drawn next to a second-tier headline."""
    if kind == "scales":
        draw.line([(x + 15, y + 2), (x + 15, y + 26)], fill=INK, width=2)
        draw.line([(x + 3, y + 6), (x + 27, y + 6)], fill=INK, width=2)
        draw.arc([x + 1, y + 6, x + 13, y + 18], 0, 180, fill=INK, width=2)
        draw.arc([x + 17, y + 6, x + 29, y + 18], 0, 180, fill=INK, width=2)
        draw.line([(x + 8, y + 26), (x + 22, y + 26)], fill=INK, width=2)
    elif kind == "dome":
        draw.arc([x + 4, y + 2, x + 26, y + 20], 180, 360, fill=INK, width=2)
        draw.line([(x + 2, y + 20), (x + 28, y + 20)], fill=INK, width=2)
        draw.rectangle([x + 6, y + 22, x + 24, y + 27], outline=INK, width=2)
    elif kind == "bridge":
        draw.line([(x + 2, y + 22), (x + 28, y + 22)], fill=INK, width=2)
        draw.arc([x + 2, y + 10, x + 28, y + 26], 180, 360, fill=INK, width=2)
        draw.line([(x + 15, y + 2), (x + 15, y + 12)], fill=INK, width=2)
    elif kind == "rocket":
        draw.polygon([(x + 15, y + 1), (x + 22, y + 16), (x + 15, y + 13),
                      (x + 8, y + 16)], fill=INK)
        draw.polygon([(x + 12, y + 20), (x + 15, y + 28), (x + 18, y + 20)],
                     fill=RED)
    elif kind == "pad":
        draw.rounded_rectangle([x + 2, y + 8, x + 28, y + 22], radius=6,
                               outline=INK, width=2)
        draw.line([(x + 9, y + 15), (x + 13, y + 15)], fill=INK, width=2)
        draw.line([(x + 11, y + 13), (x + 11, y + 17)], fill=INK, width=2)
        draw.ellipse([x + 19, y + 12, x + 22, y + 15], fill=INK)
        draw.ellipse([x + 23, y + 15, x + 26, y + 18], fill=INK)
    elif kind == "storm":
        cx, cy = x + 15, y + 15
        for r in (12, 8, 4):
            draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=INK,
                     width=2)


def draw_lead(draw, story, x, y, w):
    tag_f = font(SANS_B, 15)
    draw.text((x, y), story["tag"], font=tag_f, fill=story["colour"])
    head_f = font(SERIF_B, 27)
    hy = y + 22
    for line in story["head"].split("\n"):
        draw.text((x, hy), line, font=head_f, fill=INK)
        hy += 31
    art_y = hy + 4
    art_h = 76
    art = {"summit": draw_summit, "gulf": draw_gulf,
           "chart": draw_chart}[story["art"]]
    art(draw, x, art_y, w, art_h)
    draw.rectangle([x, art_y, x + w, art_y + art_h], outline=INK, width=2)
    body_y = art_y + art_h + 8
    return para(draw, x, body_y, story["body"], font(SANS, 13), w, 16)


def draw_second(draw, story, x, y, w):
    draw_badge(draw, x + 11, y + 11, story["num"], story["colour"])
    tag_f = font(SANS_B, 13)
    draw.text((x + 28, y + 2), story["tag"], font=tag_f,
              fill=story["colour"])
    head_f = font(SERIF_B, 19)
    hy = y + 22
    for line in wrap(draw, story["head"], head_f, w - 38):
        draw.text((x, hy), line, font=head_f, fill=INK)
        hy += 21
    draw_icon(draw, story["icon"], x + w - 34, y + 2)
    return para(draw, x, hy + 2, story["body"], font(SANS, 13), w, 16)


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(235, 240, 244),
                   outline=INK, width=2)
    step = 9
    for gy in range(6, h - 4, step):
        for gx in range(6, w - 4, step):
            if any(dot_grid_land(cx, cy, rx, ry, gx, gy)
                   for cx, cy, rx, ry in LAND):
                draw.ellipse([x + gx - 2, y + gy - 2, x + gx + 2, y + gy + 2],
                             fill=(90, 95, 100))
    for num, px, py, colour in PINS:
        draw.ellipse([x + px - 10, y + py - 10, x + px + 10, y + py + 10],
                     fill=colour, outline=(255, 255, 255), width=2)
        label = str(num)
        fnt = font(SANS_B, 12)
        tw = draw.textlength(label, font=fnt)
        draw.text((x + px - tw / 2, y + py - 8), label, font=fnt,
                  fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 26
    right = W - mx
    col_w = (right - mx - 2 * 18) // 3

    # Masthead.
    centre(d, W // 2, 4, "THE WORLD TODAY", font(SERIF_B, 56))
    centre(d, W // 2, 70, "25 STORIES \u00b7 6 CONTINENTS \u00b7 ONE PAGE",
           font(SANS_B, 20), fill=RED)
    centre(d, W // 2, 94,
           "Everything on this page happened, or was first reported, "
           "on Thursday 19 November 2026.",
           font(SERIF, 15), fill=GREY)
    d.rectangle([mx, 116, right, 144], fill=INK)
    centre(d, W // 2, 122, "THURSDAY 19 NOVEMBER 2026",
           font(SANS_B, 22), fill=(255, 255, 255))

    # Lead row.
    lead_y = 152
    lead_bottom = lead_y
    for i, story in enumerate(LEADS):
        cx = mx + i * (col_w + 18)
        bottom = draw_lead(d, story, cx, lead_y, col_w)
        lead_bottom = max(lead_bottom, bottom)
        if i < 2:
            d.line([(cx + col_w + 9, lead_y),
                    (cx + col_w + 9, lead_bottom)], fill=RULE, width=1)
    hline(d, mx, right, lead_bottom + 8)

    # Second and third rows of stories.
    row_y = lead_bottom + 10
    row_bottom = row_y
    for i, story in enumerate(SECOND[:3]):
        cx = mx + i * (col_w + 18)
        row_bottom = max(row_bottom,
                         draw_second(d, story, cx, row_y, col_w))
    hline(d, mx, right, row_bottom + 6)
    row2_y = row_bottom + 10
    row2_bottom = row2_y
    for i, story in enumerate(SECOND[3:]):
        cx = mx + i * (col_w + 18)
        row2_bottom = max(row2_bottom,
                          draw_second(d, story, cx, row2_y, col_w))
    hline(d, mx, right, row2_bottom + 6)

    # BY THE NUMBERS strip.
    num_y = row2_bottom + 10
    num_h = 54
    box_w = (right - mx - 3 * 10) // 4
    for i, (big, label) in enumerate(NUMBERS):
        bx = mx + i * (box_w + 10)
        d.rectangle([bx, num_y, bx + box_w, num_y + num_h], fill=BOX,
                    outline=INK, width=2)
        centre(d, bx + box_w // 2, num_y + 4, big, font(SERIF_B, 27))
        centre(d, bx + box_w // 2, num_y + 34, label, font(SANS_B, 11))

    # World map + legend.
    map_title_y = num_y + num_h + 8
    d.text((mx, map_title_y), "WHERE IT HAPPENED",
           font=font(SANS_B, 17), fill=INK)
    d.text((right - 190, map_title_y), "PINS MARK STORIES 1\u20136, 9",
           font=font(SANS_B, 11), fill=GREY)
    map_y = map_title_y + 22
    map_h = 108
    map_w = 660
    draw_map(d, mx, map_y, map_w, map_h)
    lx = mx + map_w + 16
    d.text((lx, map_y), "REGIONS", font=font(SANS_B, 13), fill=INK)
    ly = map_y + 18
    for label, colour in LEGEND:
        d.rectangle([lx, ly + 1, lx + 11, ly + 12], fill=colour)
        d.text((lx + 16, ly), label, font=font(SANS_B, 11), fill=INK)
        ly += 13

    # Briefs.
    brief_title_y = map_y + map_h + 8
    hline(d, mx, right, brief_title_y)
    d.text((mx, brief_title_y + 6),
           "ALSO ON THURSDAY 19 NOVEMBER \u2014 16 MORE STORIES",
           font=font(SANS_B, 15), fill=INK)
    brief_y = brief_title_y + 24
    half = len(BRIEFS) // 2
    brief_f = font(SANS, 12)
    for col in range(2):
        bx = mx + col * ((right - mx) // 2 + 6)
        by = brief_y
        for num, place, text in BRIEFS[col * half:(col + 1) * half]:
            d.text((bx, by), f"{num}.", font=font(SANS_B, 12), fill=RED)
            d.text((bx + 24, by), f"{place} \u2014 {text}", font=brief_f,
                   fill=INK)
            by += 13
    hline(d, mx, right, brief_y + 8 * 13 + 2)
    centre(d, W // 2, brief_y + 8 * 13 + 8,
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera "
           "\u00b7 CNN \u00b7 Bloomberg \u00b7 IMD \u00b7 NASA",
           font(SANS, 12), fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
