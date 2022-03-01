import logging
import random
import requests

from datetime import datetime
from homeassistant.util import Throttle

from . import NeerslagSensorBase
from ..const import MIN_TIME_BETWEEN_UPDATES

_LOGGER = logging.getLogger(__name__)

class NeerslagSensorBuienradar(NeerslagSensorBase.NeerslagSensorBase):
    def __init__(self, hass, enabled: bool, lat: str, lon: str):
        super().__init__(hass, enabled)
        self._name = 'neerslag_buienradar_regen_data'
        self._unique_id = 'neerslag-sensor-buienradar-1'
        self._attrs = {}

        # format values, enforce 2 decimals
        self._lat = f'{float(lat):.2f}'
        self._lon = f'{float(lon):.2f}'

    @property
    def state_attributes(self):
        if not len(self._attrs):
            return
        return self._attrs

    async def config_update_listener(self, hass, config, pp=None):
        self._enabled = (config.data.get('buienradar') == True)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        if(self._enabled == False):
            _LOGGER.error('Buienradar update called, but not enabled ...')
            return

        url = 'https://gps.buienradar.nl/getrr.php?lat=' + self._lat + '&lon=' + self._lon + '&c=' + str(random.randint(0, 999999999999999))
        try:
            response = requests.get(url)
            response.raise_for_status()
        except HTTPError as http_err:
            _LOGGER.warning("HTTP Error: %s", http_err)
        except Exception as exc:
            _LOGGER.warning("Other Error: %s", exc)

        try:
            self._attrs['updated_at'] = datetime.now().strftime("%X")
            self._attrs['data'] = response.text.replace('\r\n', ' ').strip()
            self._state = random.random()
            self.update_neerslag_sensor_cache({ "source": self._name, "data": self._attrs['data'] })
        except Exception as exc:
            _LOGGER.warning("Parse Error: %s", exc)

