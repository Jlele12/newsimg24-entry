#!/usr/bin/env python3
"""Renders the front page of the world's news for Tuesday 24 November 2026
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Deterministic: every draw call takes fixed inputs, so two runs write
byte-identical PNGs. No network access is used; the headlines below were
gathered from BBC World RSS on the day and baked in.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# Palette (newspaper on a late-November night)
PAPER = (244, 242, 235)
INK = (24, 26, 31)
RED = (178, 34, 38)
BLUE = (32, 62, 110)
GREY = (110, 112, 118)
SLATE = (58, 64, 74)
GOLD = (176, 132, 44)

# The day's stories, in lead-first order.
# (region tag, tag colour, headline, detail, glyph key)
STORIES = [
    ("USA", RED,
     "TRUMP BROKERS RETURN",
     "Nvidia reinstates CEO Jensen Huang\nafter scandal; comeback adds $1tn",
     "chip"),
    ("EUROPE / AFRICA", BLUE,
     "RUSSIAN WARSHIP SUNK OFF LIBYA",
     "Ukraine strikes ships at Libyan port;\nwar's reach spreads to Africa",
     "wave"),
    ("GLOBAL", GOLD,
     "COP31 COLLAPSES IN ANTALYA",
     "Oil interests, US boycott and finance\nrift sink longest UN climate talks",
     "globe"),
    ("ASIA", RED,
     "US TO BLACKLIST MEGASPEED",
     "Asian AI firm accused of funneling\nchips to China after Nvidia scandal",
     "chip"),
    ("ASIA", BLUE,
     "IRAN FLOGS SINGER OVER HIJAB",
     "Parastoo Ahmadi and three musicians\ngiven 74 lashes in Qom, lawyers say",
     "note"),
    ("MIDEAST", GOLD,
     "GAZA A 'TOXIC WASTELAND'",
     "Oxfam finds contamination signs\nacross almost all of the Strip",
     "globe"),
    ("AFRICA / ASIA", BLUE,
     "MYANMAR LEADERS SANCTIONED",
     "UK and allies act after ICJ rules\nRohingya genocide took place",
     "wave"),
    ("USA", GREY,
     "WHITE HOUSE TREE ARRIVES",
     "18-foot Wisconsin fir welcomed by\nFirst Lady for Christmas 2026",
     "note"),
]

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def glyph_chip(d, x, y, key, colour):
    """A small 26x26 pictogram, drawn with primitives only."""
    d.rectangle([x, y, x + 25, y + 25], outline=colour, width=2)
    cx, cy = x + 13, y + 13
    if key == "chip":
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], outline=colour, width=2)
        for i in (-3, 0, 3):
            d.line([cx + i, cy - 5, cx + i, y + 3], fill=colour, width=1)
            d.line([cx + i, cy + 5, cx + i, y + 22], fill=colour, width=1)
    elif key == "wave":
        for k in range(3):
            yy = cy - 6 + k * 6
            d.arc([x + 4, yy - 4, x + 22, yy + 4], 180, 360, fill=colour, width=2)
    elif key == "globe":
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=colour, width=2)
        d.line([cx - 8, cy, cx + 8, cy], fill=colour, width=1)
        d.arc([cx - 4, cy - 8, cx + 4, cy + 8], 0, 360, fill=colour, width=1)
    elif key == "note":
        d.line([cx - 2, cy - 7, cx - 2, cy + 5], fill=colour, width=2)
        d.ellipse([cx - 7, cy + 2, cx - 1, cy + 8], fill=colour)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Sky band: a single composed night-to-dawn gradient strip behind the masthead
    top = 0
    while top < 118:
        t = top / 118.0
        c = (int(20 + 190 * t), int(24 + 175 * t), int(40 + 160 * t))
        d.line([(0, top), (W, top)], fill=c)
        top += 1

    # Masthead
    f_mast = font("DejaVuSerif-Bold.ttf", 64)
    f_date = font("DejaVuSans-Bold.ttf", 26)
    f_small = font("DejaVuSans.ttf", 17)
    mast = "THE WORLD IN ONE DAY"
    tw = d.textlength(mast, font=f_mast)
    d.text(((W - tw) / 2, 16), mast, font=f_mast, fill=(250, 248, 240))
    date = "TUESDAY 24 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, 86), date, font=f_date, fill=GOLD)
    d.text((24, 92), "WORLD EDITION", font=f_small, fill=(230, 232, 238))
    sub = "Eight stories that moved the planet, as reported on the day"
    sw = d.textlength(sub, font=f_small)
    d.text(((W - sw) / 2, 122), sub, font=f_small, fill=GREY)
    d.line([(24, 146), (W - 24, 146)], fill=INK, width=3)

    # Lead story, larger
    f_head = font("DejaVuSans-Bold.ttf", 34)
    f_detail = font("DejaVuSans.ttf", 21)
    f_tag = font("DejaVuSans-Bold.ttf", 15)

    y = 162
    region, colour, head, detail, gkey = STORIES[0]
    d.rectangle([24, y, 318, y + 24], fill=colour)
    d.text((34, y + 4), "LEAD | " + region, font=f_tag, fill=PAPER)
    glyph_chip(d, W - 60, y + 2, gkey, colour)
    d.text((24, y + 34), head, font=f_head, fill=INK)
    yy = y + 34 + 44
    d.text((24, yy), detail, font=f_detail, fill=SLATE, spacing=4)
    d.line([(24, yy + 62), (W - 24, yy + 62)], fill=GREY, width=2)

    # Remaining stories in a two-column grid
    y0 = yy + 78
    col_w = 488
    row_h = 168
    f_head2 = font("DejaVuSans-Bold.ttf", 23)
    f_detail2 = font("DejaVuSans.ttf", 17)
    for i, (region, colour, head, detail, gkey) in enumerate(STORIES[1:]):
        col = i % 2
        row = i // 2
        x = 24 + col * (col_w + 24)
        y = y0 + row * row_h
        d.rectangle([x, y, x + 150, y + 20], fill=colour)
        d.text((x + 7, y + 2), region, font=f_tag, fill=PAPER)
        glyph_chip(d, x + col_w - 34, y, gkey, colour)
        d.text((x, y + 30), head, font=f_head2, fill=INK)
        d.text((x, y + 62), detail, font=f_detail2, fill=SLATE, spacing=3)
        d.line([(x, y + row_h - 18), (x + col_w - 16, y + row_h - 18)],
               fill=(200, 198, 190), width=2)

    # Footer: the day's date again, so the image names its day even cropped
    d.rectangle([0, H - 44, W, H], fill=INK)
    foot = "24 NOVEMBER 2026  |  THE DAY THE WORLD MADE HEADLINES"
    fw = d.textlength(foot, font=f_date)
    d.text(((W - fw) / 2, H - 40), foot, font=f_date, fill=PAPER)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), "PNG", optimize=True)


if __name__ == "__main__":
    render()
