"""The iPixel integration."""
import logging
import asyncio
import subprocess
import sys
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, CONF_MAC_ADDRESS, CONF_WS_URL
from .coordinator import IPixelHub

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iPixel from a config entry."""
    mac_address = entry.data.get(CONF_MAC_ADDRESS)
    ws_url = entry.data.get(CONF_WS_URL)
    
    hass.data.setdefault(DOMAIN, {})

    if ws_url:
        _LOGGER.info("Connecting to remote iPixel WebSocket Server at %s", ws_url)
        ws_uri = ws_url
    else:
        port = 5042
        ws_uri = f"ws://127.0.0.1:{port}"
        
        cmd = [
            sys.executable, "-m", "pypixelcolor.websocket",
            "-a", mac_address,
            "--host", "127.0.0.1",
            "--port", str(port)
        ]
        
        _LOGGER.info("Starting iPixel WebSocket Server: %s", " ".join(cmd))
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        async def _log_output():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                _LOGGER.error("iPixel Server: %s", line.decode().rstrip())
                
        hass.loop.create_task(_log_output())
        
        # Let the websocket server start
        await asyncio.sleep(2)
        hass.data[DOMAIN][f"{entry.entry_id}_process"] = process
    
    hub = IPixelHub(hass, ws_uri)
    hub.mac_address = mac_address

    hass.data[DOMAIN][entry.entry_id] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Exposer directement l'API en tant que services
    await async_setup_services(hass, hub)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    process_key = f"{entry.entry_id}_process"
    if process_key in hass.data[DOMAIN]:
        process = hass.data[DOMAIN][process_key]
        _LOGGER.info("Stopping iPixel WebSocket Server")
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
        except Exception as e:
            _LOGGER.warning("Error stopping iPixel server: %s", e)
            
        hass.data[DOMAIN].pop(process_key)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_setup_services(hass: HomeAssistant, hub: IPixelHub):
    """Register custom iPixel services."""
    async def handle_send_image(call):
        path = call.data.get("path")
        resize = call.data.get("resize_method", "crop")
        params = [f"path={path}", f"resize_method={resize}"]
        await hub.async_send_command("send_image", params)

    async def handle_send_text(call):
        text = call.data.get("message", "")
        color = call.data.get("color", "ffffff")
        bg_color = call.data.get("bg_color", "")
        params = [f"text={text}", f"color={color}", f"bg_color={bg_color}"]
        if font := call.data.get("font"): params.append(f"font={font}")
        if speed := call.data.get("speed"): params.append(f"speed={speed}")
        if rainbow := call.data.get("rainbow_mode"): params.append(f"rainbow_mode={rainbow}")
        await hub.async_send_command("send_text", params)

    async def handle_set_power(call):
        on_state = call.data.get("on_state", True)
        await hub.async_send_command("set_power", [f"on={on_state}"])

    async def handle_set_brightness(call):
        level = call.data.get("level", 80)
        await hub.async_send_command("set_brightness", [f"level={level}"])

    async def handle_set_clock_mode(call):
        style = call.data.get("style", 1)
        await hub.async_send_command("set_clock_mode", [f"style={style}", "show_date=True", "format_24=True"])

    async def handle_set_orientation(call):
        orientation = call.data.get("orientation", 0)
        await hub.async_send_command("set_orientation", [f"orientation={orientation}"])

    async def handle_set_pixel(call):
        x = call.data.get("x", 0)
        y = call.data.get("y", 0)
        color = call.data.get("color", "FF0000")
        await hub.async_send_command("set_pixel", [f"x={x}", f"y={y}", f"color={color}"])

    async def handle_clear(call):
        await hub.async_send_command("clear", [])

    hass.services.async_register(DOMAIN, "send_image", handle_send_image)
    hass.services.async_register(DOMAIN, "send_text", handle_send_text)
    hass.services.async_register(DOMAIN, "set_power", handle_set_power)
    hass.services.async_register(DOMAIN, "set_brightness", handle_set_brightness)
    hass.services.async_register(DOMAIN, "set_clock_mode", handle_set_clock_mode)
    hass.services.async_register(DOMAIN, "set_orientation", handle_set_orientation)
    hass.services.async_register(DOMAIN, "set_pixel", handle_set_pixel)
    hass.services.async_register(DOMAIN, "clear", handle_clear)
