from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.data_entry_flow import FlowResult

import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from .const import DOMAIN, SWITCH_WECOM, SWITCH_WEBSITE, SWITCH_WECHAT, SWITCH_QQMAIL, SWITCH_PASSWORD

CONF_SWITCH = 'switch'

class MyHomeConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None, errors={}) -> FlowResult:

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title=DOMAIN, data={})

        DATA_SCHEMA = vol.Schema({})
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        return OptionsFlowHandler(entry)


class OptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    def async_update_entry(self, data):
        return self.async_create_entry(title='', data={ **self.config_entry.options, **data })

    async def async_step_init(self, user_input=None, errors={}):
        CONF_TYPE = 'item'
        if user_input is not None:
            item = user_input.get(CONF_TYPE)

            if item == 'website':
                return await self.async_step_website()
            elif item == 'password':
                return await self.async_step_password()

        return self.async_show_form(step_id="init", data_schema=vol.Schema({
                vol.Required(CONF_TYPE): vol.In({
                    "website": "网站导航",
                    "password": "密码管理",
                    "wecom": "企业微信",
                    "wechat": "微信小程序",
                    "qqmail": "QQ邮箱"
                }),
            }), errors=errors)

    async def async_step_website(self, user_input=None, errors={}):

        if user_input is not None:
            return self.async_update_entry({
                SWITCH_WEBSITE: user_input.get(CONF_SWITCH)
            })
    
        return self.async_show_form(step_id="website", data_schema=vol.Schema({
            vol.Required(CONF_SWITCH, default=self.config_entry.options.get(SWITCH_WEBSITE, False)): bool,
        }), errors=errors)

    async def async_step_password(self, user_input=None, errors={}):

        if user_input is not None:
            return self.async_update_entry({
                SWITCH_PASSWORD: user_input.get(CONF_SWITCH)
            })
    
        return self.async_show_form(step_id="password", data_schema=vol.Schema({
            vol.Required(CONF_SWITCH): bool,
        }), errors=errors)