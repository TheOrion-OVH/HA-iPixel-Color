"""Switch platform for iPixel."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel switch platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IPixelPowerSwitch(hub)])

class IPixelPowerSwitch(SwitchEntity):
    """iPixel Power Switch."""
    
    def __init__(self, hub):
        self.hub = hub
        self._attr_name = "Alimentation"
        self._attr_unique_id = f"{hub.entry_id}_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="iPixel",
        )
        self._attr_is_on = True

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hub.async_send_command("set_power", ["on=True"])
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hub.async_send_command("set_power", ["on=False"])
        self._attr_is_on = False
        self.async_write_ha_state()
