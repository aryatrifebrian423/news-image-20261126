#!/usr/bin/env python3
"""26 November 2026: the world's news in one image (1024x1024 PNG).

Draws a news front page with the Python standard library only: a 5x7
bitmap font defined below, a hand-rolled PNG encoder (zlib + struct),
flat vector art for the climax panel. No network, no randomness, no
clock: two runs write byte-identical files.

Layout: masthead (date + story count), climax panel (Gulf in flames),
three region columns with 47 numbered stories, a numbers strip and a
sources footer. 50 verified stories in total, every one first reported
in the 26 November 2026 morning roundups (see SOURCES.md).
"""
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette: newsprint cream, ink, signal red, deep blue, gold ---
CREAM = (246, 241, 230)
INK = (20, 20, 20)
PAPER2 = (238, 231, 214)
RED = (176, 32, 32)
DARKRED = (122, 18, 18)
BLUE = (27, 58, 92)
GOLD = (201, 162, 39)
ORANGE = (232, 116, 30)
YELLOW = (244, 196, 66)
SMOKE = (120, 116, 108)
WHITE = (255, 255, 255)
GREY = (90, 86, 78)
LINE = (180, 172, 154)

# --- 5x7 bitmap font: '#' = on, '.' = off; bit 4 is the leftmost pixel ---
FONT = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ',': [".....", ".....", ".....", ".....", ".....", ".##..", ".#..."],
    ':': [".....", ".##..", ".....", ".....", ".....", ".##..", "....."],
    ';': [".....", ".##..", ".....", ".....", ".##..", ".#...", "....."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    '%': ["#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"],
    '$': ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    '&': [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    '*': [".....", ".#.#.", "..#..", ".#.#.", ".....", ".....", "....."],
    '#': ["#.#.#", "#.#.#", "#####", "#.#.#", "#####", "#.#.#", "#.#.#"],
    '@': [".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."],
    '_': [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    '(': ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ')': [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    '[': [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
    ']': [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    '>': ["#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."],
    '<': ["....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"],
    '~': [".....", ".....", ".##.#", "#.#.#", ".....", ".....", "....."],
    '^': ["..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    '|': ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    '\\': ["#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"],
    '{': ["...##", "..#..", "..#..", ".##..", "..#..", "..#..", "...##"],
    '}': ["##...", "..#..", "..#..", "..##.", "..#..", "..#..", "##..."],
}


def text_width(s, scale):
    """Pixel width of s at the given scale (5 px per glyph + 1 px gap)."""
    return len(s) * (5 * scale + scale) - scale


def wrap(s, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur = cur + " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg[0] for _ in range(w * h * 3))
        # fill properly: bytearray repeat trick above only sets R; do it right
        buf = bytearray(w * h * 3)
        for i in range(w * h):
            buf[i * 3] = bg[0]
            buf[i * 3 + 1] = bg[1]
            buf[i * 3 + 2] = bg[2]
        self.px = buf

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        # Clip to the canvas: without this, a rect past the right edge
        # wraps onto the next row's left edge (flat buffer arithmetic).
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x1 - x0):
                i = base + xx * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon (list of (x, y))."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def glyph(self, x, y, ch, scale, c):
        rows = FONT.get(ch.upper(), FONT['?'])
        for r, row in enumerate(rows):
            for col, bit in enumerate(row):
                if bit == '#':
                    self.rect(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            if ch == ' ':
                cx += 5 * scale + scale
                continue
            self.glyph(cx, y, ch, scale, c)
            cx += 5 * scale + scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def text_right(self, x, y, s, scale, c):
        self.text(x - text_width(s, scale), y, s, scale, c)


def png_bytes(cv):
    """Encode the canvas as a deterministic RGB PNG (filter 0 rows)."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# --- the 50 stories: (number, headline, detail) ---
# Headline <= 27 chars, detail <= 27 chars: one line each at scale 2 in
# a 328 px column (12 px per glyph). Stories 01-03 live in the climax
# panel; 04-50 fill the three region columns. Sources: SOURCES.md.
CLIMAX = [
    ("01", "RAS TANURA HIT",
     "Houthis claim hit on Saudi giant",
     "refinery, 550,000 bpd; smoke seen"),
    ("02", "TWO TANKERS HIT MINES",
     "Two tankers hit mines, explode",
     "in Strait of Hormuz, key oil route"),
    ("03", "BRENT PAST $93",
     "Brent crude past $93 a barrel;",
     "Riyadh flights cancelled"),
]

COL1 = [  # MIDDLE EAST, AFRICA, LATIN AMERICA
    ("04", "GAZA: HAMAS CHIEF KILLED", "ABOELOUF + WIFE + 2 KIDS"),
    ("05", "RIYADH ATTACK HURTS 11", "11 hurt in Riyadh"),
    ("06", "HODEIDAH PORT STRUCK", "Coalition hits Yemen port"),
    ("07", "UKRAINE HITS 2 REFINERIES", "Putin vows retaliation"),
    ("08", "RUSSIA WAR DEAD NEAR 500K", "Moscow toll: ~500,000"),
    ("09", "SUDAN DRONES KILL 19", "19 dead in Blue Nile"),
    ("10", "CAIRO FIRE: 31 DEAD", "Ring Road blaze, 27 cars"),
    ("11", "EGYPT: SUEZ REVENUE BACK", "Canal revenues recovering"),
    ("12", "IRAN FACES CASH CRUNCH", "Hardship deepens in Iran"),
    ("13", "LEBANON PLANS 2ND AIRPORT", "Second airport planned"),
    ("14", "COLOMBIA: 20 FREED", "20 freed after 17 hours"),
    ("15", "COLOMBIA: 10 YRS OF PEACE", "UN hails 10 yrs of peace"),
    ("16", "VENEZUELA DEBT $237.5BN", "Caracas reveals huge debt"),
    ("17", "BRAZIL OIL BET $122BN", "Petrobras $122bn plan"),
    ("18", "EL SALVADOR: $860M DEBT", "$860m for year-end bills"),
]

COL2 = [  # ASIA
    ("19", "INDIA: CONSTITUTION DAY", "77 years since 1949"),
    ("20", "MUMBAI 26/11: 18 YEARS", "160+ died in 2008"),
    ("21", "PAKISTANI IN ORBIT", "First Pakistani in orbit"),
    ("22", "INDIA-NEPAL: RS 15,000 CR", "Modi, Shah agree package"),
    ("23", "SARAYU-KAMALA EXPRESS", "Ayodhya-Janakpur train"),
    ("24", "IITs ADD 6,000 SEATS", "Robotics, AI, space seats"),
    ("25", "CABINET: PORTS + AIRPORT", "Rs 4,288-cr port approved"),
    ("26", "BANGLADESH WAGE +36%", "Pay up to 17,000 taka"),
    ("27", "HASINA EYES DEC 16 RETURN", "Ex-PM seeks Dhaka return"),
    ("28", "N KOREA EXPELS SWISS", "Swiss office shut in 48h"),
    ("29", "INDIA: HUMANS RUN AI WAR", "Human control of AI urged"),
    ("30", "NEPAL QUAKE 5.6", "Koshi, near China border"),
    ("31", "UAE CRASH KILLS 11", "Ras Al Khaimah road crash"),
    ("32", "VIETNAM GOES GREEN", "Sustainable farming drive"),
    ("33", "S KOREA BOOSTS EVs", "Seoul boosts EV industry"),
]

COL3 = [  # AMERICAS, EUROPE, SPORT
    ("34", "THANKSGIVING IN AMERICA", "US marks Thanksgiving Day"),
    ("35", "US CONFIDENCE NEAR HIGH", "High despite inflation"),
    ("36", "MARKETS TUMBLE ON NVIDIA", "S&P, Nasdaq fall"),
    ("37", "US TARIFF PLAN COMING", "New tariffs eyed"),
    ("38", "FED SPLIT ON INFLATION", "Split on inflation"),
    ("39", "MISSISSIPPI CRASH: 6 DEAD", "6 dead, incl. 2 children"),
    ("40", "CANADA HOLDS THE LINE", "Ottawa holds the line"),
    ("41", "POLAND: AIRSPACE VIOLATED", "Warsaw warns of violation"),
    ("42", "FRANCE EYES MINERALS", "Paris seeks minerals"),
    ("43", "UK PROBES NUCLEAR LEGACY", "Cost of tests probed"),
    ("44", "IRELAND: NEUTRALITY FIGHT", "Row over neutrality"),
    ("45", "GERMANY: MODI MEETS MERZ", "Partnership talks"),
    ("46", "SOLOMONS-AUSTRALIA PACT", "Treaty bars foreign bases"),
    ("47", "AUSTRALIA FERRY STRIKE", "Palm Beach ferries halt"),
    ("48", "SOORYAVANSHI 204 OFF 53", "15-yr-old, 28 sixes, 204"),
    ("49", "GUKESH-SINDAROV GAME 3", "Game 2 drawn in 20 moves"),
    ("50", "IPL AUCTION: 1,220 IN", "1,220 in IPL 2027 auction"),
]

NUMBERS = [
    ("31", "CAIRO DEAD"),
    ("19", "SUDAN DEAD"),
    ("$93", "BRENT"),
    ("550K", "BPD"),
    ("204", "RUNS OFF 53"),
    ("1,220", "IPL PLAYERS"),
    ("6,000", "IIT SEATS"),
    ("+36%", "WAGE RISE"),
    ("77", "YEARS"),
    ("18", "YRS SINCE 26/11"),
]

SOURCES_LINE = "SOURCES: REUTERS - AP - CNN - XINHUA - ESA - THE HINDU - JAGRAN JOSH"
DATE_CHECK = "EVERY STORY CHECKED AS 26 NOVEMBER 2026"


def draw_masthead(cv):
    cv.rect(0, 0, W, 104, INK)
    cv.text(16, 14, "THE WORLD IN ONE DAY", 2, GOLD)
    cv.text_right(W - 16, 14, "50 VERIFIED STORIES", 2, GOLD)
    cv.text_center(W // 2, 38, "THURSDAY 26 NOVEMBER 2026", 5, WHITE)
    cv.text_center(W // 2, 84, "GULF IN FLAMES  -  GAZA  -  CAIRO  -  THANKSGIVING", 2, (200, 200, 200))


def draw_refinery(cv, x0, y0, x1, y1):
    """Flat-vector refinery at dusk: towers, flames, smoke, tanker."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, (24, 16, 12))
    # dusk sky band
    cv.rect(x0, y0, x1 - x0, 58, (58, 28, 20))
    cv.disc(x0 + 300, y0 + 34, 22, (244, 196, 66))
    # smoke clouds
    for cx, cy, r in ((x0 + 60, y0 + 30, 26), (x0 + 92, y0 + 18, 20),
                      (x0 + 128, y0 + 30, 24), (x0 + 250, y0 + 22, 18),
                      (x0 + 278, y0 + 34, 22)):
        cv.disc(cx, cy, r, SMOKE)
    base = y1 - 26
    # distillation towers
    for tx, tw, th in ((x0 + 18, 26, 96), (x0 + 56, 20, 120),
                       (x0 + 88, 30, 84), (x0 + 250, 22, 108),
                       (x0 + 284, 18, 88)):
        cv.rect(tx, base - th, tw, th, (52, 48, 44))
        cv.rect(tx - 3, base - th - 6, tw + 6, 6, (70, 66, 60))
        cv.hline(tx, base - th + 22, tw, (90, 86, 78), 2)
        cv.hline(tx, base - th + 48, tw, (90, 86, 78), 2)
    # flare stack with flame
    cv.rect(x0 + 150, base - 150, 10, 150, (52, 48, 44))
    cv.poly([(x0 + 148, base - 150), (x0 + 162, base - 150),
             (x0 + 172, base - 178), (x0 + 155, base - 196),
             (x0 + 138, base - 178)], ORANGE)
    cv.poly([(x0 + 150, base - 152), (x0 + 160, base - 152),
             (x0 + 164, base - 170), (x0 + 155, base - 184),
             (x0 + 146, base - 170)], YELLOW)
    # ground flames on two towers
    cv.poly([(x0 + 56, base - 120), (x0 + 76, base - 120),
             (x0 + 84, base - 146), (x0 + 66, base - 162),
             (x0 + 48, base - 146)], ORANGE)
    cv.poly([(x0 + 250, base - 108), (x0 + 272, base - 108),
             (x0 + 280, base - 132), (x0 + 261, base - 146),
             (x0 + 242, base - 132)], ORANGE)
    # storage tanks
    for tx in (x0 + 180, x0 + 214):
        cv.rect(tx, base - 44, 30, 44, (70, 66, 60))
        cv.rect(tx - 2, base - 48, 34, 4, (90, 86, 78))
    # sea + tanker
    cv.rect(x0, y1 - 26, x1 - x0, 26, (16, 42, 66))
    cv.rect(x0 + 130, y1 - 22, 170, 12, (30, 30, 30))
    cv.rect(x0 + 150, y1 - 38, 60, 16, (176, 32, 32))
    cv.rect(x0 + 220, y1 - 38, 40, 16, (176, 32, 32))
    cv.line(x0 + 130, y1 - 22, x0 + 300, y1 - 22, (200, 200, 200))


def draw_climax(cv):
    cv.rect(0, 104, W, 232, DARKRED)
    cv.text(16, 118, "GULF IN FLAMES", 6, WHITE)
    cv.text(16, 164, "THE DAY'S BIGGEST STORY", 2, GOLD)
    y = 186
    for num, head, l1, l2 in CLIMAX:
        cv.text(16, y, num + "  " + head, 2, YELLOW)
        y += 15
        for line in (l1, l2):
            cv.text(40, y, line, 2, WHITE)
            y += 15
        y += 3
    draw_refinery(cv, 660, 112, 1008, 328)


def draw_column(cv, x, w, title, stories, y_top, y_bot):
    cv.rect(x, y_top, w, 26, BLUE)
    cv.text(x + 8, y_top + 6, title, 2, WHITE)
    y = y_top + 32
    for num, head, detail in stories:
        cv.text(x, y, num, 2, RED)
        cv.text(x + 28, y, head, 2, INK)
        y += 14
        cv.text(x + 28, y, detail, 2, GREY)
        y += 14
        cv.hline(x, y, w, LINE, 1)
        y += 3
    return y


def draw_columns(cv):
    y_top, y_bot = 344, 906
    col_w = 328
    draw_column(cv, 16, col_w, "MIDEAST - AFRICA - LATAM", COL1, y_top, y_bot)
    draw_column(cv, 352, col_w, "ASIA", COL2, y_top, y_bot)
    draw_column(cv, 688, col_w, "AMERICAS - EUROPE - SPORT", COL3, y_top, y_bot)
    cv.vline(348, y_top, y_bot - y_top, LINE, 1)
    cv.vline(684, y_top, y_bot - y_top, LINE, 1)


def draw_numbers(cv):
    cv.rect(0, 914, W, 58, INK)
    cv.text(16, 922, "THE DAY IN NUMBERS:", 2, GOLD)
    x = 16 + text_width("THE DAY IN NUMBERS:", 2) + 16
    y = 922
    for val, lab in NUMBERS[:5]:
        cv.text(x, y, val, 2, WHITE)
        x += text_width(val, 2) + 6
        cv.text(x, y, lab, 2, (170, 170, 170))
        x += text_width(lab, 2) + 18
    x = 16
    y = 942
    for val, lab in NUMBERS[5:]:
        cv.text(x, y, val, 2, WHITE)
        x += text_width(val, 2) + 6
        cv.text(x, y, lab, 2, (170, 170, 170))
        x += text_width(lab, 2) + 18


def draw_footer(cv):
    cv.text_center(W // 2, 982, SOURCES_LINE, 2, GREY)
    cv.text_center(W // 2, 1000, DATE_CHECK + "  -  @TRIFERBRIAN", 2, RED)


def build():
    cv = Canvas(W, H, CREAM)
    draw_masthead(cv)
    draw_climax(cv)
    draw_columns(cv)
    draw_numbers(cv)
    draw_footer(cv)
    return png_bytes(cv)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote", len(data), "bytes")


if __name__ == "__main__":
    main()
