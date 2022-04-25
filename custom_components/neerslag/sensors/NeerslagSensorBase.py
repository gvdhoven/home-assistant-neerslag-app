import csv
import json
import logging
import math
from datetime import date, datetime, timedelta

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError (f'Type {type(obj)} not serializable')

# Cache  - since multiple sensors inherit from the base sensor.
_LAST_DATA = {}
_LAST_RAIN_NOW = ''
_LAST_RAIN_NOW_ATTR = {}
_LAST_RAIN_PREDECTION = ""
_LAST_RAIN_PREDECTION_ATTR = {}

class NeerslagSensorBase(Entity):
    def __init__(self, hass, enabled: bool):
        self._hass = hass
        self._enabled = enabled
        self._name = ''
        self._unique_id = ''
        self._icon = 'mdi:weather-cloudy'
        self._state = 'working'

        # Load translations
        self._translations = {
            "status": {
                "is_dry": "Het is droog",
                "is_raining": "Het regent",
                "stays_dry": "Het blijft droog",
                "starts": "Neerslag begint rond {:%H:%M}",
                "stops": "Neerslag stopt rond {:%H:%M}",
                "starts_again": " en begint weer rond {:%H:%M}",
                "stops_at": " en duurt ongeveer tot {:%H:%M}"
            },
            "rain_now": {
                "none": "Geen neerslag",
                "light": "Lichte neerslag",
                "moderate": "Matige neerslag",
                "heavy": "Zware neerslag",
                "extreme": "Zware buien"
            }
        }

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        """Return unique ID."""
        return self._unique_id

    @property
    def icon(self):
        return self._icon

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._enabled

    @property
    def state(self):
        return self._state

    def update(self):
        return True

    def get_rain_level(self, precip):
        # The following values are taken for the mm/hr precipitation:
        # - geen neerslag 0 mm
        # - lichte neerslag 0.1-1 mm
        # - matige neerslag 1-3 mm
        # - zware neerslag 3-10 mm
        # - zware buien > 10
        precip = round(precip, 1)
        if (precip < 0.1):
            return 'none'
        if (precip <= 1):
            return 'light'
        if (precip <= 3):
            return 'moderate'
        if (precip <= 10):
            return 'heavy'
        return 'extreme'

    def get_rain_icon(self, level):
        if (level == 'none'):
            return "mdi:weather-cloudy"
        if (level == 'light'):
            return "mdi:weather-partly-rainy"
        if (level == 'moderate'):
            return "mdi:weather-rainy"
        return "mdi:weather-pouring"

    def init_sensor_attributes(self, precipitation, timestamp):
        attr = { }
        attr['dry'] = (precipitation == 0)
        attr['from_dt'] = timestamp
        attr['to_dt'] = timestamp
        attr['mm_hr'] = precipitation
        attr['level'] = self.get_rain_level(precipitation)
        attr['icon'] = self.get_rain_icon(attr['level'])
        return attr

    def equal_dicts(self, dict_a, dict_b, ignore_keys):
        keys_a = set(dict_a).difference(ignore_keys)
        keys_b = set(dict_b).difference(ignore_keys)
        return keys_a == keys_b and all(dict_a[key] == dict_b[key] for key in keys_a)

    def update_neerslag_sensor_cache(self, evt):
        global _LAST_DATA
        global _LAST_RAIN_NOW
        global _LAST_RAIN_NOW_ATTR
        global _LAST_RAIN_PREDECTION
        global _LAST_RAIN_PREDECTION_ATTR

        # Save today date for comparison
        dt_today = datetime.today()
        old_data = _LAST_DATA
        new_data = evt['data']

        # Get sensor data for Buienalarm
        if (self._name == 'neerslag_buienalarm_regen_data'):
            # Initialize
            dt_start = datetime.fromtimestamp(new_data['start'])
            dt_delta = new_data["delta"]
            dt_entry = dt_start

            # Loop entries
            for entry in new_data['precip']:
                # Initialize dictionary if needed
                data_key = dt_entry.strftime("%Y%m%d%H%M%S")
                if (not data_key in old_data):
                    old_data[data_key] = { "time": dt_entry.strftime("%X") }

                # Add to dictionary
                old_data[data_key]['buienalarm'] = entry

                # Add the delta
                dt_entry = dt_entry + timedelta(seconds=dt_delta)

        # Get sensor data for Buienradar
        if (self._name == 'neerslag_buienradar_regen_data'):
            # Initialize
            dt_start_hour = None

            # Loop entries
            entries = csv.reader(new_data.split(), delimiter='|')
            for entry in entries:
                # Convert 'time' to include the date.
                dt_entry = datetime.combine(dt_today, datetime.strptime(entry[1] + ":00", '%H:%M:%S').time())

                # Make sure the date is correct
                if (dt_start_hour is None):
                    dt_start_hour = dt_entry.hour
                elif (dt_entry.hour < dt_start_hour):
                    # In case we pass midnight, add 1 day to make sure our 'garbage collector' still works later on.
                    dt_entry = dt_entry + timedelta(days=1)

                # Initialize dictionary if needed
                data_key = dt_entry.strftime("%Y%m%d%H%M%S")
                if (not data_key in old_data):
                    old_data[data_key] = { "time": dt_entry.strftime("%X") }

                # Add to dictionary
                old_data[data_key]["buienradar"] = round(math.pow(10, ((int(entry[0]) - 109) / 32)), 3)

        # Only keep keys which are in the future
        _LAST_DATA = {}
        dt_remove_before = dt_today.strftime("%Y%m%d%H%M%S")
        for key, val in old_data.items():
            if (key > dt_remove_before):
                _LAST_DATA[key] = val

        # Data not yet complete
        if (bool(_LAST_DATA) is False):
            _LOGGER.error('No items in buffer!')
            return

        # raining_type explained:
        # 0: Geen neerslag
        # 1: Neerslag
        # 2: Neerslag stopt rond {}
        # 3: Neerslag stopt rond {} en begint weer rond {}
        # 4: Neerslag begint rond {}
        # 5: Neerslag begint rond {} en duurt ongeveer tot {}
        raining_type = None

        # Variables used below
        rain_prediction_text = ""
        rain_prediction_attr = None
        max_precipitation = 0
        cur_precipitation = 0
        cur_datetime = None

        # We can now loop the data and determine if it is dry or raining and when that will change...
        for key, val in _LAST_DATA.items():
            # Combine information from buienalarm and buienradar
            precipitation = 0
            if ('buienalarm' in val):
                precipitation += val['buienalarm']

            if ('buienradar' in val):
                precipitation += val['buienradar']

            # We have a value, so now we can check it.
            timestamp = datetime.strptime(key, '%Y%m%d%H%M%S')
            if (raining_type is None):
                # Save current precipitation
                cur_precipitation = precipitation
                cur_datetime = timestamp

                # Compare it
                if (precipitation == 0):
                    # Currently no rain
                    raining_type = 0
                    rain_prediction_text = self._translations['status']['stays_dry']
                else:
                    # It is raining now
                    raining_type = 1
                    rain_prediction_text = self._translations['status']['is_raining']
            else:
                if (raining_type == 0):
                    if (precipitation > 0):
                        # Rain starts within 2 hours
                        raining_type = 4
                        rain_prediction_text = self._translations['status']['starts'].format(timestamp)

                        # Initialize prediction attributes
                        if (rain_prediction_attr is None):
                            rain_prediction_attr = self.init_sensor_attributes(precipitation, timestamp)
                elif (raining_type == 1):
                    if (precipitation == 0):
                        # It is currently raining but will stop within 2 hours
                        raining_type = 2
                        rain_prediction_text = self._translations['status']['stops'].format(timestamp)

                        # Initialize prediction attributes
                        if (rain_prediction_attr is None):
                            rain_prediction_attr = self.init_sensor_attributes(precipitation, timestamp)
                elif (raining_type == 2):
                    if (precipitation > 0):
                        # Raining will stop but restart within 2 hours
                        raining_type = 3
                        rain_prediction_text += self._translations['status']['starts_again'].format(timestamp)
                elif (raining_type == 4):
                    if (precipitation == 0):
                        # Rain starts within 2 hours but will stop
                        raining_type = 5
                        rain_prediction_text += self._translations['status']['stops_at'].format(timestamp)

            if (precipitation > max_precipitation):
                max_precipitation = precipitation

        # In case it remains dry or stays raining for a long time, this variable is still None, so fill it.
        if (rain_prediction_attr is None):
            rain_prediction_attr = self.init_sensor_attributes(precipitation, timestamp)

        # Update current state, but only if the input data changed.
        rain_now_attr = self.init_sensor_attributes(cur_precipitation, cur_datetime)
        rain_now = rain_now_attr['level']

        # Calculate how long this state 'lasts' but maximize it at 1.5hrs.
        # We maximize this because (depending on the data we get from both sources) otherwise it would sometimes be 105, sometimes 110 etc.
        rain_now_attr['for_at_least'] = (rain_prediction_attr['to_dt'] - cur_datetime).total_seconds() / 60.0
        if (rain_now_attr['for_at_least'] > 90):
            rain_now_attr['for_at_least'] = 90
        rain_now_attr['from_dt'] = cur_datetime
        rain_now_attr['to_dt'] = cur_datetime + timedelta(minutes=rain_now_attr['for_at_least'])

        # Compare states and update sensor if needed
        rain_now_attr_equal = self.equal_dicts(rain_now_attr, _LAST_RAIN_NOW_ATTR, [ 'from_dt', 'to_dt' ])
        if ((rain_now != _LAST_RAIN_NOW) or (not rain_now_attr_equal)):
            _LAST_RAIN_NOW = rain_now
            _LAST_RAIN_NOW_ATTR = rain_now_attr
            self._hass.states.set('sensor.neerslag_rain_now', rain_now, rain_now_attr, True)
            _LOGGER.debug('sensor.neerslag_rain_now changed to ' + _LAST_RAIN_NOW + ': ' + json.dumps(_LAST_RAIN_NOW_ATTR, default=json_serial))


        # Expected state (stays dry/stays raining/starts/stops/etc.) + expected_duration_in_minutes + expected_change_in_minutes?
        rain_prediction = rain_prediction_attr['level']
        rain_prediction_attr['text'] = rain_prediction_text + '.'

        # Calculate how long this state 'lasts' but maximize it at 1.5hrs.
        # We maximize this because (depending on the data we get from both sources) otherwise it would sometimes be 105, sometimes 110 etc.
        rain_prediction_attr['for_at_least'] = (rain_prediction_attr['to_dt'] - cur_datetime).total_seconds() / 60.0
        if (rain_prediction_attr['for_at_least'] > 90):
            rain_prediction_attr['for_at_least'] = 90
        rain_prediction_attr['from_dt'] = cur_datetime
        rain_prediction_attr['to_dt'] = cur_datetime + timedelta(minutes=rain_prediction_attr['for_at_least'])

        # Compare states and update sensor if needed
        rain_prediction_attr_equal = self.equal_dicts(rain_prediction_attr, _LAST_RAIN_PREDECTION_ATTR, [ 'from_dt', 'to_dt' ])
        if ((rain_prediction != _LAST_RAIN_PREDECTION) or (not rain_prediction_attr_equal)):
            _LAST_RAIN_PREDECTION = rain_prediction
            _LAST_RAIN_PREDECTION_ATTR = rain_prediction_attr
            self._hass.states.set('sensor.neerslag_rain_prediction', rain_prediction, rain_prediction_attr, True)
            _LOGGER.debug('sensor.neerslag_rain_prediction changed to ' + _LAST_RAIN_PREDECTION + ': ' + json.dumps(_LAST_RAIN_PREDECTION_ATTR, default=json_serial))
