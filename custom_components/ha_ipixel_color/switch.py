"""Switch platform for iPixel."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEFAULT_NAME

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the iPixel switch platform."""
    hub = hass.data[DOMAIN][entry.entry_id]
    switches = [
        IPixelPowerSwitch(hub),
        IPixelClockDateSwitch(hub),
    ]
    async_add_entities(switches)

class IPixelPowerSwitch(SwitchEntity, RestoreEntity):
    """iPixel Power Switch."""
    
    def __init__(self, hub):
        self.hub = hub
        self._attr_name = "Alimentation"
        self._attr_unique_id = f"{hub.entry_id}_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="BKLight",
        )
        self._attr_is_on = True

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            self._attr_is_on = state.state == "on"

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

class IPixelClockDateSwitch(SwitchEntity, RestoreEntity):
    """iPixel Clock Date Switch."""
    
    def __init__(self, hub):
        self.hub = hub
        self._attr_name = "Afficher Date"
        self._attr_unique_id = f"{hub.entry_id}_show_date_clock"
        self._attr_icon = "mdi:calendar-clock"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, hub.entry_id)},
            name=hub.name,
            manufacturer="BKLight",
        )
        self._attr_is_on = hub.data.get("show_date", True)

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) is not None:
            self._attr_is_on = state.state == "on"
            self.hub.data["show_date"] = self._attr_is_on

    async def async_turn_on(self, **kwargs):
        """Show date."""
        self._attr_is_on = True
        self.hub.data["show_date"] = True
        self.async_write_ha_state()
        await self._update_clock()

    async def async_turn_off(self, **kwargs):
        """Hide date."""
        self._attr_is_on = False
        self.hub.data["show_date"] = False
        self.async_write_ha_state()
        await self._update_clock()

    async def _update_clock(self):
        """Trigger clock update with new date setting."""
        d = self.hub.data
        await self.hub.async_send_command("set_clock_mode", [
            f"style={d['clock_style']}", 
            f"show_date={self._attr_is_on}", 
            "format_24=True"
        ])
