"""Select platform for iPixel."""
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel select platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    selects = [
        IPixelSelect(hub, "Animation", "anim_gif", [
            "Sélectionner...", "🔥 Feu", "💻 Matrix", "❄️ Neige", "🌌 Aurora",
            "🌊 Vagues", "🌈 Rainbow", "🌀 Plasma", "👾 Pac-Man", "🎶 Equalizer"
        ], "mdi:gif"),
        IPixelSelect(hub, "Police", "font", ["CUSONG", "SIMSUN", "VCR_OSD_MONO"], "mdi:format-font"),
        IPixelSelect(hub, "Animation texte", "anim_txt", [
            "0 — Statique", "1 — Défilement ←", "2 — Défilement →",
            "5 — Clignotement", "6 — Fondu", "7 — Aléatoire"
        ], "mdi:animation"),
        IPixelSelect(hub, "Style horloge", "clock_style", [str(i) for i in range(9)], "mdi:clock-outline"),
        IPixelSelect(hub, "Orientation", "orientation", [
            "0 — Normal", "1 — 90°", "2 — 180°", "3 — 270°"
        ], "mdi:screen-rotation"),
        IPixelSelect(hub, "Redimensionnement image", "resize", ["crop", "fit"], "mdi:resize"),
    ]
    async_add_entities(selects)

class IPixelSelect(SelectEntity):
    """iPixel Dropdown Select."""
    
    def __init__(self, hub, name, key, options, icon):
        self.hub = hub
        self._key = key
        self._attr_name = name
        self._attr_options = options
        self._attr_current_option = hub.data.get(key, options[0])
        self._attr_unique_id = f"{hub.mac_address}_{key}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.mac_address)},
            name=DEFAULT_NAME,
            manufacturer="iPixel",
        )

    async def async_select_option(self, option: str) -> None:
        """Update the value."""
        self.hub.data[self._key] = option
        self._attr_current_option = option
        self.async_write_ha_state()

        # Appliquer instantanément l'orientation
        if self._key == "orientation":
            orient = option.split(' ')[0]
            await self.hub.async_send_command("set_orientation", [f"orientation={orient}"])
