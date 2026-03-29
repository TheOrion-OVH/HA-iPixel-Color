"""Text platform for iPixel."""
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel text platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    texts = [
        IPixelText(hub, "Message", "message", 255, "mdi:text"),
        IPixelText(hub, "Couleur texte (hex)", "color", 6, "mdi:palette"),
        IPixelText(hub, "Couleur fond (hex)", "bg_color", 6, "mdi:palette-outline"),
        IPixelText(hub, "Chemin image", "image_url", 255, "mdi:image"),
        IPixelText(hub, "Couleur pixel (hex)", "pixel_color", 6, "mdi:square"),
    ]
    async_add_entities(texts)

class IPixelText(TextEntity):
    """iPixel Text Input."""
    
    def __init__(self, hub, name, key, max_length, icon):
        self.hub = hub
        self._key = key
        self._attr_name = name
        self._attr_native_value = hub.data[key]
        self._attr_native_max = max_length
        self._attr_unique_id = f"{hub.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="iPixel",
        )

    async def async_set_value(self, value: str) -> None:
        """Update the value."""
        self.hub.data[self._key] = value
        self._attr_native_value = value
        self.async_write_ha_state()
