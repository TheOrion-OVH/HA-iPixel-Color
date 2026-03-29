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
    "%": [(0,0),(2,1),(1,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,4)],
    "~": [(0,1),(1,0),(2,1),(1,2)],
    ":": [(0,1),(0,3)],
    "A": [(1,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "C": [(1,0),(2,0),(0,1),(0,2),(0,3),(1,4),(2,4)],
    "D": [(0,0),(1,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(1,4)],
    "E": [(0,0),(1,0),(2,0),(0,1),(0,2),(1,2),(0,3),(0,4),(1,4),(2,4)],
    "H": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "I": [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(0,4),(1,4),(2,4)],
    "L": [(0,0),(0,1),(0,2),(0,3),(0,4),(1,4),(2,4)],
    "M": [(0,0),(2,0),(0,1),(1,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "N": [(0,0),(2,0),(0,1),(1,1),(2,1),(0,2),(2,2),(0,3),(2,3),(0,4),(2,4)],
    "O": [(1,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(1,4)],
    "R": [(0,0),(1,0),(0,1),(2,1),(0,2),(1,2),(0,3),(2,3),(0,4),(2,4)],
    "S": [(1,0),(2,0),(0,1),(0,2),(1,2),(2,3),(0,4),(1,4)],
    "T": [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(1,4)],
    "U": [(0,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(2,3),(1,4)],
    "W": [(0,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(1,3),(2,3),(0,4),(2,4)],
    "↑": [(1,0),(0,1),(1,1),(2,1),(1,2),(1,3),(1,4)],
    "↓": [(1,0),(1,1),(1,2),(0,3),(1,3),(2,3),(1,4)],
    "☀": [(1,0),(0,1),(1,1),(2,1),(1,2)],
    "❄": [(1,0),(0,1),(1,1),(2,1),(1,2),(1,3),(1,4)],
    " ": [],
}

def draw_text(d, text, x, y, color):
    cx = x
    for ch in text:
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
        _draw_panel_bg(d)
        is_next_set = self.state == "above_horizon"
        
        # Petit icône décorative à la place du texte
        y_center = 16
        icon_col = (255, 120, 30) if is_next_set else (180, 200, 255)
        if is_next_set:
            d.point((26, y_center), fill=(255, 100, 0)) 
            d.line([(24, y_center+1), (28, y_center+1)], fill=(255, 160, 0))
        else:
            d.point((26, y_center+1), fill=(100, 150, 255))
            d.point((27, y_center), fill=(200, 200, 255))

    def next_frame(self):
        is_day = self.state == "above_horizon"
        self._current_y = lerp(self._current_y, self._target_sun_y(), 0.15)
        self._current_x = lerp(self._current_x, self._target_sun_x(), 0.15)
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
                if sx < 21:
                    d.point((sx, sy), fill=(brightness, brightness, min(255, brightness + 30)))

        horizon_y = 26
        d.line([(0, horizon_y), (19, horizon_y)], fill=(40, 55, 90))
        d.line([(0, horizon_y + 1), (19, horizon_y + 1)], fill=(25, 35, 60))

        if is_day and cy <= horizon_y:
            self._draw_sun(d, cx, cy)
        elif not is_day and cy <= horizon_y:
            self._draw_moon(d, cx, cy)

        if self.frame % 2 == 0:
            reflet_col = (255, 140, 50) if is_day else (100, 110, 220)
            for _ in range(4):
                ry = random.randint(horizon_y + 1, W - 1)
                rx = cx + random.randint(-5, 5)
                if 0 <= rx < 20:
                    d.point((rx, ry), fill=reflet_col)

        d = ImageDraw.Draw(img)
        self._draw_panel(d)
        self.frame += 1
        return img

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

        draw_text(d, f"{self.temp}°", 24, 4, t_col)
        
        _draw_separator(d, 16)

        if self.humidity >= 80:
            h_col = (80, 160, 255)
        elif self.humidity >= 60:
            h_col = (120, 200, 200)
        else:
            h_col = (100, 210, 130)

        draw_text(d, f"{self.humidity}%", 24, 22, h_col)

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


class DashboardAnimation:
    def __init__(self, data):
        self.frame = 0
        sun_data = data.copy()
        sun_data["state"] = data.get("sun_state", "above_horizon")
        self.sun = SunAnimation(sun_data)
        self.weather = WeatherAnimation(data)
        self.time_str = data.get("current_time", "00:00")
        self.temp = self.weather.temp
        self.feels_like = self.weather.feels_like
        self.hum = self.weather.humidity
        self.wind = self.weather.wind

    def next_frame(self):
        is_day = self.sun.state == "above_horizon"
        self.sun._current_y = lerp(self.sun._current_y, self.sun._target_sun_y(), 0.15)
        self.sun._current_x = lerp(self.sun._current_x, self.sun._target_sun_x(), 0.15)
        cy, cx = int(round(self.sun._current_y)), int(round(self.sun._current_x))
        top_col, bot_col = sky_color(self.sun.elevation if is_day else -30)

        img = Image.new("RGB", (W, W), top_col)
        d = ImageDraw.Draw(img)

        for row in range(W):
            t = row / (W - 1)
            d.line([(0, row), (W-1, row)], fill=lerp_color(top_col, bot_col, t))

        if not is_day:
            for sx, sy, phase in self.sun._stars:
                if sx < 21:
                    twinkle_val = 0.5 + 0.5 * math.sin(self.frame * 0.07 + phase * 6.28)
                    brightness = int(80 + 175 * twinkle_val)
                    d.point((sx, sy), fill=(brightness, brightness, min(255, brightness + 30)))

        horizon_y = 26
        d.line([(0, horizon_y), (19, horizon_y)], fill=(40, 55, 90))
        d.line([(0, horizon_y + 1), (19, horizon_y + 1)], fill=(25, 35, 60))

        if is_day and cy <= horizon_y:
            self.sun._draw_sun(d, cx, cy)
        elif not is_day and cy <= horizon_y:
            self.sun._draw_moon(d, cx, cy)

        self.weather.frame = self.frame
        self.weather._draw_icon(d, img)

        if self.frame % 2 == 0:
            reflet_col = (255, 140, 50) if is_day else (100, 110, 220)
            for _ in range(3):
                ry = random.randint(horizon_y + 1, W - 1)
                rx = cx + random.randint(-4, 4)
                if 0 <= rx < 20:
                    d.point((rx, ry), fill=reflet_col)

        d = ImageDraw.Draw(img)
        _draw_panel_bg(d)

        # Heure (Centrée horizontalement sur le panneau 22-31 -> milieu 26)
        h, m = self.time_str[:2], self.time_str[3:5]
        blink = (self.frame // 8) % 2 == 0
        draw_text(d, h, 22, 1, (255, 255, 255))
        if blink:
            draw_text(d, ":", 26, 1, (200, 200, 200))
        draw_text(d, m, 27, 1, (255, 255, 255))

        _draw_separator(d, 8)

        # Prochain événement solaire (Icone compacte seulement)
        is_next_set = self.sun.state == "above_horizon"
        y_ev = 11
        icon_col = (255, 120, 30) if is_next_set else (180, 200, 255)
        if is_next_set:
            d.point((26, y_ev), fill=(255, 100, 0)) 
            d.line([(24, y_ev+1), (28, y_ev+1)], fill=(255, 160, 0))
        else:
            d.point((26, y_ev+1), fill=(100, 150, 255))
            d.point((27, y_ev), fill=(200, 200, 255))

        _draw_separator(d, 16)

        # Température et Humidité (Plus petits/nets)
        if self.temp > 25: t_col = (255, 110, 50)
        elif self.temp > 15: t_col = (255, 195, 70)
        elif self.temp > 5: t_col = (150, 215, 255)
        else: t_col = (110, 175, 255)
        
        draw_text(d, f"{self.temp}°", 23, 18, t_col)

        _draw_separator(d, 24)

        if self.hum >= 80: h_col = (80, 160, 255)
        elif self.hum >= 60: h_col = (120, 200, 200)
        else: h_col = (100, 210, 130)
        
        draw_text(d, f"{self.hum}%", 23, 26, h_col)

        self.frame += 1
        self.sun.frame = self.frame
        return img