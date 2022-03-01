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
        if not len(self._attrs):
            return
        return self._attrs

    async def config_update_listener(self, hass, config, pp=None):
        self._enabled = ((config.data.get('buienalarm') == True) or (config.data.get('buienradar') == True))
