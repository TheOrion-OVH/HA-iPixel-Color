"""Coordinator / Hub for iPixel."""
import asyncio
import json
import logging
import math
import random
import colorsys
import io
import os
import aiohttp
import websockets

from homeassistant.core import HomeAssistant

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

_LOGGER = logging.getLogger(__name__)

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
        self.cols = [{"head":  random.randint(0, W), "speed": random.uniform(0.4, 1.2), "len": random.randint(4, 14)} for _ in range(W)]
        self.buf = [[(0, 0, 0)] * W for _ in range(W)]
    def next_frame(self) -> 'Image.Image':
        self.buf = [[(int(r * 0.7), int(g * 0.75), int(b * 0.7)) for r, g, b in row] for row in self.buf]
        for x, col in enumerate(self.cols):
            col["head"] = (col["head"] + col["speed"]) % (W + col["len"])
            head_y = int(col["head"]) - col["len"]
            for i in range(col["len"]):
                y = head_y + i
                if 0 <= y < W:
                    intensity = (i + 1) / col["len"]
                    if i == col["len"] - 1:
                        self.buf[y][x] = (200, 255, 200)
                    else:
                        gv = int(40 + 215 * intensity)
                        self.buf[y][x] = (0, gv, int(gv * 0.3))
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

ANIMATION_CLASSES = {
    "fire": FireAnimation, "matrix": MatrixAnimation, "snow": SnowAnimation,
    "aurora": AuroraAnimation, "waves": WavesAnimation, "rainbow": RainbowAnimation,
    "plasma": PlasmaAnimation, "equalizer": EqualizerAnimation, "pacman": PacmanAnimation,
}

class IPixelHub:
    """Hub for connecting and sending commands to the iPixel Proxy."""

    def __init__(self, hass: HomeAssistant, ws_uri: str) -> None:
        """Initialize."""
        self.hass = hass
        self.ws_uri = ws_uri
        self.mac_address = None
        self.name = None
        self.data = {
            "message": "Hello",
            "color": "ffffff",
            "bg_color": "",
            "font": "CUSONG",
            "anim_txt": "0 — Statique",
            "speed": 80,
            "image_url": "",
            "resize": "crop",
            "brightness": 80,
            "clock_style": "1",
            "orientation": "0 — Normal",
            "pixel_x": 0,
            "pixel_y": 0,
            "pixel_color": "FF0000",
            "anim_gif": "🔥 Feu"
        }

    async def generate_python_animation_hex(self, anim_name: str, num_frames=30) -> str:
        """Generation of GIF inside an executor."""
        def _generate():
            if not HAS_PIL:
                raise RuntimeError("Pillow is required for animations.")
            cls = ANIMATION_CLASSES.get(anim_name)
            if not cls:
                raise ValueError(f"Unknown animation {anim_name}")
            anim_obj = cls()
            frames = [anim_obj.next_frame() for _ in range(num_frames)]
            buf = io.BytesIO()
            frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], duration=100, loop=0)
            return buf.getvalue().hex()
            
        return await self.hass.async_add_executor_job(_generate)

    async def async_send_command(self, command: str, params: list[str] = None):
        """Build and send payload."""
        if params is None:
            params = []

        if command == "send_image":
            path = None
            resize_method = "crop"
            
            for p in params:
                if p.startswith("path="): path = p.split("=", 1)[1].strip()
                elif p.startswith("resize_method="): resize_method = p.split("=", 1)[1].strip()
                    
            if path:
                try:
                    if path.startswith("animation:"):
                        anim_name = path.split(":", 1)[1]
                        _LOGGER.info("Generating animation %s", anim_name)
                        hex_string = await self.generate_python_animation_hex(anim_name, num_frames=40)
                        ext = ".gif"
                    elif path.startswith("http://") or path.startswith("https://"):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(path, timeout=10) as response:
                                data = await response.read()
                                hex_string = data.hex()
                        ext = os.path.splitext(path)[1].lower().split("?")[0]
                        if not ext: ext = ".gif"
                    else:
                        def _read_file():
                            if not os.path.isfile(path): raise FileNotFoundError(f"File {path} not found")
                            with open(path, "rb") as f: return f.read().hex()
                        hex_string = await self.hass.async_add_executor_job(_read_file)
                        ext = os.path.splitext(path)[1].lower()

                    command = "send_image_hex"
                    params = [f"hex_string={hex_string}", f"file_extension={ext}", f"resize_method={resize_method}"]
                except Exception as e:
                    _LOGGER.error("Error processing image %s: %s", path, e)
                    return False

        payload = json.dumps({
            "command": command,
            "params": [p for p in params if "=" not in p or p.split("=", 1)[1].strip()]
        })

        try:
            async with websockets.connect(self.ws_uri, max_size=None, close_timeout=5) as ws:
                await ws.send(payload)
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    _LOGGER.debug("[%s] Response: %s", command, response)
                except asyncio.TimeoutError:
                    _LOGGER.debug("[%s] Sent OK", command)
            return True
        except Exception as err:
            _LOGGER.error("WebSocket Error sending %s: %s", command, err)
            return False
