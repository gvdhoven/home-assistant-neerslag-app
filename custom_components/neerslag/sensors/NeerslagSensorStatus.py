from homeassistant.helpers.entity import Entity

class NeerslagSensorStatus(Entity):
    def __init__(self, name, uniqueid, enabled: bool):
        self._name = name
        self._unique_id = uniqueid
        self._icon = 'mdi:weather-cloudy'
        self._state = 'working'
        self._enabled = enabled
        self._attrs = {}

    @property
    def state_attributes(self):
        return self._attrs

    async def config_update_listener(self, hass, config, pp=None):
        # pylint:disable=unused-argument,invalid-name
        self._enabled = ((config.data.get('buienalarm') is True) or (config.data.get('buienradar') is True))
