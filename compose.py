#!/usr/bin/env python3
"""Compose the front page for make.fun's news-image-20261120 entry.

Typesets a broadsheet front page summing up Friday 20 November 2026 into
entry.png (1024x1024) with PIL. Deterministic: same fonts, same text, same
bytes on every run. main.py ships the finished PNG; this script is the
typesetter that rebuilds it.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

W = H = 1024
MARGIN = 40
CW = W - 2 * MARGIN  # 944 px of live matter

PAPER = (247, 243, 234)   # #F7F3EA
INK = (18, 18, 18)        # #121212
RED = (168, 12, 28)       # #A80C1C
GREY = (90, 86, 78)       # #5A564E
BODY_INK = (35, 33, 30)
DIVIDER = (178, 172, 160)

FONTS = "/usr/share/fonts/truetype"
SERIF_DISPLAY = f"{FONTS}/noto/NotoSerifDisplay-Black.ttf"
SERIF_BOLD = f"{FONTS}/noto/NotoSerif-Bold.ttf"
SANS_XBOLD = f"{FONTS}/noto/NotoSans-ExtraBold.ttf"
SANS_BLACK = f"{FONTS}/noto/NotoSans-Black.ttf"
SANS_BOLD = f"{FONTS}/noto/NotoSans-Bold.ttf"
SERIF = f"{FONTS}/liberation/LiberationSerif-Regular.ttf"
SERIF_ITALIC = f"{FONTS}/liberation/LiberationSerif-Italic.ttf"

FOOTER_RULE_Y = H - 46
CONTENT_LIMIT = FOOTER_RULE_Y - 14


def font(path, size):
    return ImageFont.truetype(path, size)


def line_height(f, factor):
    ascent, descent = f.getmetrics()
    return int((ascent + descent) * factor)


def wrap(draw, text, f, max_width):
    """Greedy word wrap measured with PIL; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=f) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def wrap_rich(draw, segments, max_width):
    """Wrap mixed-font segments; returns lines of (text, font, fill) runs."""
    words = []  # (word, font, fill, space_before_width)
    for text, f, fill in segments:
        for i, word in enumerate(text.split(" ")):
            if word == "":
                continue
            space_w = draw.textlength(" ", font=f) if i > 0 else 0.0
            words.append((word, f, fill, space_w))
    lines, cur, cur_w = [], [], 0.0
    for word, f, fill, space_w in words:
        w = draw.textlength(word, font=f)
        if cur and cur_w + space_w + w > max_width:
            lines.append(cur)
            cur, cur_w = [(word, f, fill)], w
        else:
            if cur:
                cur_w += space_w
            cur.append((word, f, fill))
            cur_w += w
    if cur:
        lines.append(cur)
    return lines


def draw_ink_line(draw, x, y, text, f, fill, center=False):
    """Draw a line with its ink top exactly at y; return the ink bottom.

    Display faces carry large internal leading in their metrics, so big
    headlines are stacked by measured ink height instead of getmetrics().
    """
    bbox = draw.textbbox((0, 0), text, font=f)
    dx = x - draw.textlength(text, font=f) / 2 if center else x
    draw.text((dx, y - bbox[1]), text, font=f, fill=fill)
    return y + (bbox[3] - bbox[1])


def draw_rich_line(draw, x, y, runs):
    for word, f, fill in runs:
        draw.text((x, y), word, font=f, fill=fill)
        x += draw.textlength(word, font=f) + draw.textlength(" ", font=f)
    return x


def draw_tracked(draw, cx, y, text, f, tracking, fill):
    """Letter-spaced text centred on cx; y is the ascender line."""
    widths = [draw.textlength(ch, font=f) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + tracking


def fit_banner(draw, lines, start_size):
    """Shrink the display font from start_size until every line fits CW."""
    size = start_size
    while size > 10:
        f = font(SERIF_DISPLAY, size)
        if all(draw.textlength(ln, font=f) <= CW for ln in lines):
            return f, size
        size -= 1
    raise AssertionError("banner headline does not fit at any size")


def panel(draw, x, y, width, kicker, headline, body, f_kick, f_head, f_body):
    draw.text((x, y), kicker, font=f_kick, fill=RED)
    y += line_height(f_kick, 1.0) + 3
    for ln in wrap(draw, headline, f_head, width):
        y = draw_ink_line(draw, x, y, ln, f_head, INK)
        y += 4
    y += 3
    for ln in wrap(draw, body, f_body, width):
        draw.text((x, y), ln, font=f_body, fill=BODY_INK)
        y += line_height(f_body, 1.22)
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    f_folio = font(SANS_BOLD, 14)
    f_masthead = font(SERIF_DISPLAY, 76)
    f_date = font(SANS_BLACK, 26)
    f_lead_kick = font(SANS_XBOLD, 18)
    f_subhead = font(SERIF_ITALIC, 22)
    f_kick = font(SANS_XBOLD, 16)
    f_head = font(SERIF_BOLD, 30)
    f_body = font(SERIF, 18)
    f_brief_head = font(SANS_BLACK, 18)
    f_brief_place = font(SANS_BOLD, 16)
    f_brief = font(SERIF, 17)
    f_footer = font(SERIF_ITALIC, 14)

    y = 26

    # 1. Folio strip ------------------------------------------------------
    draw.text((MARGIN, y), "THE DAY'S NEWS · ONE PAGE · ONE IMAGE",
              font=f_folio, fill=GREY)
    right = "EST. 2026 — NO. 20"
    draw.text((W - MARGIN - draw.textlength(right, font=f_folio), y), right,
              font=f_folio, fill=GREY)
    y += line_height(f_folio, 1.0) + 5
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=1)
    y += 9

    # 2. Masthead ----------------------------------------------------------
    y = draw_ink_line(draw, W / 2, y, "The Daily World", f_masthead, INK,
                      center=True)
    y += 5
    draw.rectangle([MARGIN, y, W - MARGIN, y + 3], fill=INK)
    y += 6
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=1)
    y += 8

    # 3. Date bar ----------------------------------------------------------
    bar_h = 38
    draw.rectangle([MARGIN, y, W - MARGIN, y + bar_h], fill=INK)
    asc, desc = f_date.getmetrics()
    text_y = y + (bar_h - (asc + desc)) // 2
    draw_tracked(draw, W / 2, text_y, "FRIDAY · 20 NOVEMBER 2026", f_date, 3,
                 (255, 255, 255))
    y += bar_h + 11

    # 4. Lead story ---------------------------------------------------------
    draw.text((MARGIN, y), "THE HAGUE  ·  INTERNATIONAL COURT OF JUSTICE",
              font=f_lead_kick, fill=RED)
    y += line_height(f_lead_kick, 1.0) + 5
    banner_lines = ["World Court: Myanmar committed",
                    "genocide against the Rohingya"]
    f_banner, _ = fit_banner(draw, banner_lines, 57)
    for ln in banner_lines:
        y = draw_ink_line(draw, MARGIN, y, ln, f_banner, INK)
        y += 6
    y += 2
    subhead = ("The first genocide verdict against a state in the court's "
               "history, over the 2017 crackdown — Myanmar rejects the "
               "judgment.")
    for ln in wrap(draw, subhead, f_subhead, CW):
        draw.text((W / 2, y), ln, font=f_subhead, fill=BODY_INK, anchor="ma")
        y += line_height(f_subhead, 1.26)
    y += 8
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 8

    # 5-6. News panels, two rows of two ------------------------------------
    col_w = (CW - 28) // 2
    col2_x = MARGIN + col_w + 28
    divider_x = MARGIN + col_w + 14

    rows = [
        (("SHENZHEN · FIRST THREE-WAY SUMMIT",
          "Trump, Xi & Putin sign a peace declaration",
          "US, Chinese and Russian leaders meet face to face for the first "
          "time and sign a four-point pact. Europe warns: no deal over our "
          "heads."),
         ("KYIV · WARSAW · THE WAR",
          "Russia pounds Kyiv; a missile hits Poland",
          "400+ drones and 110 missiles in one night; three Kyiv bridges "
          "hit. Ukraine hits the Crimea Bridge a third time; Putin vows a "
          "hard reply.")),
        (("NEW YORK · MARKETS",
          "AI sell-off deepens as Anthropic lists",
          "S&P 500 −2%, a fifth straight loss; Nikkei −4.8%. Anthropic, "
          "the first pure-AI listing, closed its debut +17% at $97, then "
          "slid. Gold −4.2%."),
         ("RIYADH · MIDDLE EAST",
          "Houthi missiles strike the Riyadh skyline",
          "Missiles damage the sovereign wealth fund tower in the "
          "financial district. Oil tops $92 as Hormuz tanker attacks "
          "intensify.")),
    ]
    for left, right_panel in rows:
        row_top = y
        end_l = panel(draw, MARGIN, y, col_w, *left, f_kick, f_head, f_body)
        end_r = panel(draw, col2_x, y, col_w, *right_panel,
                      f_kick, f_head, f_body)
        y = max(end_l, end_r)
        draw.line([(divider_x, row_top), (divider_x, y - 6)], fill=DIVIDER,
                  width=1)
        y += 8
        draw.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
        y += 8

    # 7. Briefs --------------------------------------------------------------
    draw.text((MARGIN, y), "ALSO ON FRIDAY", font=f_brief_head, fill=INK)
    y += line_height(f_brief_head, 1.0) + 5
    briefs = [
        ("BRUSSELS", "EU–UK summit seals a Brexit “reset” deal."),
        ("NAIROBI", "Last Ebola patient home; outbreak over, 37 days on."),
        ("GAZA", "Israeli troops cross the Gaza ceasefire line."),
        ("ANTALYA", "COP31 draft drops fossil phase-out call."),
        ("LOS ANGELES", "GTA VI launch sales top $2.3 billion."),
    ]
    brief_leading = line_height(f_brief, 1.24)
    for row_start in range(0, len(briefs), 2):
        row = briefs[row_start:row_start + 2]
        row_h = 0
        for col, (place, text) in enumerate(row):
            x = MARGIN if col == 0 else col2_x
            # red square bullet, aligned with the first line's x-height
            draw.rectangle([x, y + 6, x + 7, y + 13], fill=RED)
            segments = [(place + " — ", f_brief_place, INK),
                        (text, f_brief, BODY_INK)]
            lines = wrap_rich(draw, segments, col_w - 18)
            ly = y
            for runs in lines:
                draw_rich_line(draw, x + 18, ly, runs)
                ly += brief_leading
            row_h = max(row_h, ly - y)
        y += row_h + 5

    # 8. Footer --------------------------------------------------------------
    assert y <= CONTENT_LIMIT, f"content overflows: y={y} > {CONTENT_LIMIT}"
    draw.line([(MARGIN, FOOTER_RULE_Y), (W - MARGIN, FOOTER_RULE_Y)],
              fill=INK, width=1)
    draw.text((MARGIN, FOOTER_RULE_Y + 8),
              "Compiled from the day's reporting by Reuters, the BBC and "
              "international news wires.",
              font=f_footer, fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print(f"wrote {out}: {os.path.getsize(out)} bytes, content ends y={y}")


if __name__ == "__main__":
    build()
