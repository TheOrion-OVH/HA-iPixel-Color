import math
import random
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

W = 32

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
    "%": [(0,0),(2,0),(0,1),(1,1),(2,1),(1,2),(0,3),(2,3),(2,4),(0,4)],
    "~": [(0,1),(1,0),(2,1),(1,2)],
    "^": [(1,0),(0,1),(2,1)],
    "v": [(0,0),(2,0),(1,1)],
    "+": [(1,0),(0,1),(1,1),(2,1),(1,2)],
    " ": [],
}

def draw_text(d, text, x, y, color):
    cx = x
    for ch in text:
        pts = MINI_FONT.get(ch, [])
        for dx, dy in pts:
            d.point((cx + dx, y + dy), fill=color)
        cx += 4

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

SKY_PALETTE = [
    (-90, (5, 5, 20), (10, 10, 35)),
    (-18, (10, 10, 40), (20, 15, 50)),
    (-6, (60, 25, 80), (180, 80, 60)),
    (0, (200, 80, 30), (240, 140, 60)),
    (8, (100, 160, 220), (180, 210, 255)),
    (30, (40, 120, 220), (120, 180, 255)),
    (70, (20, 90, 200), (80, 150, 240)),
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

class SunAnimation:
    STAR_COUNT = 18

    def __init__(self, data):
        self.frame = 0
        self.state = data.get("state", "above_horizon")
        self.elevation = float(data.get("elevation", 20))
        self._current_y = self._target_sun_y()
        random.seed(42)
        self._stars = [(random.randint(1, W - 2), random.randint(1, 20)) for _ in range(self.STAR_COUNT)]
        random.seed()

    def _target_sun_y(self):
        t = (self.elevation + 90) / 180.0
        return int(lerp(24, 3, t))

    def next_frame(self) -> 'Image.Image':
        is_day = self.state == "above_horizon"
        target_y = self._target_sun_y()
        self._current_y = lerp(self._current_y, target_y, 0.15)
        cy, cx = int(round(self._current_y)), 16
        top_col, bot_col = sky_color(self.elevation if is_day else -30)
        img = Image.new("RGB", (W, W), top_col)
        d = ImageDraw.Draw(img)
        for row in range(W):
            t = row / (W - 1)
            d.line([(0, row), (W - 1, row)], fill=lerp_color(top_col, bot_col, t))
        if not is_day:
            for i, (sx, sy) in enumerate(self._stars):
                brightness = 255 if (i + self.frame // 4) % 7 != 0 else 100
                d.point((sx, sy), fill=(brightness, brightness, brightness))
        horizon_y = 26
        d.line([(0, horizon_y), (W - 1, horizon_y)], fill=(30, 40, 80))
        if is_day and cy <= horizon_y:
            self._draw_sun(d, cx, cy)
        elif not is_day and cy <= horizon_y:
            self._draw_moon(d, cx, cy)
        reflet_col = (255, 130, 40) if is_day else (80, 90, 200)
        if self.frame % 3 != 0:
            for _ in range(4):
                ry, rx = random.randint(horizon_y, W - 1), random.randint(8, W - 8)
                d.point((rx, ry), fill=reflet_col)
        self.frame += 1
        return img

    def _draw_sun(self, d, cx, cy):
        pulse = math.sin(self.frame * 0.15) * 1.5
        halo_r = int(8 + pulse)
        for r in range(halo_r, 4, -1):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, max(0, 180 - r * 10), 0))
        ray_colors = [(255, 140, 0), (255, 140, 100)]
        for i in range(8):
            angle = math.radians(i * 45 + self.frame * 2)
            r1, r2 = 5, int(9 + pulse + (1 if i % 2 == 0 else -1))
            d.line([(cx + math.cos(angle) * r1, cy + math.sin(angle) * r1), (cx + math.cos(angle) * r2, cy + math.sin(angle) * r2)], fill=ray_colors[i % 2])
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 220, 0))
        d.ellipse([cx - 2, cy - 3, cx + 2, cy + 1], fill=(255, 255, 210))

    def _draw_moon(self, d, cx, cy):
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(210, 210, 255))
        top_col, _ = sky_color(-30)
        d.ellipse([cx - 2, cy - 5, cx + 8, cy + 3], fill=top_col)
        d.arc([cx - 5, cy - 5, cx + 1, cy + 1], start=200, end=320, fill=(255, 255, 255))

class WeatherAnimation:
    PARTICLE_COUNT = 10

    def __init__(self, data):
        self.frame = 0
        self.state = data.get("state", "cloudy")
        self.temp = int(round(float(data.get("temp", 0))))
        self.humidity = int(round(float(data.get("humidity", 0))))
        self._particles = [{"x": random.uniform(2, 20), "y": random.uniform(2, 22), "vx": random.uniform(-0.3, 0.3), "vy": random.uniform(1.2, 2.8), "phase": random.uniform(0, math.tau), "splash": 0} for _ in range(self.PARTICLE_COUNT)]
        self._fog_layers = [{"x": random.uniform(0, W), "speed": random.uniform(0.05, 0.15), "y": y, "alpha": a} for y, a in [(14, 120), (18, 90), (22, 70)]]

    def _draw_bg(self, d):
        for row in range(W):
            t = row / (W - 1)
            d.line([(0, row), (W - 1, row)], fill=lerp_color((30, 45, 90), (50, 65, 110), t))

    def _draw_cloud(self, d, cx, cy, fill, shadow):
        d.ellipse([cx - 7, cy - 3, cx + 7, cy + 5], fill=shadow)
        d.ellipse([cx - 4, cy - 6, cx + 2, cy + 2], fill=shadow)
        d.ellipse([cx - 7, cy - 4, cx + 7, cy + 4], fill=fill)
        d.ellipse([cx - 4, cy - 7, cx + 2, cy + 1], fill=fill)

    def _draw_icon(self, d, img):
        s, cx, cy = self.state, 11, 12
        if s in ("sunny", "clear-night"):
            c1, c2 = ((255, 220, 0) if s == "sunny" else (210, 210, 255)), ((255, 255, 200) if s == "sunny" else (255, 255, 255))
            pulse = math.sin(self.frame * 0.2) * 1.5
            d.ellipse([cx - 6 - pulse, cy - 6 - pulse, cx + 6 + pulse, cy + 6 + pulse], fill=(c1[0] // 2, c1[1] // 2, c1[2] // 2))
            d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=c1)
            d.ellipse([cx - 2, cy - 3, cx + 2, cy + 1], fill=c2)
        elif s == "partlycloudy":
            d.ellipse([cx - 3, cy - 5, cx + 7, cy + 5], fill=(255, 200, 0))
            self._draw_cloud(d, cx, cy + 2, (200, 200, 200), (150, 150, 150))
        elif s in ("rainy", "pouring", "drizzle"):
            intensity = 1.8 if s == "pouring" else 1.2
            self._draw_cloud(d, cx, cy, (120, 140, 180), (80, 90, 120))
            floor_y = 24
            for p in self._particles:
                p["y"] += p["vy"] * intensity
                if p["y"] >= floor_y:
                    p["splash"], p["y"], p["x"], p["vy"] = 3, 12.0, random.uniform(3, 18), random.uniform(1.2, 2.8)
                d.line([(int(p["x"]), int(p["y"])), (int(p["x"]), int(p["y"]) + 2)], fill=(100, 180, 255))
                if p["splash"] > 0:
                    d.point((int(p["x"]) - 1, floor_y), fill=(140, 200, 255))
                    d.point((int(p["x"]) + 1, floor_y), fill=(140, 200, 255))
                    p["splash"] -= 1
        elif s in ("snowy", "snowy-rainy"):
            self._draw_cloud(d, cx, cy, (220, 220, 230), (180, 180, 190))
            for p in self._particles:
                p["y"] += (0.3 if p["phase"] < math.pi else 0.5)
                p["x"] += math.sin(self.frame * 0.08 + p["phase"]) * 0.4
                if p["y"] > 25: p["y"], p["x"] = 12.0, random.uniform(3, 19)
                px, py = int(p["x"]) % W, int(p["y"])
                d.point((px, py), fill=(255, 255, 255))
                if p["phase"] < math.pi and py < 24:
                    d.point((px - 1, py), fill=(200, 200, 220))
                    d.point((px + 1, py), fill=(200, 200, 220))
        elif s in ("lightning", "lightning-rainy", "thunder"):
            flash = (self.frame % 20) < 3
            self._draw_cloud(d, cx, cy, ((40, 40, 70) if flash else (80, 80, 110)), ((25, 25, 50) if flash else (50, 50, 80)))
            d.line([(cx, cy + 4), (cx - 3, cy + 10), (cx + 1, cy + 9), (cx - 1, cy + 16)], fill=((255, 255, 100) if flash else (200, 200, 50)))
            if flash: img.paste(Image.new("RGB", (W, W), (80, 80, 60)), mask=Image.new("L", (W, W), 60))
        elif s in ("fog", "mist"):
            for layer in self._fog_layers:
                layer["x"] = (layer["x"] + layer["speed"]) % (W + 10)
                lx = int(layer["x"]) - 5
                fog_img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
                ImageDraw.Draw(fog_img).rectangle([lx, layer["y"] - 2, lx + W + 5, layer["y"] + 3], fill=(200, 200, 210, layer["alpha"]))
                img.paste(fog_img.convert("RGB"), (0, 0), fog_img.split()[3])
        else:
            self._draw_cloud(d, cx, cy, (180, 180, 180), (140, 140, 140))
            self._draw_cloud(d, cx + 5, cy - 3, (200, 200, 200), (160, 160, 160))

    def _draw_panel(self, d, flash=False):
        d.line([(21, 0), (21, W - 1)], fill=(100, 120, 160))
        t_col = ((255, 255, 255) if flash else ((255, 160, 80) if self.temp > 15 else (140, 220, 255)))
        draw_text(d, f"{self.temp}°", 23, 4, t_col)
        d.line([(22, 14), (31, 14)], fill=(80, 100, 140))
        h_col = ((255, 255, 255) if flash else ((100, 200, 100) if self.humidity < 60 else (100, 180, 255)))
        draw_text(d, "~", 23, 16, (100, 150, 200))
        draw_text(d, f"{self.humidity}%", 23, 22, h_col)

    def next_frame(self) -> 'Image.Image':
        img = Image.new("RGB", (W, W), (0, 0, 0))
        d = ImageDraw.Draw(img)
        self._draw_bg(d)
        self._draw_icon(d, img)
        for x in range(22, W):
            for y in range(W):
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (r // 2 + 18, g // 2 + 22, b // 2 + 38))
        d = ImageDraw.Draw(img)
        self._draw_panel(d, (self.state in ("lightning", "lightning-rainy", "thunder") and (self.frame % 20) < 3))
        self.frame += 1
        return img