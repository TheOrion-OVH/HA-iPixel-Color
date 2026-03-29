import math
import random
import colorsys
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

W = 32

def _new_frame() -> 'Image.Image':
    return Image.new("RGB", (W, W), (0, 0, 0))

class FireAnimation:
    def __init__(self):
        self.H = W + 4
        self.buf = [[0.0] * W for _ in range(self.H)]
    def next_frame(self) -> 'Image.Image':
        for x in range(W):
            self.buf[self.H-1][x] = random.uniform(0.7, 1.0)
            self.buf[self.H-2][x] = random.uniform(0.5, 0.9)
        new_buf = [row[:] for row in self.buf]
        for y in range(1, self.H-1):
            for x in range(W):
                v = (self.buf[y][x] + self.buf[y+1][x] + self.buf[y+1][(x-1) % W] + self.buf[y+1][(x+1) % W]) / 4.0
                v *= random.uniform(0.92, 0.99)
                new_buf[y-1][x] = max(0.0, v)
        self.buf = new_buf
        img = _new_frame()
        pixels = []
        for y in range(W):
            fy = y + (self.H - W)
            for x in range(W):
                t = max(0.0, min(1.0, self.buf[fy][x]))
                if t < 0.3:
                    r, g, b = int(t * 3 * 80), 0, 0
                elif t < 0.6:
                    r, g, b = 180 + int((t - 0.3) * 3 * 75), int((t - 0.3) * 3 * 80), 0
                else:
                    r, g, b = 255, 80 + int((t - 0.6) * 2.5 * 175), int((t - 0.6) * 2.5 * 60)
                pixels.append((min(255, r), min(255, g), min(255, b)))
        img.putdata(pixels)
        return img

class MatrixAnimation:
    def __init__(self):
        # We start with columns at various heights (some above the screen)
        self.cols = []
        for _ in range(W):
            self.cols.append(self._make_col(random.randint(-W, W)))
        self.buf = [[(0, 0, 0)] * W for _ in range(W)]
        
    def _make_col(self, start_y=None):
        return {
            "head": float(start_y if start_y is not None else -random.randint(5, 20)),
            "speed": random.uniform(0.5, 1.8),
            "len": random.randint(8, 24),
            "sparkle": [random.random() for _ in range(32)] # Random phase for flickers
        }

    def next_frame(self) -> 'Image.Image':
        # Fade the background for a "trail" effect
        # We use a slightly faster fade to keep it clean (0.6-0.7)
        self.buf = [[(int(r * 0.65), int(g * 0.7), int(b * 0.65)) for r, g, b in row] for row in self.buf]
        
        for x, col in enumerate(self.cols):
            col["head"] += col["speed"]
            
            # If the tail has cleared the screen, reset the column
            if col["head"] - col["len"] > W:
                self.cols[x] = self._make_col()
                col = self.cols[x]
                
            hy = int(col["head"])
            for i in range(col["len"]):
                y = hy - i
                if 0 <= y < W:
                    # Classic Matrix palette: very bright head, neon green trail
                    # With some flickering "characters"
                    flicker = math.sin(col["sparkle"][y % 32] + hy * 0.5) > 0.8
                    
                    if i == 0: # The "head" is white/very bright green
                        self.buf[y][x] = (200, 255, 200)
                    elif i < 3: # Near the head is bright green
                        self.buf[y][x] = (50, 255, 80)
                    else:
                        # Fade based on distance from head
                        intensity = (col["len"] - i) / col["len"]
                        gv = int(255 * intensity * 0.8)
                        if flicker: gv = min(255, gv + 60)
                        self.buf[y][x] = (0, gv, int(gv * 0.2))
                        
        img = _new_frame()
        img.putdata([p for row in self.buf for p in row])
        return img

class SnowAnimation:
    def __init__(self):
        self.flakes = [{"x": random.uniform(0, W), "y": random.uniform(0, W), "vy": random.uniform(0.2, 0.8), "vx": random.uniform(-0.1, 0.1), "r": random.uniform(0.4, 1.2), "bright": random.randint(180, 255), "osc": random.uniform(0, 2 * math.pi)} for _ in range(40)]
        self.sky = [(int(5 + 15 * (y / W)), int(10 + 25 * (y / W)), int(30 + 50 * (y / W))) for y in range(W)]
        self.frame = 0
    def next_frame(self) -> 'Image.Image':
        pixels = [self.sky[y] for y in range(W) for _ in range(W)]
        for fl in self.flakes:
            fl["y"] += fl["vy"]
            fl["x"] = (fl["x"] + fl["vx"] + 0.15 * math.sin(fl["osc"] + self.frame * 0.1)) % W
            if fl["y"] >= W:
                fl["y"], fl["x"], fl["vy"] = 0, random.uniform(0, W), random.uniform(0.2, 0.8)
            ix, iy = int(fl["x"]), int(fl["y"])
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < W and 0 <= ny < W:
                        fade = 1.0 - (abs(dx) + abs(dy)) * 0.4
                        bv = int(fl["bright"] * fade * fl["r"])
                        idx = ny * W + nx
                        pr, pg, pb = pixels[idx]
                        pixels[idx] = (min(255, pr + bv), min(255, pg + bv), min(255, pb + bv))
        self.frame += 1
        img = _new_frame()
        img.putdata(pixels)
        return img

class AuroraAnimation:
    def __init__(self): self.t = 0.0
    def next_frame(self) -> 'Image.Image':
        pixels = []
        for y in range(W):
            for x in range(W):
                r, g, b = 2, 2, 8
                for i in range(3):
                    freq, speed, phase = 0.18 + i * 0.07, 0.04 + i * 0.02, i * 2.1
                    wave_y = W * 0.35 + 6 * math.sin(x * freq + self.t * speed + phase)
                    dist = abs(y - wave_y)
                    width = 4.0 + 2 * math.sin(x * 0.3 + self.t * 0.03 + i)
                    intensity = math.exp(-dist * dist / (2 * width * width))
                    if i == 0:
                        g += int(1.0 * intensity * 200); b += int(0.4 * intensity * 160)
                    elif i == 1:
                        r += int(0.2 * intensity * 120); g += int(0.6 * intensity * 180); b += int(1.0 * intensity * 220)
                    else:
                        r += int(0.8 * intensity * 160); g += int(0.1 * intensity * 80); b += int(1.0 * intensity * 200)
                if random.Random(x * 1000 + y).random() > 0.94:
                    sv = int(150 + 105 * math.sin(self.t * 2 + x * y * 0.1))
                    r, g, b = max(r, sv), max(g, sv), max(b, sv)
                pixels.append((min(255, r), min(255, g), min(255, b)))
        self.t += 1.0
        img = _new_frame()
        img.putdata(pixels)
        return img

class WavesAnimation:
    def __init__(self): self.t = 0.0
    def next_frame(self) -> 'Image.Image':
        pixels = []
        for y in range(W):
            for x in range(W):
                surface = W * 0.42 + math.sin(x * 0.5 + self.t * 0.8) * 3 + math.sin(x * 0.3 - self.t * 0.5) * 2 + math.sin(x * 0.8 + self.t * 1.1) * 1.5
                depth = y - surface
                if depth < 0:
                    sky_t = max(0, min(1, (-depth) / (W * 0.5)))
                    r, g, b = int(30 + 80 * sky_t), int(80 + 100 * sky_t), int(160 + 80 * sky_t)
                    sun_d = abs(x - (W * 0.7 + 4 * math.sin(self.t * 0.2)))
                    if sun_d < 3 and depth > -8:
                        glow = max(0, 1 - sun_d / 3) * max(0, 1 - (-depth) / 8)
                        r, g, b = int(r + 200 * glow), int(g + 150 * glow), int(b + 50 * glow)
                else:
                    d_norm = min(1.0, depth / (W * 0.6))
                    r, g, b = int(20 * (1 - d_norm)), int(40 + 80 * (1 - d_norm)), int(120 + 100 * (1 - d_norm))
                    if depth < 1.5:
                        foam = max(0, 1 - depth / 1.5)
                        r, g, b = int(r + 200 * foam), int(g + 220 * foam), int(b + 240 * foam)
                    if math.sin(x * 0.6 + self.t * 1.5) * math.cos(y * 0.4 + self.t * 0.9) > 0.6:
                        r, g, b = min(255, r + 40), min(255, g + 60), min(255, b + 80)
                pixels.append((min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))))
        self.t += 0.15
        img = _new_frame()
        img.putdata(pixels)
        return img

class RainbowAnimation:
    def __init__(self): self.t = 0.0
    def next_frame(self) -> 'Image.Image':
        pixels = []
        for y in range(W):
            for x in range(W):
                r, g, b = colorsys.hsv_to_rgb((x / W + y / W * 0.3 + self.t * 0.05) % 1.0, 1.0, 0.9 + 0.1 * math.sin(x * 0.4 + y * 0.3 + self.t * 2))
                pixels.append((int(r * 255), int(g * 255), int(b * 255)))
        self.t += 0.5
        img = _new_frame()
        img.putdata(pixels)
        return img

class PlasmaAnimation:
    def __init__(self): self.t = 0.0
    def next_frame(self) -> 'Image.Image':
        pixels = []
        for y in range(W):
            for x in range(W):
                v = (math.sin(x * 0.4 + self.t) + math.sin(y * 0.3 + self.t * 0.7) + math.sin((x + y) * 0.25 + self.t * 1.3) + math.sin(math.sqrt(x * x + y * y) * 0.4 + self.t * 0.9) + 4) / 8
                r, g, b = colorsys.hsv_to_rgb(v, 1.0, 1.0)
                pixels.append((int(r * 255), int(g * 255), int(b * 255)))
        self.t += 0.12
        img = _new_frame()
        img.putdata(pixels)
        return img

class EqualizerAnimation:
    def __init__(self):
        self.bars = [random.uniform(0.1, 0.9) for _ in range(16)]
        self.targets = [random.uniform(0.1, 0.9) for _ in range(16)]
    def next_frame(self) -> 'Image.Image':
        pixels = []
        for i in range(16):
            if abs(self.targets[i] - self.bars[i]) < 0.05:
                self.targets[i] = random.uniform(0.1, 0.9)
            self.bars[i] += (self.targets[i] - self.bars[i]) * 0.2
        for y in range(W):
            for x in range(W):
                bar_idx = x // 2
                height = int(self.bars[bar_idx] * 28)
                if y >= W - height:
                    h = W - y
                    if h < 10: r, g, b = 0, 255, 0
                    elif h < 20: r, g, b = 255, 255, 0
                    else: r, g, b = 255, 0, 0
                else: r, g, b = 0, 0, 0
                pixels.append((r, g, b))
        img = _new_frame()
        img.putdata(pixels)
        return img

class PacmanAnimation:
    def __init__(self):
        self.x, self.ghost_x = -10.0, -25.0
        self.mouth_angle, self.mouth_opening = 0.0, True
    def next_frame(self) -> 'Image.Image':
        pixels = [(0, 0, 0)] * (W * W)
        self.x += 1.2; self.ghost_x += 1.2
        if self.x > W + 30: self.x, self.ghost_x = -10.0, -25.0
        if self.mouth_opening:
            self.mouth_angle += 0.15
            if self.mouth_angle >= 0.7: self.mouth_opening = False
        else:
            self.mouth_angle -= 0.15
            if self.mouth_angle <= 0.0: self.mouth_opening = True
                
        for y in range(W):
            for x in range(W):
                idx = y * W + x
                dx, dy = x - self.x, y - (W/2)
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 7.5:
                    angle = math.atan2(dy, dx)
                    if not (dx > 0 and abs(angle) < self.mouth_angle):
                        pixels[idx] = (255, 255, 0)
                elif abs(y - W/2) < 1.5 and x > self.x + 8 and x % 6 < 2:
                    pixels[idx] = (255, 255, 255)
                dx_g, dy_g = x - self.ghost_x, y - (W/2)
                if abs(dx_g) <= 5 and dy_g >= -5 and dy_g <= 6:
                    if dy_g < -1 and dx_g*dx_g + (dy_g+1)*(dy_g+1) > 25: pass
                    elif dy_g == 6 and int(dx_g) % 2 != 0: pass
                    elif dy_g in (-2, -1) and abs(int(dx_g)) in (2, 3):
                        pixels[idx] = (255, 255, 255)
                        if dx_g > 0 and int(dx_g) == 2: pixels[idx] = (0, 0, 255)
                        elif dx_g < 0 and int(dx_g) == 2: pixels[idx] = (0, 0, 255)
                    else: pixels[idx] = (255, 0, 0)
        img = _new_frame()
        img.putdata(pixels)
        return img

MINI_FONT = {
    "0": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "1": [(1,0),(0,1),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
    "2": [(0,0),(1,0),(2,0),(2,1),(0,2),(1,2),(2,2),(0,3),(0,4),(1,4),(2,4)],
    "3": [(0,0),(1,0),(2,0),(2,1),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
    "4": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(2,3),(2,4)],
    "5": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
    "6": [(0,0),(1,0),(0,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "7": [(0,0),(1,0),(2,0),(2,1),(1,2),(1,3),(1,4)],
    "8": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(1,4),(2,4)],
    "9": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(2,3),(0,4),(1,4),(2,4)],
    "-": [(0,2),(1,2),(2,2)],
    "°": [(0,0),(1,0),(0,1),(1,1)],
    "%": [(0,0),(2,1),(1,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,4)],
    "~": [(0,1),(1,0),(2,1),(1,2)],
    ":": [(0,1),(0,3)],
    "A": [(1,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "B": [(0,0),(1,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(1,4)],
    "C": [(1,0),(2,0),(0,1),(0,2),(0,3),(1,4),(2,4)],
    "D": [(0,0),(1,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4)],
    "E": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(0,3),(0,4),(1,4),(2,4)],
    "F": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(0,3),(0,4)],
    "G": [(1,0),(2,0),(0,1),(0,2),(2,2),(0,3),(2,3),(1,4),(2,4)],
    "H": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "I": [(1,0),(1,1),(1,2),(1,3),(1,4)],
    "J": [(2,0),(2,1),(2,2),(0,3),(2,3),(1,4)],
    "K": [(0,0),(2,0),(0,1),(1,1),(0,2),(0,3),(1,3),(0,4),(2,4)],
    "L": [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4)],
    "M": [(0,0),(2,0),(0,1),(1,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "N": [(0,0),(2,0),(0,1),(1,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "O": [(1,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(1,4)],
    "P": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(0,4)],
    "R": [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(2,4)],
    "S": [(1,0),(2,0),(0,1),(0,2),(1,2),(2,3),(0,4),(1,4)],
    "T": [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(1,4)],
    "U": [(0,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(1,4)],
    "V": [(0,0),(2,0),(0,1),(2,1),(0,2),(2,2),(1,3)],
    "W": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,3),(0,4),(2,4)],
    "X": [(0,0),(2,0),(0,1),(2,1),(1,2),(0,3),(2,3),(0,4),(2,4)],
    "Y": [(0,0),(2,0),(0,1),(2,1),(1,2),(1,3),(1,4)],
    "Z": [(0,0),(1,0),(2,0),(2,1),(1,2),(0,3),(0,4),(1,4),(2,4)],
    "↑": [(1,0),(0,1),(1,1),(2,1),(1,2),(1,3),(1,4)],
    "↓": [(1,0),(1,1),(1,2),(0,3),(1,3),(2,3),(1,4)],
    "☀": [(1,0),(0,1),(1,1),(2,1),(1,2)],
    "❄": [(1,0),(0,1),(1,1),(2,1),(1,2),(1,3),(1,4)],
    " ": [],
}

def draw_text(d, text, x, y, color):
    cx = x
    for ch in text.upper():
        pts = MINI_FONT.get(ch, [])
        for dx, dy in pts:
            d.point((cx + dx, y + dy), fill=color)
        cx += 4

def draw_text_shadow(d, text, x, y, color, shadow=(0,0,0)):
    draw_text(d, text, x+1, y+1, shadow)
    draw_text(d, text, x, y, color)

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

SKY_PALETTE = [
    (-90, (5, 5, 20), (10, 10, 35)),
    (-18, (10, 10, 40), (20, 15, 50)),
    (-6,  (60, 25, 80), (180, 80, 60)),
    (0,   (200, 80, 30), (240, 140, 60)),
    (8,   (100, 160, 220), (180, 210, 255)),
    (30,  (40, 120, 220), (120, 180, 255)),
    (70,  (20, 90, 200), (80, 150, 240)),
]

def sky_color(elevation):
    elev = max(-90, min(90, elevation))
    for i in range(len(SKY_PALETTE) - 1):
        e0, t0, b0 = SKY_PALETTE[i]
        e1, t1, b1 = SKY_PALETTE[i + 1]
        if e0 <= elev <= e1:
            frac = (elev - e0) / (e1 - e0) if e1 != e0 else 0.0
            return lerp_color(t0, t1, frac), lerp_color(b0, b1, frac)
    if elev < SKY_PALETTE[0][0]:
        return SKY_PALETTE[0][1], SKY_PALETTE[0][2]
    return SKY_PALETTE[-1][1], SKY_PALETTE[-1][2]

def _parse_time(iso_str):
    try:
        return iso_str.split("T")[1][:5]
    except Exception:
        return "--:--"

def _darken(col, factor=0.45):
    return tuple(int(c * factor) for c in col)

def _draw_panel_bg(d, panel_col=(18, 24, 42), border_col=(80, 110, 180)):
    for x in range(22, W):
        for y in range(W):
            d.point((x, y), fill=panel_col)
    d.line([(21, 0), (21, W - 1)], fill=border_col)
    d.line([(22, 0), (22, W - 1)], fill=(30, 40, 70))

def _draw_separator(d, y, col=(50, 70, 120)):
    d.line([(22, y), (W - 1, y)], fill=col)

class SunAnimation:
    STAR_COUNT = 22

    def __init__(self, data):
        self.frame = 0
        self.state = data.get("state", "above_horizon")
        self.elevation = float(data.get("elevation", 20))
        self.azimuth = float(data.get("azimuth", 180))
        self.next_rising = data.get("next_rising", "")
        self.next_setting = data.get("next_setting", "")
        self._current_y = self._target_sun_y()
        self._current_x = self._target_sun_x()
        random.seed(42)
        self._stars = [
            (random.randint(1, 19), random.randint(1, 24), random.random())
            for _ in range(self.STAR_COUNT)
        ]
        random.seed()

    def _target_sun_y(self):
        t = (self.elevation + 90) / 180.0
        return int(lerp(24, 2, t))

    def _target_sun_x(self):
        if self.azimuth < 90: return 1
        if self.azimuth > 270: return 19
        t = (self.azimuth - 90) / 180.0
        return int(lerp(2, 18, t))

    def _draw_panel(self, d):
        # Supprimé comme demandé pour laisser juste le soleil
        pass

    def next_frame(self):
        is_day = self.state == "above_horizon"
        self._current_y = lerp(self._current_y, self._target_sun_y(), 0.15)
        # On utilise une zone plus large car plus de panneau
        self._current_x = lerp(self._current_x, self._target_sun_x_full(), 0.15)
        cy, cx = int(round(self._current_y)), int(round(self._current_x))
        top_col, bot_col = sky_color(self.elevation if is_day else -30)

        img = Image.new("RGB", (W, W), top_col)
        d = ImageDraw.Draw(img)

        for row in range(W):
            t = row / (W - 1)
            d.line([(0, row), (W - 1, row)], fill=lerp_color(top_col, bot_col, t))

        if not is_day:
            for sx, sy, phase in self._stars:
                twinkle_val = 0.5 + 0.5 * math.sin(self.frame * 0.07 + phase * 6.28)
                brightness = int(80 + 175 * twinkle_val)
                d.point((sx, sy), fill=(brightness, brightness, min(255, brightness + 30)))

        horizon_y = 26
        d.line([(0, horizon_y), (W - 1, horizon_y)], fill=(40, 55, 90))
        d.line([(0, horizon_y + 1), (W - 1, horizon_y + 1)], fill=(25, 35, 60))

        if is_day and cy <= horizon_y:
            self._draw_sun(d, cx, cy)
        elif not is_day and cy <= horizon_y:
            self._draw_moon(d, cx, cy)

        if self.frame % 2 == 0:
            reflet_col = (255, 140, 50) if is_day else (100, 110, 220)
            for _ in range(4):
                ry = random.randint(horizon_y + 1, W - 1)
                rx = cx + random.randint(-8, 8)
                if 0 <= rx < W:
                    d.point((rx, ry), fill=reflet_col)

        self.frame += 1
        return img

    def _target_sun_x_full(self):
        # Azimuth mapping sur tout l'écran (W=32)
        if self.azimuth < 45: return 2
        if self.azimuth > 315: return 2
        # On map 45-315 sur 2-30
        t = (self.azimuth - 45) / 270.0
        return int(lerp(2, 29, t))

    def _draw_sun(self, d, cx, cy):
        pulse = math.sin(self.frame * 0.12) * 1.8
        outer_r = int(9 + pulse)
        for r in range(outer_r, 3, -1):
            fade = max(0, 255 - (outer_r - r) * 28)
            orange = max(0, 160 - (outer_r - r) * 18)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(fade, orange, 0))
        for i in range(8):
            angle = math.radians(i * 45 + self.frame * 2.5)
            r1 = 5
            r2 = int(10 + pulse + (2 if i % 2 == 0 else 0))
            ray_col = (255, 200, 50) if i % 2 == 0 else (255, 140, 20)
            d.line([
                (cx + math.cos(angle) * r1, cy + math.sin(angle) * r1),
                (cx + math.cos(angle) * r2, cy + math.sin(angle) * r2)
            ], fill=ray_col)
        d.ellipse([cx-4, cy-4, cx+4, cy+4], fill=(255, 230, 60))
        d.ellipse([cx-2, cy-3, cx+2, cy+0], fill=(255, 255, 220))

    def _draw_moon(self, d, cx, cy):
        d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=(230, 230, 255))
        top_col, _ = sky_color(-30)
        d.ellipse([cx-2, cy-5, cx+8, cy+3], fill=top_col)
        d.point((cx-3, cy-1), fill=(255, 255, 255))
        d.point((cx-2, cy+2), fill=(200, 200, 230))
        d.point((cx-1, cy-3), fill=(220, 220, 250))


class WeatherAnimation:
    PARTICLE_COUNT = 12

    def __init__(self, data):
        self.frame = 0
        self.state = data.get("state", "cloudy")
        self.temp = int(round(float(data.get("temp", 0))))
        self.humidity = int(round(float(data.get("humidity", 0))))
        self.wind = int(round(float(data.get("wind", 0))))
        self.feels_like = int(round(float(data.get("feels_like", self.temp))))
        self._particles = [
            {
                "x": random.uniform(2, 19),
                "y": random.uniform(2, 22),
                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(1.0, 2.6),
                "phase": random.uniform(0, math.tau),
                "splash": 0,
            }
            for _ in range(self.PARTICLE_COUNT)
        ]
        self._fog_layers = [
            {"x": random.uniform(0, W), "speed": random.uniform(0.04, 0.12), "y": y, "alpha": a}
            for y, a in [(12, 110), (16, 85), (20, 65), (24, 50)]
        ]

    def _draw_bg(self, d):
        for row in range(W):
            t = row / (W - 1)
            d.line([(0, row), (W-1, row)], fill=lerp_color((28, 40, 85), (48, 62, 108), t))

    def _draw_cloud(self, d, cx, cy, fill, shadow):
        d.ellipse([cx-7, cy-3, cx+7, cy+5], fill=shadow)
        d.ellipse([cx-4, cy-6, cx+2, cy+2], fill=shadow)
        d.ellipse([cx-7, cy-4, cx+7, cy+4], fill=fill)
        d.ellipse([cx-4, cy-7, cx+2, cy+1], fill=fill)
        d.ellipse([cx+1, cy-5, cx+5, cy-1], fill=fill)

    def _draw_panel(self, d, flash=False):
        _draw_panel_bg(d)

        if self.temp > 25:
            t_col = (255, 120, 60)
        elif self.temp > 15:
            t_col = (255, 200, 80)
        elif self.temp > 5:
            t_col = (160, 220, 255)
        else:
            t_col = (120, 180, 255)
        if flash:
            t_col = (255, 255, 200)

        draw_text(d, f"{self.temp}°", 23, 10, t_col)
        
        _draw_separator(d, 16)

        if self.humidity >= 80:
            h_col = (80, 160, 255)
        elif self.humidity >= 60:
            h_col = (120, 200, 200)
        else:
            h_col = (100, 210, 130)

        # On décale pour faire de la place au %
        draw_text(d, f"{self.humidity}", 23, 21, h_col)
        draw_text(d, "%", 28, 26, (100, 150, 255))

    def _draw_icon(self, d, img):
        s, cx, cy = self.state, 10, 12

        if s in ("sunny", "clear-night"):
            is_sun = s == "sunny"
            c1 = (255, 220, 0) if is_sun else (210, 210, 255)
            c2 = (255, 255, 200) if is_sun else (255, 255, 255)
            pulse = math.sin(self.frame * 0.18) * 1.8
            r = 6 + pulse
            for layer in range(4):
                lr = r + layer * 1.5
                alpha_factor = max(0, 1 - layer * 0.3)
                col = tuple(int(c * alpha_factor) for c in c1)
                d.ellipse([cx-lr, cy-lr, cx+lr, cy+lr], fill=col)
            d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=c1)
            d.ellipse([cx-2, cy-3, cx+2, cy+1], fill=c2)
            if is_sun:
                for i in range(8):
                    angle = math.radians(i * 45 + self.frame * 2)
                    r1, r2 = 7, int(10 + pulse)
                    d.line([
                        (cx + math.cos(angle)*r1, cy + math.sin(angle)*r1),
                        (cx + math.cos(angle)*r2, cy + math.sin(angle)*r2)
                    ], fill=(255, 180, 0))

        elif s == "partlycloudy":
            pulse = math.sin(self.frame * 0.1) * 0.8
            d.ellipse([cx-3+int(pulse), cy-7, cx+8+int(pulse), cy+3], fill=(255, 210, 30))
            self._draw_cloud(d, cx, cy+2, (210, 215, 225), (155, 158, 168))

        elif s in ("rainy", "pouring", "drizzle"):
            intensity = 2.2 if s == "pouring" else (0.9 if s == "drizzle" else 1.5)
            cloud_col = (100, 120, 165) if s == "pouring" else (130, 148, 188)
            self._draw_cloud(d, cx, cy, cloud_col, _darken(cloud_col, 0.65))
            floor_y = 24
            for p in self._particles:
                p["y"] += p["vy"] * intensity
                if p["y"] >= floor_y:
                    p["splash"] = 4
                    p["y"] = 12.0
                    p["x"] = random.uniform(2, 18)
                    p["vy"] = random.uniform(1.0, 2.6)
                rain_col = (80, 160, 255) if s == "pouring" else (120, 190, 255)
                d.line([
                    (int(p["x"]), int(p["y"])),
                    (int(p["x"]) - 1, int(p["y"]) + 2)
                ], fill=rain_col)
                if p["splash"] > 0:
                    sx = int(p["x"])
                    d.point((sx-2, floor_y), fill=(140, 200, 255))
                    d.point((sx+2, floor_y), fill=(140, 200, 255))
                    d.point((sx, floor_y-1), fill=(180, 220, 255))
                    p["splash"] -= 1

        elif s in ("snowy", "snowy-rainy"):
            self._draw_cloud(d, cx, cy, (215, 218, 228), (175, 178, 188))
            for p in self._particles:
                drift = math.sin(self.frame * 0.06 + p["phase"]) * 0.5
                p["y"] += 0.35 if p["phase"] < math.pi else 0.55
                p["x"] += drift
                if p["y"] > 25:
                    p["y"] = 12.0
                    p["x"] = random.uniform(2, 19)
                px, py = int(p["x"]) % 20, int(p["y"])
                d.point((px, py), fill=(255, 255, 255))
                if p["phase"] < math.pi and py < 24:
                    d.point((px-1, py), fill=(200, 210, 235))
                    d.point((px+1, py), fill=(200, 210, 235))
                    d.point((px, py-1), fill=(220, 225, 245))

        elif s in ("lightning", "lightning-rainy", "thunder"):
            flash = (self.frame % 20) < 3
            c = (30, 30, 60) if flash else (70, 70, 100)
            s_c = _darken(c, 0.6)
            self._draw_cloud(d, cx, cy, c, s_c)
            bolt_col = (255, 255, 100) if flash else (200, 200, 50)
            bolt = [(cx+1, cy+4), (cx-2, cy+9), (cx+1, cy+8), (cx-2, cy+14)]
            d.line(bolt, fill=bolt_col)
            if flash:
                overlay = Image.new("RGB", (W, W), (70, 70, 50))
                img.paste(overlay, mask=Image.new("L", (W, W), 55))

        elif s in ("fog", "mist"):
            for i, layer in enumerate(self._fog_layers):
                layer["x"] = (layer["x"] + layer["speed"]) % (W + 12)
                lx = int(layer["x"]) - 6
                fog_img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
                fog_col = (190, 195, 210, layer["alpha"])
                ImageDraw.Draw(fog_img).rectangle(
                    [lx, layer["y"] - 2, lx + W + 6, layer["y"] + 3],
                    fill=fog_col
                )
                img.paste(fog_img.convert("RGB"), (0, 0), fog_img.split()[3])
        else:
            wave = int(math.sin(self.frame * 0.08) * 2)
            self._draw_cloud(d, cx, cy + wave, (170, 175, 185), (130, 132, 142))
            self._draw_cloud(d, cx + 4, cy - 4 + wave // 2, (190, 195, 205), (150, 152, 162))

    def next_frame(self):
        img = Image.new("RGB", (W, W), (0, 0, 0))
        d = ImageDraw.Draw(img)
        self._draw_bg(d)
        self._draw_icon(d, img)
        flash = self.state in ("lightning", "lightning-rainy", "thunder") and (self.frame % 20) < 3
        d = ImageDraw.Draw(img)
        self._draw_panel(d, flash)
        self.frame += 1
        return img


class Particle:
    def __init__(self, x: float, y: float, col: tuple[int, int, int], v: float = 0.0, vx: float = 0.0, vy: float = 0.0):
        self.x = x
        self.y = y
        self.col = col
        self.v = v
        self.vx = vx
        self.vy = vy
        self.life = 1.0


class ConfettiAnimation:
    def __init__(self, data=None):
        self.frame = 0
        self.particles = []
        for _ in range(50):
            self.particles.append(Particle(
                x=float(random.randint(0, W - 1)),
                y=float(random.randint(0, W - 1)),
                col=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                v=random.uniform(0.5, 1.5)
            ))

    def next_frame(self):
        img = Image.new("RGB", (W, W), (0, 0, 0))
        d = ImageDraw.Draw(img)
        for p in self.particles:
            p.y = (p.y + p.v) % float(W)
            p.x = (p.x + math.sin(self.frame * 0.15 + p.y * 0.5)) % float(W)
            d.point((int(p.x), int(p.y)), fill=p.col)
        self.frame += 1
        return img


class FireworkAnimation:
    def __init__(self, data=None):
        self.frame = 0
        self.state = "launch"
        self.x = 0.0
        self.y = 0.0
        self.vy = 0.0
        self.explode_y = 0.0
        self.particles = []
        self.reset()

    def reset(self):
        self.x = float(random.randint(5, W - 6))
        self.y = float(W - 1)
        self.vy = -random.uniform(0.9, 1.4)
        self.explode_y = float(random.randint(4, 12))
        self.particles = []
        self.state = "launch"

    def next_frame(self):
        img = Image.new("RGB", (W, W), (0, 0, 0))
        d = ImageDraw.Draw(img)
        if self.state == "launch":
            self.y += self.vy
            d.line([(self.x, int(self.y)), (self.x, int(self.y) + 2)], fill=(220, 220, 230))
            if self.y <= self.explode_y:
                self.state = "explode"
                col = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                for _ in range(25):
                    angle = random.uniform(0, 2 * math.pi)
                    v = random.uniform(0.4, 2.2)
                    self.particles.append(Particle(
                        x=self.x,
                        y=self.y,
                        vx=math.cos(angle) * v,
                        vy=math.sin(angle) * v,
                        col=col
                    ))
        else:
            active = False
            for p in self.particles:
                p.life -= 0.04
                if p.life > 0:
                    p.x += p.vx
                    p.y += p.vy
                    p.vy += 0.04
                    c = tuple(int(c * p.life) for c in p.col)
                    d.point((int(p.x), int(p.y)), fill=c) # type: ignore
                    active = True
            if not active:
                self.reset()
        self.frame += 1
        return img


class SnakeAnimation:
    def __init__(self, data=None):
        self.frame = 0
        self.snake = [(16, 16), (16, 17), (16, 18)]
        self.v_dir = (0, -1)
        self.food = (random.randint(2, W - 3), random.randint(2, W - 3))

    def next_frame(self):
        if self.frame % 3 == 0:
            hx, hy = self.snake[0]
            fx, fy = self.food
            if hx < fx: new_dir = (1, 0)
            elif hx > fx: new_dir = (-1, 0)
            elif hy < fy: new_dir = (0, 1)
            else: new_dir = (0, -1)
            self.v_dir = new_dir

            dx, dy = self.v_dir
            new_h = ((hx + dx) % W, (hy + dy) % W)
            self.snake.insert(0, new_h)
            if new_h == self.food:
                self.food = (random.randint(2, W - 3), random.randint(2, W - 3))
            else:
                self.snake.pop()

        img = Image.new("RGB", (W, W), (5, 5, 15))
        d = ImageDraw.Draw(img)
        for i, (sx, sy) in enumerate(self.snake):
            col = (0, 255, 100) if i == 0 else (0, 160, 60)
            d.point((sx, sy), fill=col)
        d.point(self.food, fill=(255, 50, 50))
        self.frame += 1
        return img


class TetrisAnimation:
    def __init__(self, data=None):
        self.frame = 0
        self.grid = [[(0, 0, 0) for _ in range(14)] for _ in range(32)]
        self.pieces = [
            [(0, 0), (1, 0), (0, 1), (1, 1)],  # O
            [(0, 0), (0, 1), (0, 2), (0, 3)],  # I
            [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z
            [(1, 0), (0, 1), (1, 1), (2, 1)],  # T
            [(0, 0), (0, 1), (1, 1), (2, 1)],  # L
        ]
        self.colors = [(255, 255, 0), (0, 255, 255), (255, 0, 0), (180, 0, 255), (255, 165, 0)]
        self.p_idx = 0
        self.p_col = (0, 0, 0)
        self.px, self.py = 0, 0
        self.reset_piece()

    def reset_piece(self):
        self.p_idx = random.randint(0, len(self.pieces) - 1)
        self.p_col = self.colors[self.p_idx]
        self.px, self.py = 6, 0

    def next_frame(self):
        if self.frame % 4 == 0:
            self.py += 1
            if self.py >= 28:
                for dx, dy in self.pieces[self.p_idx]:
                    yy = self.py + dy
                    if 0 <= yy < 32:
                        self.grid[yy][self.px + dx] = self.p_col
                self.reset_piece()
                if any(any(c != (0, 0, 0) for c in self.grid[y]) for y in range(2)):
                    self.grid = [[(0, 0, 0) for _ in range(14)] for _ in range(32)]

        img = Image.new("RGB", (W, W), (18, 18, 30))
        d = ImageDraw.Draw(img)
        off = 9
        for y in range(32):
            for x in range(14):
                if self.grid[y][x] != (0, 0, 0):
                    d.point((x + off, y), fill=self.grid[y][x]) # type: ignore
        for dx, dy in self.pieces[self.p_idx]:
            d.point((self.px + dx + off, self.py + dy), fill=self.p_col) # type: ignore
        self.frame += 1
        return img


class DinoAnimation:
    def __init__(self, data=None):
        self.frame = 0
        self.dy, self.dvy = 24.0, 0.0
        self.cactus_x = float(W)
        self.ground_y = 26

    def next_frame(self):
        img = Image.new("RGB", (W, W), (240, 240, 240))
        d = ImageDraw.Draw(img)
        d.line([(0, self.ground_y + 1), (W, self.ground_y + 1)], fill=(100, 100, 100))

        if self.cactus_x < 12 and self.dy >= 24:
            self.dvy = -2.2

        self.dy += self.dvy
        if self.dy < 24:
            self.dvy += 0.25
        else:
            self.dy, self.dvy = 24.0, 0.0

        self.cactus_x -= 1.2
        if self.cactus_x < -5:
            self.cactus_x = float(W + random.randint(0, 10))

        # Dino
        dx, dy = 5, int(self.dy)
        d.rectangle([dx, dy - 4, dx + 3, dy], fill=(80, 80, 80))
        d.point((dx + 4, dy - 4), fill=(80, 80, 80))

        # Cactus
        cx = int(self.cactus_x)
        d.rectangle([cx, 22, cx + 1, 26], fill=(40, 120, 40))

        self.frame += 1
        return img


class PenguinAnimation:
    def __init__(self, data=None):
        self.frame = 0

    def next_frame(self):
        img = Image.new("RGB", (W, W), (180, 220, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 20, W, W], fill=(255, 255, 255))

        off = int(math.sin(self.frame * 0.1) * 10)
        px, py = 12 + off, 18
        d.ellipse([px, py, px + 8, py + 8], fill=(30, 30, 30))
        d.ellipse([px + 2, py + 2, px + 6, py + 7], fill=(255, 255, 255))
        d.point((px + 7 if off > 0 else px, py + 3), fill=(255, 160, 0))

        self.frame += 1
        return img


class RPSAnimation:
    def __init__(self, data):
        self.frame = 0
        self.user_choice = str(data.get("choice", "pierre")).lower()
        self.pc_choice = str(random.choice(["pierre", "feuille", "ciseaux"]))
        self.winner = self._get_winner()

    def _get_winner(self):
        u, p = self.user_choice, self.pc_choice
        if u == p:
            return "EGALITE"
        win_map = {"pierre": "ciseaux", "feuille": "pierre", "ciseaux": "feuille"}
        return "GAGNE !" if win_map.get(u) == p else "PERDU"

    def _draw_icon(self, d, choice: str, x: int, y: int):
        # Simplified icons for robustness
        if choice == "pierre":
            d.rectangle([x, y + 2, x + 8, y + 8], fill=(120, 120, 120))
        elif choice == "feuille":
            d.rectangle([x + 1, y, x + 7, y + 10], fill=(220, 220, 220))
        else:  # ciseaux
            d.rectangle([x, y, x + 2, y + 2], fill=(255, 50, 50))
            d.rectangle([x + 6, y, x + 8, y + 2], fill=(255, 50, 50))
            d.line([(x + 1, y + 2), (x + 7, y + 8)], fill=(150, 150, 150))
            d.line([(x + 7, y + 2), (x + 1, y + 8)], fill=(150, 150, 150))

    def next_frame(self):
        img = Image.new("RGB", (W, W), (10, 10, 30))
        d = ImageDraw.Draw(img)

        # Show Result immediately (No countdown)
        self._draw_icon(d, self.user_choice, 2, 6)
        self._draw_icon(d, self.pc_choice, 20, 6)
        draw_text(d, "VS", 14, 10, (255, 200, 0))
        
        res_col = (100, 255, 100) if "GAGNE" in self.winner else (255, 100, 100)
        if self.winner == "EGALITE":
            res_col = (200, 200, 200)
        
        draw_text(d, self.winner, int((W - len(self.winner)*4)/2), 22, res_col)

        self.frame += 1
        return img
