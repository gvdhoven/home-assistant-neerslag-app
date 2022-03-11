# pylint: disable=superfluous-parens
import logging

from .sensors import NeerslagSensorBuienalarm
from .sensors import NeerslagSensorBuienradar
from .sensors import NeerslagSensorStatus

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entity."""

    # Setup buienalarm
    buienalarm_enabled = (config_entry.data.get('buienalarm') is True)
    buienalarm_lat = hass.config.latitude
    buienalarm_lon = hass.config.longitude
    if (config_entry.data.get('NeerslagSensorUseHAforLocation') is False):
        buienalarm_lat = config_entry.data.get('buienalarmLatitude')
        buienalarm_lon = config_entry.data.get('buienalarmLongitude')

    buienalarm = NeerslagSensorBuienalarm.NeerslagSensorBuienalarm(hass, buienalarm_enabled, buienalarm_lat, buienalarm_lon)
    config_entry.add_update_listener(buienalarm.config_update_listener)

    # Setup buienradar
    buienradar_enabled = (config_entry.data.get('buienradar') is True)
    buienradar_lat = hass.config.latitude
    buienradar_lon = hass.config.longitude
    if (config_entry.data.get('NeerslagSensorUseHAforLocation') is False):
        buienradar_lat = config_entry.data.get('buienradarLatitude')
        buienradar_lon = config_entry.data.get('buienradarLongitude')

    buienradar = NeerslagSensorBuienradar.NeerslagSensorBuienradar(hass, buienradar_enabled, buienradar_lat, buienradar_lon)
    config_entry.add_update_listener(buienradar.config_update_listener)

    # Setup generic sensors
    neerslag_rain_now = NeerslagSensorStatus.NeerslagSensorStatus('neerslag_rain_now', 'neerslag-sensor-rain-now-1', (buienalarm_enabled or buienradar_enabled))
    config_entry.add_update_listener(neerslag_rain_now.config_update_listener)

    neerslag_rain_prediction = NeerslagSensorStatus.NeerslagSensorStatus('neerslag_rain_prediction', 'neerslag-sensor-rain-prediction-1', (buienalarm_enabled or buienradar_enabled))
    config_entry.add_update_listener(neerslag_rain_prediction.config_update_listener)

    # Add sensors to HA
    async_add_entities([ buienalarm, buienradar, neerslag_rain_now, neerslag_rain_prediction ])
