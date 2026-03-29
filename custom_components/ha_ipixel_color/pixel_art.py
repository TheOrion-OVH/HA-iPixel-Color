import math
import random
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

W = 32

def draw_text(d, text, x, y, color):
    """Draws a 3x5 mini font."""
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
    }
    cx = x
    for ch in text:
        pts = MINI_FONT.get(ch, [])
        for dx, dy in pts:
            d.point((cx + dx, y + dy), fill=color)
        cx += 4

class SunAnimation:
    def __init__(self):
        self.frame = 0
        
    def next_frame(self) -> 'Image.Image':
        img = Image.new("RGB", (W, W), (10, 20, 40))
        d = ImageDraw.Draw(img)
        
        # Glow
        pulse = math.sin(self.frame * 0.15) * 3
        cx, cy = 16, 16
        for r in range(16, 8, -1):
            alpha = (16 - r) * 5
            d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(255, 180, 0)) # Basic alpha simulation
            
        # Rays
        for i in range(12):
            angle = math.radians(i * 30 + self.frame * 2)
            r1, r2 = 9, 15 + pulse
            p1 = (cx + math.cos(angle)*r1, cy + math.sin(angle)*r1)
            p2 = (cx + math.cos(angle)*r2, cy + math.sin(angle)*r2)
            d.line([p1, p2], fill=(255, 140, 0), width=1)
            
        # Core
        inner_pulse = math.sin(self.frame * 0.3) * 1
        d.ellipse([cx - 8 - inner_pulse, cy - 8 - inner_pulse, cx + 8 + inner_pulse, cy + 8 + inner_pulse], fill=(255, 220, 0))
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 200))
        
        self.frame += 1
        return img

class WeatherAnimation:
    def __init__(self, data):
        self.frame = 0
        self.state = data.get("state", "cloudy")
        self.temp = int(round(float(data.get("temp", 0))))
        self.humidity = int(round(float(data.get("humidity", 0))))
        # Procedural weather details
        self.particles = [{"x": random.randint(1, 20), "y": random.randint(2, 22), "v": random.uniform(1.5, 3.0)} for _ in range(8)]

    def draw_bg(self, d):
        # Sky gradient
        for y in range(W):
            r = int(20 + y * 1.5)
            g = int(30 + y * 2)
            b = int(70 + y * 1.5)
            d.line([(0, y), (W-1, y)], fill=(r, g, b))

    def draw_icon(self, d):
        s = self.state
        cx, cy = 11, 12
        if s in ("sunny", "clear-night"):
            c1 = (255, 220, 0) if s == "sunny" else (220, 220, 255)
            c2 = (255, 255, 200) if s == "sunny" else (255, 255, 255)
            pulse = math.sin(self.frame*0.2) * 1.5
            d.ellipse([cx-6-pulse, cy-6-pulse, cx+6+pulse, cy+6+pulse], fill=(c1[0]//2, c1[1]//2, c1[2]//2))
            d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=c1)
            d.ellipse([cx-2, cy-3, cx+2, cy+1], fill=c2)
        elif s == "partlycloudy":
            d.ellipse([cx-3, cy-5, cx+7, cy+5], fill=(255, 200, 0)) # Sun behind
            self._draw_cloud(d, cx, cy+2, (200, 200, 200), (150, 150, 150))
        elif s in ("rainy", "pouring", "drizzle"):
            self._draw_cloud(d, cx, cy, (120, 140, 180), (80, 90, 120))
            for p in self.particles:
                p["y"] += p["v"]
                if p["y"] > 24: p["y"] = 12; p["x"] = random.randint(3, 18)
                d.line([(p["x"], int(p["y"])), (p["x"], int(p["y"]+2))], fill=(100, 180, 255))
        elif s in ("snowy", "snowy-rainy"):
            self._draw_cloud(d, cx, cy, (220, 220, 220), (180, 180, 180))
            for p in self.particles:
                p["y"] += p["v"] * 0.4
                p["x"] += math.sin(self.frame * 0.1 + p["x"]) * 0.5
                if p["y"] > 24: p["y"] = 12; p["x"] = random.randint(3, 18)
                d.point((int(p["x"]), int(p["y"])), fill=(255, 255, 255))
        elif s in ("lightning", "lightning-rainy", "thunder"):
            self._draw_cloud(d, cx, cy, (80, 80, 110), (50, 50, 80))
            if self.frame % 15 < 3:
                d.line([(cx, cy+4), (cx-3, cy+10), (cx+1, cy+9), (cx-1, cy+15)], fill=(255, 255, 100), width=1)
        else: # cloudy, fog
            self._draw_cloud(d, cx, cy, (180, 180, 180), (140, 140, 140))
            self._draw_cloud(d, cx+5, cy-3, (200, 200, 200), (160, 160, 160))

    def _draw_cloud(self, d, cx, cy, fill, shadow):
        d.ellipse([cx-7, cy-3, cx+7, cy+5], fill=shadow)
        d.ellipse([cx-4, cy-6, cx+2, cy+2], fill=shadow)
        d.ellipse([cx-7, cy-4, cx+7, cy+4], fill=fill)
        d.ellipse([cx-4, cy-7, cx+2, cy+1], fill=fill)

    def next_frame(self) -> 'Image.Image':
        img = Image.new("RGB", (W, W), (0, 0, 0))
        d = ImageDraw.Draw(img)
        
        self.draw_bg(d)
        self.draw_icon(d)
        
        # Right info panel (frosted glass effect simulation)
        for x in range(22, 32):
            for y in range(0, 32):
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (r//2+20, g//2+25, b//2+40))
        
        # Divider
        d.line([(21, 0), (21, 31)], fill=(100, 120, 160))
        
        # Temp
        t_str = f"{self.temp}°"
        ty = 4 if len(t_str) < 3 else 2
        draw_text(d, t_str, 23, ty, (255, 160, 80) if self.temp > 15 else (140, 220, 255))
        
        # Humidity
        h_str = f"{self.humidity}%"
        draw_text(d, h_str, 23, 22, (100, 200, 100) if self.humidity < 60 else (100, 180, 255))
        
        self.frame += 1
        return img
