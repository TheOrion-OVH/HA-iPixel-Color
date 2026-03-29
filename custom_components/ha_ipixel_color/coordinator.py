"""Coordinator / Hub for iPixel."""
import asyncio
import json
import logging
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

from .pixel_art import (
    SunAnimation, WeatherAnimation, ConfettiAnimation, FireworkAnimation,
    SnakeAnimation, TetrisAnimation, DinoAnimation, PenguinAnimation, RPSAnimation,
    FireAnimation, MatrixAnimation, SnowAnimation, AuroraAnimation,
    WavesAnimation, RainbowAnimation, PlasmaAnimation, EqualizerAnimation, PacmanAnimation
)

ANIMATION_CLASSES = {
    "fire": FireAnimation, "matrix": MatrixAnimation, "snow": SnowAnimation,
    "aurora": AuroraAnimation, "waves": WavesAnimation, "rainbow": RainbowAnimation,
    "plasma": PlasmaAnimation, "equalizer": EqualizerAnimation, "pacman": PacmanAnimation,
    "confetti": ConfettiAnimation, "firework": FireworkAnimation, "snake": SnakeAnimation,
    "tetris": TetrisAnimation, "dino": DinoAnimation, "penguin": PenguinAnimation,
}

class IPixelHub:
    """Hub for connecting and sending commands to the iPixel Proxy."""

    def __init__(self, hass: HomeAssistant, ws_uri: str) -> None:
        """Initialize."""
        self.hass = hass
        self.ws_uri = ws_uri
        self.entry_id = None
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
            "brightness": 50,
            "clock_style": "1",
            "orientation": "0 — Normal",
            "pixel_x": 0,
            "pixel_y": 0,
            "pixel_color": "FF0000",
            "anim_gif": "🔥 Feu",
            "rainbow_mode": 0
        }

    async def generate_python_animation_hex(self, anim_name: str, num_frames=30) -> str:
        """Generation of GIF inside an executor."""
        def _generate():
            if not HAS_PIL:
                raise RuntimeError("Pillow is required for animations.")
                
            frames = num_frames
            if anim_name.startswith("sun_mode:"):
                data = json.loads(anim_name.split(":", 1)[1])
                anim_obj = SunAnimation(data)
            elif anim_name.startswith("weather_mode:"):
                data = json.loads(anim_name.split(":", 1)[1])
                anim_obj = WeatherAnimation(data)
            elif anim_name.startswith("rps:"):
                data = json.loads(anim_name.split(":", 1)[1])
                anim_obj = RPSAnimation(data)
                frames = 30
            else:
                cls = ANIMATION_CLASSES.get(anim_name)
                if not cls:
                    raise ValueError(f"Unknown animation {anim_name}")
                anim_obj = cls()
                
            all_frames = []
            for _ in range(frames):
                all_frames.append(anim_obj.next_frame())
            buf = io.BytesIO()
            all_frames[0].save(buf, format="GIF", save_all=True, append_images=all_frames[1:], duration=100, loop=0)
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
