"""Constants for the iPixel integration."""
from logging import getLogger
from homeassistant.const import Platform

LOGGER = getLogger(__package__)

DOMAIN = "ha_ipixel_color"
CONF_WS_URL = "ws_url"
DEFAULT_NAME = "HA iPixel Color"

PLATFORMS = [
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.TEXT,
    Platform.NUMBER,
    Platform.SELECT,
]
