"""Number platform for iPixel."""
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel number platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    numbers = [
        IPixelNumber(hub, "Luminosité", "brightness", 0, 100, "mdi:brightness-6"),
        IPixelNumber(hub, "Vitesse animation", "speed", 1, 100, "mdi:speedometer"),
        IPixelNumber(hub, "Pixel X", "pixel_x", 0, 31, "mdi:arrow-right"),
        IPixelNumber(hub, "Pixel Y", "pixel_y", 0, 31, "mdi:arrow-down"),
    ]
    async_add_entities(numbers)

class IPixelNumber(NumberEntity):
    """iPixel Number Input."""
    
    def __init__(self, hub, name, key, min_val, max_val, icon):
        self.hub = hub
        self._key = key
        self._attr_name = name
        self._attr_native_value = hub.data[key]
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = 1
        self._attr_unique_id = f"{hub.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="iPixel",
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the value."""
        v = int(value)
        self.hub.data[self._key] = v
        self._attr_native_value = v
        self.async_write_ha_state()

        # Appliquer instantanément la luminosité
        if self._key == "brightness":
            await self.hub.async_send_command("set_brightness", [f"level={v}"])
