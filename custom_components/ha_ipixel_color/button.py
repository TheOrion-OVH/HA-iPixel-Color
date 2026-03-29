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
        IPixelButton(hub, "Envoyer Image", "send_image", "mdi:image"),
        IPixelButton(hub, "Appliquer luminosité", "set_brightness", "mdi:brightness-5"),
        IPixelButton(hub, "Appliquer vitesse", "set_speed", "mdi:speedometer"),
        IPixelButton(hub, "Mode Horloge", "set_clock_mode", "mdi:clock-outline"),
        IPixelButton(hub, "Appliquer Orientation", "set_orientation", "mdi:screen-rotation"),
        IPixelButton(hub, "Dessiner Pixel", "set_pixel", "mdi:square-edit-outline"),
        IPixelButton(hub, "Démarrer l'animation", "play_anim", "mdi:play-circle"),
        IPixelButton(hub, "Effacer écran", "clear", "mdi:monitor-off"),
        IPixelButton(hub, "Mode Soleil", "show_sun", "mdi:white-balance-sunny"),
        IPixelButton(hub, "Mode Météo", "show_weather", "mdi:weather-partly-cloudy"),
        IPixelButton(hub, "Redémarrer", "reboot", "mdi:restart"),
    ]
    async_add_entities(buttons)

class IPixelButton(ButtonEntity):
    """iPixel Action Button."""
    
    def __init__(self, hub, name, action, icon):
        self.hub = hub
        self._action = action
        self._attr_name = name
        self._attr_unique_id = f"{hub.entry_id}_{action}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="BKLight",
        )

    async def async_press(self) -> None:
        """Handle the button press using internal hub state."""
        d = self.hub.data
        if self._action == "send_text":
            anim = d["anim_txt"].split(' ')[0]
            params = [
                f"text={d['message']}", f"color={d['color']}", f"bg_color={d['bg_color']}",
                f"font={d['font']}", f"animation={anim}", f"speed={int(d['speed'])}"
            ]
            
            rainbow = int(d.get('rainbow_mode', 0))
            if rainbow > 0:
                params.append(f"rainbow_mode={rainbow}")
                
            await self.hub.async_send_command("send_text", params)
        elif self._action == "send_image":
            await self.hub.async_send_command("send_image", [f"path={d['image_url']}", f"resize_method={d['resize']}"])
        elif self._action == "set_brightness":
            await self.hub.async_send_command("set_brightness", [f"brightness={int(d['brightness'])}"])
        elif self._action == "set_speed":
            await self.hub.async_send_command("set_speed", [f"speed={int(d['speed'])}"])
        elif self._action == "clear":
            await self.hub.async_send_command("clear")
        elif self._action == "show_sun":
            sun = self.hub.hass.states.get("sun.sun")
            if sun:
                state = sun.state
                elev = sun.attributes.get("elevation", 0)
                azimuth = sun.attributes.get("azimuth", 180)
                next_rising = sun.attributes.get("next_rising", "")
                next_setting = sun.attributes.get("next_setting", "")
            else:
                state, elev, azimuth, next_rising, next_setting = "unknown", 0, 180, "", ""
            
            import json
            json_data = json.dumps({
                "state": state, 
                "elevation": elev, 
                "azimuth": azimuth,
                "next_rising": next_rising,
                "next_setting": next_setting
            })
            await self.hub.async_send_command("send_image", [f"path=animation:sun_mode:{json_data}", "resize_method=fit"])
        elif self._action == "show_weather":
            w_states = self.hub.hass.states.async_all("weather")
            if w_states:
                w = w_states[0]
                state = w.state
                temp = w.attributes.get("temperature", 0)
                hum = w.attributes.get("humidity", 0)
            else:
                state, temp, hum = "unknown", 0, 0
                
            import json
            json_data = json.dumps({"state": state, "temp": temp, "humidity": hum})
            await self.hub.async_send_command("send_image", [f"path=animation:weather_mode:{json_data}", "resize_method=fit"])
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
