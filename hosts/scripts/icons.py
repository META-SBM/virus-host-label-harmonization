# -*- coding: utf-8 -*-
"""The lineage icons every heatmap in this project puts beside its side panels:
emoji rendered to flat silhouettes, plus the one that had to be drawn because
Unicode has no glyph for it.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ICON_COLOR = "#284b6e"
# Rendered via PIL from the system's Apple Color Emoji font, since matplotlib/
# FreeType cannot rasterize that font's sbix colour tables directly.
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
EMOJI_STRIKE = 160  # one of Apple Color Emoji's fixed bitmap-strike sizes
LINEAGE_EMOJI = {
    "Mammals": "\U0001F99B",                    # hippopotamus
    "Non-mammalian vertebrates": "\U0001F41F",  # fish
    "Invertebrates": "\U0001F577",              # spider
    "Plants": "\U0001F33F",                     # herb
    "Protists & oomycetes": "\U0001F9A0",       # microbe
    "Fungi": "\U0001F344",                      # mushroom
    "Unknown/Excluded": "❓",
}


EMOJI_AVAILABLE = os.path.exists(EMOJI_FONT)
_EMOJI_WARNED = False


def emoji_silhouette(char, color=ICON_COLOR):
    # The icons are rasterized from the system emoji font, which exists only on
    # macOS. Off macOS the committed PNGs in r_general_scheme/icons are used as
    # they are, and this returns a blank tile so that importing still works.
    global _EMOJI_WARNED
    try:
        font = ImageFont.truetype(EMOJI_FONT, EMOJI_STRIKE)
    except OSError:
        if not _EMOJI_WARNED:
            print(f"note: {EMOJI_FONT} is unavailable here; icons are not regenerated")
            _EMOJI_WARNED = True
        return np.zeros((1, 1, 4), dtype=np.uint8)
    img = Image.new("RGBA", (EMOJI_STRIKE + 40, EMOJI_STRIKE + 40), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((20, 20), char, font=font, embedded_color=True)
    alpha = img.split()[3]
    bbox = alpha.getbbox()
    if bbox:
        alpha = alpha.crop(bbox)
    rgb = tuple(int(color.lstrip("#")[k:k+2], 16) for k in (0, 2, 4))
    solid = Image.new("RGBA", alpha.size, rgb + (255,))
    solid.putalpha(alpha)
    return np.asarray(solid)


def lineage_icons(names, color=ICON_COLOR):
    """One icon array per lineage the caller actually draws. A figure asks for
    its own lineages only, so adding an eighth here cannot put an icon on a
    figure that has no such band."""
    return {n: (kelp_silhouette(color) if n == "Algae" else emoji_silhouette(LINEAGE_EMOJI[n], color))
            for n in names}


def tick_silhouette(color=ICON_COLOR):
    """Arachnida gets a drawn tick, not a glyph.

    Unicode has no tick: the nearest are a spider and a scorpion, and the block
    this labels is 941 Ixodida records against 222 other arachnids, so a spider
    would name the minority. Built to the same recipe as the emoji silhouettes
    -- one flat colour, cropped to its own alpha -- so it sits in the set
    rather than beside it.
    """
    img = Image.new("RGBA", (400, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rgb = tuple(int(color.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)) + (255,)
    # legs first, so the body covers where they attach
    for (x0, y0), (x1, y1) in [((122, 180), (38, 122)), ((124, 222), (26, 196)),
                               ((130, 264), (30, 272)), ((144, 302), (50, 350)),
                               ((278, 180), (362, 122)), ((276, 222), (374, 196)),
                               ((270, 264), (370, 272)), ((256, 302), (350, 350))]:
        d.line([(x0, y0), (x1, y1)], fill=rgb, width=17)
    d.ellipse([98, 148, 302, 384], fill=rgb)          # idiosoma
    d.polygon([(168, 168), (232, 168), (216, 92), (184, 92)], fill=rgb)  # capitulum
    d.line([(184, 96), (150, 52)], fill=rgb, width=13)                   # palps
    d.line([(216, 96), (250, 52)], fill=rgb, width=13)
    bbox = img.split()[3].getbbox()
    return np.asarray(img.crop(bbox) if bbox else img)


def kelp_silhouette(color=ICON_COLOR, strike=150):
    """Algae get a drawn frond, not a glyph.

    Unicode has no seaweed. The near misses -- coral, shell -- are animals, and
    a wave is not an organism at all, so both name something this row is not.
    Same recipe as the tick drawn for Arachnida elsewhere in this project: one
    flat colour, cropped to its own alpha, so it sits in the emoji set rather
    than beside it. A kelp is the one alga a reader recognises in silhouette;
    the diatoms and Aureococcus that make up most of the row have no shape
    anyone would know.
    """
    img = Image.new("RGBA", (620, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rgb = tuple(int(color.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)) + (255,)
    # A holdfast and broad ribbon blades.
    d.polygon([(248, 546), (372, 546), (350, 518), (270, 518)], fill=rgb)
    for ax in (250, 286, 334, 370):
        d.line([(310, 516), (ax, 548)], fill=rgb, width=14)
    stipe = [(310 + int(16 * math.sin(t / 160.0)), 522 - t) for t in range(0, 150, 3)]
    for x, y in stipe:
        d.ellipse([x - 15, y - 15, x + 15, y + 15], fill=rgb)
    # Kept near square: the matplotlib figure sizes a lineage icon by width, so
    # a tall glyph in a one-row band overflows onto its neighbours.
    for base, side, length, lean in ((44, -1, 250, 0.72), (49, 1, 270, 0.60),
                                     (38, -1, 205, 1.15), (47, 1, 200, 1.05)):
        x, y = stipe[base]
        for k in range(120):
            f = k / 119.0
            bx = x + side * (lean * length * f + 22 * math.sin(2.6 * f))
            by = y - length * f * 0.95 + 26 * math.sin(2.0 * math.pi * f)
            # nearly constant width, tapering only at the tip
            r = 21 * min(1.0, 6.0 * (1 - f) ** 0.8) * min(1.0, 9.0 * f + 0.5)
            if r > 0.7:
                d.ellipse([bx - r, by - r, bx + r, by + r], fill=rgb)
    bbox = img.split()[3].getbbox()
    out = img.crop(bbox) if bbox else img
    # Scaled to the emoji strike: the figures place icons at a fixed zoom on the
    # pixel array, so a larger canvas would render a larger glyph.
    if out.height != strike:
        out = out.resize((max(1, round(out.width * strike / out.height)), strike),
                         Image.LANCZOS)
    return np.asarray(out)
