#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 20 November 2026.

A one-day world-news front page, drawn procedurally with the Python
standard library only. No network, no fonts, no image libraries: the
5x7 bitmap font below and the PNG encoder are written here from scratch.

Run:  python3 main.py
Writes: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)
Deterministic: two runs produce byte-identical output.
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (253, 252, 247)
PAPER_SHADE = (246, 243, 233)
INK = (18, 18, 18)
RED = (178, 30, 30)
RED_DARK = (140, 20, 20)
GREY = (110, 108, 100)
BLUE = (28, 58, 110)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit value,
# most significant bit = leftmost column.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x10, 0x0E),
    "d": (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x1E, 0x10, 0x10),
    "q": (0x00, 0x00, 0x0D, 0x13, 0x0F, 0x01, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "^": (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    "~": (0x00, 0x00, 0x00, 0x0E, 0x15, 0x00, 0x00),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "\\": (0x10, 0x10, 0x08, 0x04, 0x02, 0x01, 0x01),
    "\u2022": (0x00, 0x00, 0x00, 0x0E, 0x0E, 0x00, 0x00),
    "\u2014": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "\u2019": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "\u2018": (0x08, 0x08, 0x04, 0x00, 0x00, 0x00, 0x00),
    "\u201c": (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "\u201d": (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
}
BLANK = (0, 0, 0, 0, 0, 0, 0)
CHAR_W = 6  # 5 pixels + 1 spacing, times scale


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    limit = max(1, max_w // (CHAR_W * scale))
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # a single over-long word is hard-split
            while len(w) > limit:
                lines.append(w[:limit])
                w = w[limit:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x1 - x0):
                i = base + xx * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def hline(self, x, y, w, color, thick=1):
        for t in range(thick):
            self.rect(x, y + t, w, 1, color)

    def vline(self, x, y, h, color, thick=1):
        for t in range(thick):
            self.rect(x + t, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, color):
        for yy in range(-r, r + 1):
            half = int((r * r - yy * yy) ** 0.5)
            self.rect(cx - half, cy + yy, 2 * half + 1, 1, color)

    def text(self, s, x, y, scale, color, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (0x10 >> col):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
                        if bold:
                            self.rect(cx + col * scale + 1, y + row * scale,
                                      scale, scale, color)
            cx += CHAR_W * scale
        return cx

    def text_center(self, s, cx, y, scale, color, bold=False):
        self.text(s, cx - text_width(s, scale) // 2, y, scale, color,
                  bold=bold)

# ---------------------------------------------------------------- news data
# 32 stories from Friday 20 November 2026 (events of the day, plus
# overnight reports first published late 19 Nov / early 20 Nov),
# ranked most consequential first. Every item was checked against live
# news reports on 20 Nov 2026; nothing is invented. Locations are the
# dateline of each report. Headlines are kept short so each fits one
# line at scale 2 in its column; bodies are one or two short lines.

HERO_HEAD = "TRUMP PUSHES IRAN WAR DECISION INTO 2027"
HERO_SUB = [
    "President says he will \"see what happens\" after Jan 1 and is in",
    "no rush on a decision over striking Iran, after talks in China.",
]
HERO_TAG = "WASHINGTON  •  20 NOV"

# (headline, body, dateline) — 31 ranked stories after the hero.
# Bodies are complete sentences that wrap to at most two short lines.
STORIES = [
    ("COURT: MYANMAR COMMITTED GENOCIDE",
     "UN court rules Myanmar's army intended to destroy the Rohingya minority in its 2017 crackdown.",
     "THE HAGUE"),
    ("EUROPE READY FOR TALKS WITH RUSSIA",
     "Leaders say Europe is ready to negotiate an end to the war in Ukraine and take a seat at the table.",
     "BERLIN"),
    ("KUSHNER: RUSSIA OK WITH KYIV PLEDGE",
     "US envoy says Moscow is 'comfortable' with Article 5-style security guarantees for Ukraine.",
     "BERLIN"),
    ("CRIMEAN BRIDGE HIT AGAIN",
     "Ukraine confirms a Neptune missile strike; rail traffic is halted and no injuries are reported.",
     "CRIMEA"),
    ("CYCLONE AKVAN BEARS DOWN ON INDIA",
     "300,000 people are evacuated in Odisha and 423 rescue teams deployed as the storm nears landfall.",
     "ODISHA"),
    ("ANTHROPIC'S $81.3BN IPO DEBUT",
     "Shares close up 17% at $97.17 in the largest IPO on record, valuing the AI firm near $1.5 trillion.",
     "NEW YORK"),
    ("VOYAGER 1 PASSES ONE LIGHT-DAY",
     "NASA confirms the probe is the first human-made object 16 billion miles from Earth, after 49 years.",
     "CALIFORNIA"),
    ("GAZA OP ENDS; TRUCE TOLL 1,600+",
     "Israel says its central Gaza ground operation is over; an AFP tally counts 1,600+ killed since the Oct 2025 ceasefire began.",
     "GAZA"),
    ("GTA VI SALES TOP $1.8BN",
     "Sensor Tower estimates Rockstar's blockbuster passes The Odyssey's $1.8bn global box-office run.",
     "WORLDWIDE"),
    ("HAYABUSA2 LOSES ASTEROID LANDING",
     "Engine trouble forces Japan's probe to abandon its planned touchdown on an asteroid.",
     "TOKYO"),
    ("MODI MEETS WILLIAM AND KATE",
     "India's prime minister hosts the Prince and Princess of Wales in New Delhi to boost ties.",
     "NEW DELHI"),
    ("NICHOLLS 113* RESCUES NEW ZEALAND",
     "An unbeaten century lifts the hosts to 273 for 5 on day one of the first Test against India.",
     "WELLINGTON"),
    ("BAVUMA OUT OF BANGLADESH DECIDER",
     "South Africa's captain is ruled out of the series decider with a calf injury.",
     "JOHANNESBURG"),
    ("HARMER BREAKS 130-YEAR RECORD",
     "The spinner's 6 for 51 seals South Africa's win over Bangladesh.",
     "JOHANNESBURG"),
    ("FIJI DECLARES DISASTER OVER DROUGHT",
     "El Nino drought forces a national state of disaster, with rain below normal until April.",
     "SUVA"),
    ("SENSEX SURGES 990 POINTS",
     "Indian stocks close at 83,022 as the Nifty crosses 25,500 on strong buying.",
     "MUMBAI"),
    ("TRUMP PARDONS PETE ROSE",
     "Baseball's all-time hits leader is pardoned posthumously by the president.",
     "WASHINGTON"),
    ("AUSTRALIA SANCTIONS SETTLERS",
     "Canberra acts against Israeli settlers and groups over West Bank expansion.",
     "CANBERRA"),
    ("TANKER SUNK OFF BULGARIA WAS HIT",
     "Officials say the LPG tanker was struck by projectiles before it sank in the Black Sea.",
     "BLACK SEA"),
    ("JAPAN PM SEEKS CHINA DIALOGUE",
     "Takaichi calls for continued talks with Beijing to ease bilateral tensions.",
     "TOKYO"),
    ("SEOUL COURT CLEARS EX-PM HAN",
     "South Korea's top court overturns Han Duck-soo's conviction over the martial law crisis.",
     "SEOUL"),
    ("US, VENEZUELA RESTORE MILITARY TIES",
     "The two countries sign a deal to resume military cooperation, the US says.",
     "CARACAS"),
    ("NORTH KOREA EXPANDS ENRICHMENT",
     "The UN watchdog reports growth at the Yongbyon uranium enrichment plant.",
     "VIENNA"),
    ("FIRE AT YUNUS FAMILY HOME",
     "A blaze at the ancestral home of Bangladesh's ex-leader is suspected arson.",
     "BANGLADESH"),
    ("APEC LEADERS TALK TRADE IN SHENZHEN",
     "Xi urges open trade as Asia-Pacific economies meet in China for the summit.",
     "SHENZHEN"),
    ("GEMINI 4 NEON LAUNCHES",
     "Google's fast new AI model arrives at $3 per million input tokens.",
     "CALIFORNIA"),
    ("ARSENAL FACE LYON IN EUROPE",
     "The Women's Champions League tie kicks off at Meadow Park in London.",
     "LONDON"),
    ("SHELTON EDGES JODAR AT ATP FINALS",
     "The American moves close to a semi-final spot at the season finale in Turin.",
     "TURIN"),
    ("PANCREATIC CANCER PILL HOPE",
     "Daily pill daraxonrasib shrinks or clears tumours in 60% of 61 patients in an early trial.",
     "LONDON"),
    ("US COURT SUMMONS DOVAL, GOEL",
     "A judge orders summonses delivered through Delhi courts in a US case.",
     "NEW YORK"),
    ("COP31 DUE TO CLOSE IN ANTALYA",
     "Climate talks due to end after 12 days in Turkey; India presses for climate finance.",
     "ANTALYA"),
]

NUMBERS = [
    ("300,000", "evacuated as Cyclone Akvan nears Odisha"),
    ("$81.3bn", "raised in Anthropic's record IPO"),
    ("16bn miles", "Voyager 1 from Earth: one light-day"),
    ("1,600+", "killed in Gaza since the ceasefire began"),
    ("113*", "Nicholls' unbeaten century v India"),
]

# ---------------------------------------------------------------- layout
MARGIN = 24
COL_W = 476
COL_X = (MARGIN, MARGIN + COL_W + 24)
WHITE = (255, 255, 255)


def draw_globe(cv, cx, cy, r):
    """Procedural wireframe globe with red markers on story regions."""
    import math
    cv.circle(cx, cy, r, INK)
    cv.circle(cx, cy, r - 1, INK)
    # parallels
    for lat_deg, off in ((-45, -0), (0, 0), (45, 0)):
        lat = math.radians(lat_deg)
        ry = max(2, int(r * abs(math.cos(lat))))
        y = cy + int(r * math.sin(lat))
        for deg in range(0, 360, 2):
            a = math.radians(deg)
            cv.set(cx + int(r * math.cos(a)), y + int(ry * math.sin(a)), INK)
    # meridians
    for lon_deg in (-60, -30, 0, 30, 60):
        lon = math.radians(lon_deg)
        rx = max(2, int(r * abs(math.cos(lon))))
        for deg in range(0, 360, 2):
            a = math.radians(deg)
            cv.set(cx + int(rx * math.cos(a)), cy + int(r * math.sin(a)), INK)
    # red markers: Washington, Berlin, Gaza, Odisha, Suva
    for dx, dy in ((-38, -22), (6, -30), (24, -8), (52, 6), (62, 34)):
        cv.disc(cx + dx, cy + dy, 4, RED)
        cv.circle(cx + dx, cy + dy, 6, RED)


def grain(cv):
    """Deterministic paper grain: irregular sparse darker speckles
    from a fixed-seed linear congruential generator (newsprint feel)."""
    r, g, b = PAPER_SHADE
    state = 1234567
    for y in range(H):
        base = y * W * 3
        for x in range(W):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            # high bits only: the LCG's low bits cycle with a short period
            if (state >> 16) % 8 < 1:
                i = base + x * 3
                cv.px[i] = r
                cv.px[i + 1] = g
                cv.px[i + 2] = b


def render():
    cv = Canvas(W, H, PAPER)
    grain(cv)

    # page frame
    cv.rect(0, 0, W, 3, RED)
    cv.rect(0, H - 3, W, 3, RED)
    cv.rect(0, 0, 3, H, INK)
    cv.rect(W - 3, 0, 3, H, INK)

    # ---- masthead
    cv.text_center("THE WORLD TODAY", W // 2, 20, 6, INK, bold=True)
    cv.hline(MARGIN, 70, W - 2 * MARGIN, INK, 2)
    cv.text_center("ONE DAY  •  THE WHOLE WORLD  •  32 STORIES, 6 CONTINENTS",
                   W // 2, 80, 2, INK)

    # ---- red date bar
    cv.rect(MARGIN, 102, W - 2 * MARGIN, 30, RED)
    cv.text_center("FRIDAY 20 NOVEMBER 2026  •  THE DAY IN FULL",
                   W // 2, 110, 2, WHITE)

    # ---- hero
    cv.text("LEAD STORY", MARGIN, 146, 2, RED)
    cv.hline(MARGIN, 164, 640, RED, 2)
    cv.text("TRUMP PUSHES IRAN WAR", MARGIN, 174, 3, INK, bold=True)
    cv.text("DECISION INTO 2027", MARGIN, 201, 3, RED, bold=True)
    y = 236
    for line in HERO_SUB:
        cv.text(line, MARGIN, y, 2, INK)
        y += 16
    cv.text(HERO_TAG, MARGIN, y + 4, 1, RED)
    draw_globe(cv, 880, 224, 70)
    cv.text_center("THE WORLD IN ONE DAY", 880, 302, 1, GREY)
    cv.hline(MARGIN, 314, W - 2 * MARGIN, INK, 2)

    # ---- ranked list header
    cv.text("THE DAY, RANKED", MARGIN, 326, 2, INK, bold=True)
    cv.text("MOST CONSEQUENTIAL FIRST", 340, 328, 1, GREY)

    # ---- stories, two columns
    y0 = 350
    slot = 37
    for col in range(2):
        items = STORIES[col * 16:(col + 1) * 16]
        y = y0
        for i, (head, body, place) in enumerate(items):
            n = col * 16 + i + 1
            x = COL_X[col]
            # number badge
            cv.rect(x, y, 20, 20, RED)
            num = str(n)
            cv.text(num, x + (20 - text_width(num, 1)) // 2, y + 6, 1, WHITE)
            tx = x + 28
            cv.text(head, tx, y + 2, 2, INK, bold=True)
            blines = wrap_text(body + "  -- " + place, COL_W - 28, 1)[:2]
            by = y + 18
            for bl in blines:
                cv.text(bl, tx, by, 1, INK)
                by += 9
            cv.hline(x, y + slot - 2, COL_W, (196, 194, 184), 1)
            y += slot
        if y > 946:
            print("WARNING: column overflow, y =", y, file=sys.stderr)

    # ---- by the numbers strip
    cv.rect(MARGIN, 946, W - 2 * MARGIN, 48, RED)
    item_w = (W - 2 * MARGIN) // 5
    for i, (num, cap) in enumerate(NUMBERS):
        x = MARGIN + i * item_w
        if i:
            cv.vline(x, 952, 36, WHITE, 1)
        cv.text_center(num, x + item_w // 2, 954, 2, WHITE, bold=True)
        clines = wrap_text(cap, item_w - 16, 1)[:2]
        cy = 972
        for cl in clines:
            cv.text_center(cl, x + item_w // 2, cy, 1, WHITE)
            cy += 9

    # ---- footer
    cv.text_center(
        "Sources: Reuters, BBC, NASA, The Hindu, AP, AFP  •  Events of 20 Nov 2026, plus reports first published 18-19 Nov",
        W // 2, 1000, 1, GREY)
    return cv


# ---------------------------------------------------------------- PNG
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(render())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, len(png), "bytes")


if __name__ == "__main__":
    main()
