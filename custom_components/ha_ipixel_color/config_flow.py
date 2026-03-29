"""Config flow for iPixel integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME

from .const import DOMAIN, CONF_WS_URL, DEFAULT_NAME

class IPixelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iPixel."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_WS_URL])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(title=user_input.get(CONF_NAME, DEFAULT_NAME), data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_WS_URL): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
