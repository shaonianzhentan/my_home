from ..utils.page import Page
from ..const import DOMAIN, VERSION
from .http import HttpView

async def async_setup(hass, options):
    hass.http.register_view(HttpView)
    await Page.async_register_iframe("网站导航", "mdi:bookmark", DOMAIN, 
                                     f"{Page.WWW_PATH}/website/index.html?ver={VERSION}", 
                                     options.get('require_admin', False))