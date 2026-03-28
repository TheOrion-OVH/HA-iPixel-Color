"""Constants for the iPixel integration."""
from logging import getLogger
from homeassistant.const import Platform

LOGGER = getLogger(__package__)

DOMAIN = "ha_ipixel_color"
CONF_MAC_ADDRESS = "mac_address"
DEFAULT_NAME = "HA iPixel Color"

PLATFORMS = [
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.TEXT,
    Platform.NUMBER,
    Platform.SELECT,
]
