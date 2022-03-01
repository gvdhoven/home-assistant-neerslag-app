import logging

from .sensors import NeerslagSensorBuienalarm
from .sensors import NeerslagSensorBuienradar
from .sensors import NeerslagSensorStatus

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entity."""

    # Setup buienalarm
    buienAlarm = (config_entry.data.get('buienalarm') == True)
    buienAlarmLat = hass.config.latitude
    buienAlarmLon = hass.config.longitude
    if (config_entry.data.get('NeerslagSensorUseHAforLocation') == False):
        buienAlarmLat = config_entry.data.get('buienalarmLatitude')
        buienAlarmLon = config_entry.data.get('buienalarmLongitude')

    buienAlarm = NeerslagSensorBuienalarm.NeerslagSensorBuienalarm(hass, buienAlarm, buienAlarmLat, buienAlarmLon)
    config_entry.add_update_listener(buienAlarm.config_update_listener)

    # Setup buienradar
    buienRadar = (config_entry.data.get('buienradar') == True)
    buienRadarLat = hass.config.latitude
    buienRadarLon = hass.config.longitude
    if (config_entry.data.get('NeerslagSensorUseHAforLocation') == False):
        buienRadarLat = config_entry.data.get('buienradarLatitude')
        buienRadarLon = config_entry.data.get('buienradarLongitude')

    buienRadar = NeerslagSensorBuienradar.NeerslagSensorBuienradar(hass, buienRadar, buienRadarLat, buienRadarLon)
    config_entry.add_update_listener(buienRadar.config_update_listener)

    # Setup generic sensors
    neerslagRainNow = NeerslagSensorStatus.NeerslagSensorStatus('neerslag_rain_now', 'neerslag-sensor-rain-now-1', (buienAlarm or buienRadar))
    config_entry.add_update_listener(neerslagRainNow.config_update_listener)

    neerslagRainPrediction = NeerslagSensorStatus.NeerslagSensorStatus('neerslag_rain_prediction', 'neerslag-sensor-rain-prediction-1', (buienAlarm or buienRadar))
    config_entry.add_update_listener(neerslagRainPrediction.config_update_listener)

    # Add sensors to HA
    async_add_entities([ buienAlarm, buienRadar, neerslagRainNow, neerslagRainPrediction ])
