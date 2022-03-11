import logging
import random
from datetime import datetime
import requests

from homeassistant.util import Throttle

from . import NeerslagSensorBase
from ..const import MIN_TIME_BETWEEN_UPDATES

_LOGGER = logging.getLogger(__name__)

class NeerslagSensorBuienalarm(NeerslagSensorBase.NeerslagSensorBase):
    def __init__(self, hass, enabled: bool, lat: str, lon: str):
        super().__init__(hass, enabled)
        self._name = 'neerslag_buienalarm_regen_data'
        self._unique_id = 'neerslag-sensor-buienalarm-1'
        self._attrs = {}

        # format values, enforce 3 decimals
        self._lat = f'{float(lat):.3f}'
        self._lon = f'{float(lon):.3f}'

    @property
    def state_attributes(self):
        return self._attrs

    async def config_update_listener(self, hass, config, pp=None):
        # pylint:disable=unused-argument,invalid-name
        self._enabled = (config.data.get('buienalarm') is True)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        if(self._enabled is False):
            _LOGGER.error('Buienalarm update called, but not enabled ...')
            return

        url = 'https://cdn-secure.buienalarm.nl/api/3.4/forecast.php?lat=' + self._lat + '&lon=' + self._lon + '&region=nl&unit=mm%2Fu&c=' + str(random.randint(0, 999999999999999))
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            _LOGGER.error("HTTP Error: %s", http_err)
        except Exception as exc: # pylint: disable=broad-except
            _LOGGER.error("Other Error: %s", exc)

        try:
            self._attrs['updated_at'] = datetime.now().strftime("%X")
            self._attrs['data'] = response.json()
            self._state = random.random()
            self.update_neerslag_sensor_cache({ "source": self._name, "data": self._attrs['data'] })
        except Exception as exc: # pylint: disable=broad-except
            _LOGGER.error("Parse Error: %s", exc)
