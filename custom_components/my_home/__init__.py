from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import discovery

from .utils.page import Page
from .const import DOMAIN

PLATFORMS = (
    Platform.SENSOR,
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    entry.async_on_unload(entry.add_update_listener(update_listener))
    # 注册静态资源
    await Page.async_register_www(Page.WWW_PATH, f"custom_components/{DOMAIN}/www")

    #await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def update_listener(hass, entry):
    pass


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    #return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True