"""The Neerslag Sensor (Buienalarm / Buienradar) integration."""
import logging
import os
import time

from homeassistant.components.frontend import add_extra_js_url
from .const import DOMAIN, FRONTEND_SCRIPT_URL

PLATFORMS = [ 'sensor' ]
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config_entry):
    hass.data.setdefault(DOMAIN, {})

    # Load frontend card
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_to_file = "{}/home-assistant-neerslag-card/neerslag-card.js".format(dir_path)
    hass.http.register_static_path(FRONTEND_SCRIPT_URL, str(path_to_file), False)
    frontend_script_url_with_parameter = FRONTEND_SCRIPT_URL + "?cache=" + str(time.time())
    add_extra_js_url(hass, frontend_script_url_with_parameter , es5=False)
    return True

async def async_setup_entry(hass, config):
    for platform in PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(config, platform))
    return True
