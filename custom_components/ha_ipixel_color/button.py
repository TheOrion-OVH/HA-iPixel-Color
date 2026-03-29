"""Button platform for iPixel."""
import asyncio
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel button platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    buttons = [
        IPixelButton(hub, "Envoyer Message", "send_text", "mdi:send"),
        IPixelButton(hub, "Envoyer Image", "send_image", "mdi:image-outline"),
        IPixelButton(hub, "Appliquer Luminosité", "set_brightness", "mdi:brightness-6"),
        IPixelButton(hub, "Mode Horloge", "set_clock_mode", "mdi:clock-outline"),
        IPixelButton(hub, "Appliquer Orientation", "set_orientation", "mdi:screen-rotation"),
        IPixelButton(hub, "Dessiner Pixel", "set_pixel", "mdi:square-edit-outline"),
        IPixelButton(hub, "Démarrer l'animation", "play_anim", "mdi:play-circle"),
        IPixelButton(hub, "Effacer Mémoire", "clear", "mdi:eraser"),
        IPixelButton(hub, "Effacer Écran", "reboot", "mdi:monitor-off"),
    ]
    async_add_entities(buttons)

class IPixelButton(ButtonEntity):
    """iPixel Action Button."""
    
    def __init__(self, hub, name, action, icon):
        self.hub = hub
        self._action = action
        self._attr_name = name
        self._attr_unique_id = f"{hub.mac_address}_{action}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.mac_address)},
            name=hub.name,
            manufacturer="iPixel",
        )

    async def async_press(self) -> None:
        """Handle the button press using internal hub state."""
        d = self.hub.data
        if self._action == "send_text":
            anim = d["anim_txt"].split(' ')[0]
            await self.hub.async_send_command("send_text", [
                f"text={d['message']}", f"color={d['color']}", f"bg_color={d['bg_color']}",
                f"font={d['font']}", f"animation={anim}", f"speed={int(d['speed'])}"
            ])
        elif self._action == "send_image":
            await self.hub.async_send_command("send_image", [f"path={d['image_url']}", f"resize_method={d['resize']}"])
        elif self._action == "set_brightness":
            await self.hub.async_send_command("set_brightness", [f"level={int(d['brightness'])}"])
        elif self._action == "set_clock_mode":
            await self.hub.async_send_command("set_clock_mode", [f"style={d['clock_style']}", "show_date=True", "format_24=True"])
        elif self._action == "set_orientation":
            orient = d["orientation"].split(' ')[0]
            await self.hub.async_send_command("set_orientation", [f"orientation={orient}"])
        elif self._action == "set_pixel":
            await self.hub.async_send_command("set_pixel", [f"x={int(d['pixel_x'])}", f"y={int(d['pixel_y'])}", f"color={d['pixel_color']}"])
        elif self._action == "play_anim":
            mapping = {
                '🔥 Feu': 'animation:fire', '💻 Matrix': 'animation:matrix', '❄️ Neige': 'animation:snow',
                '🌌 Aurora': 'animation:aurora', '🌊 Vagues': 'animation:waves', '🌈 Rainbow': 'animation:rainbow',
                '🌀 Plasma': 'animation:plasma', '👾 Pac-Man': 'animation:pacman', '🎶 Equalizer': 'animation:equalizer'
            }
            path = mapping.get(d["anim_gif"], "animation:fire")
            await self.hub.async_send_command("send_image", [f"path={path}", "resize_method=crop"])
        elif self._action == "clear":
            await self.hub.async_send_command("clear", [])
        elif self._action == "reboot":
            await self.hub.async_send_command("set_power", ["on=False"])
            await asyncio.sleep(1)
            await self.hub.async_send_command("set_power", ["on=True"])
