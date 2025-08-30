from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import discovery

from .utils.page import Page
from .const import DOMAIN, SWITCH_WEBSITE, PATH_WEBSITE
from .manifest import manifest

from .website.http import HttpView as HttpViewWebsite

VERSION = manifest.version

PLATFORMS = (
    Platform.SENSOR,
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    entry.async_on_unload(entry.add_update_listener(update_listener))
    # 注册静态资源
    await Page.async_register_www(Page.WWW_PATH, f"custom_components/{DOMAIN}/www")

    options = entry.options
    if options.get(SWITCH_WEBSITE, False):
      hass.http.register_view(HttpViewWebsite)
      await Page.async_register_iframe("网址导航", "mdi:search-web", PATH_WEBSITE, f"{Page.WWW_PATH}/website/index.html?ver={VERSION}", False)

    #await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def update_listener(hass, entry):
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    #return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await Page.async_remove_iframe(PATH_WEBSITE)
    return True