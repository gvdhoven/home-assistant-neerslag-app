import csv
import logging
import math
from datetime import datetime, timedelta

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

# debugging - start
import json
from datetime import date
def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
# debugging - END

# Cache  - since multiple sensors inherit from the base sensor.
_last_data = {}
_last_rain_now = ''
_last_rain_now_attr = {}
_last_rain_prediction = ""
_last_rain_prediction_attr = {}

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

    def getRainLevel(self, precip):
        # The following values are taken for the mm/hr precipitation:
        # - geen neerslag 0 mm
        # - lichte neerslag 0.1-1 mm
        # - matige neerslag 1-3 mm
        # - zware neerslag 3-10 mm
        # - zware buien > 10
        precip = round(precip, 1)
        if (precip < 0.1):
            return 'none'
        elif (precip <= 1):
            return 'light'
        elif (precip <= 3):
            return 'moderate'
        elif (precip <= 10):
            return 'heavy'
        return 'extreme'

    def getRainIcon(self, level):
        if (level == 'none'):
            return "mdi:weather-cloudy"
        elif (level == 'light'):
            return "mdi:weather-partly-rainy"
        elif (level == 'moderate'):
            return "mdi:weather-rainy"
        return "mdi:weather-pouring"

    def initSensorAttributes(self, p, dt):
        attr = { }
        attr['level'] = self.getRainLevel(p)
        attr['dry'] = (p == 0)
        attr['when'] = dt
        attr['mm_hr'] = p
        attr['icon'] = self.getRainIcon(attr['level'])
        return attr

    def equal_dicts(self, a, b, ignore_keys):
        ka = set(a).difference(ignore_keys)
        kb = set(b).difference(ignore_keys)
        return ka == kb and all(a[k] == b[k] for k in ka)

    def update_neerslag_sensor_cache(self, evt):
        global _last_data
        global _last_rain_now
        global _last_rain_now_attr
        global _last_rain_prediction
        global _last_rain_prediction_attr

        # Save today date for comparison
        dt_today = datetime.today()
        old_data = _last_data
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
        _last_data = {}
        dt_remove_before = dt_today.strftime("%Y%m%d%H%M%S")
        for key, val in old_data.items():
            if (key > dt_remove_before):
                _last_data[key] = val

        # Data not yet complete
        if (not len(_last_data)):
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
        maxP = 0
        curP = 0
        curDT = None

        # We can now loop the data and determine if it is dry or raining and when that will change...
        for key, val in _last_data.items():
            # Combine information from buienalarm and buienradar
            p = 0
            if ('buienalarm' in val):
                p += val['buienalarm']

            if ('buienradar' in val):
                p += val['buienradar']

            # We have a value, so now we can check it.
            dt = datetime.strptime(key,'%Y%m%d%H%M%S')
            if (raining_type is None):
                # Save current precipitation
                curP = p
                curDT = dt

                # Compare it
                if (p == 0):
                    # Currently no rain
                    raining_type = 0
                    rain_prediction_text = self._translations['status']['stays_dry']
                else:
                    # It is raining now
                    raining_type = 1
                    rain_prediction_text = self._translations['status']['is_raining']
            else:
                if (raining_type == 0):
                    if (p > 0):
                        # Rain starts within 2 hours
                        raining_type = 4
                        rain_prediction_text = self._translations['status']['starts'].format(dt)

                        # Initialize prediction attributes
                        if (rain_prediction_attr is None):
                            rain_prediction_attr = self.initSensorAttributes(p, dt)
                elif (raining_type == 1):
                    if (p == 0):
                        # It is currently raining but will stop within 2 hours
                        raining_type = 2
                        rain_prediction_text = self._translations['status']['stops'].format(dt)

                        # Initialize prediction attributes
                        if (rain_prediction_attr is None):
                            rain_prediction_attr = self.initSensorAttributes(p, dt)
                elif (raining_type == 2):
                    if (p > 0):
                        # Raining will stop but restart within 2 hours
                        raining_type = 3
                        rain_prediction_text += self._translations['status']['starts_again'].format(dt)
                elif (raining_type == 4):
                    if (p == 0):
                        # Rain starts within 2 hours but will stop
                        raining_type = 5
                        rain_prediction_text += self._translations['status']['stops_at'].format(dt)

            if (p > maxP):
                maxP = p

        # In case it remains dry or stays raining for a long time, this variable is still None, so fill it.
        if (rain_prediction_attr is None):
            rain_prediction_attr = self.initSensorAttributes(p, dt)

        # Update current state, but only if the input data changed.
        rain_now_attr = self.initSensorAttributes(curP, curDT)
        rain_now = rain_now_attr['level']

        # Calculate how long this state 'lasts' but maximize it at 1.5hrs.
        # We maximize this because (depending on the data we get from both sources) otherwise it would sometimes be 105, sometimes 110 etc.
        rain_now_attr['for_at_least'] = (rain_prediction_attr['when'] - curDT).total_seconds() / 60.0
        if (rain_now_attr['for_at_least'] > 90):
            rain_now_attr['for_at_least'] = 90

        # Compare states and update sensor if needed
        rain_now_attr_equal = self.equal_dicts(rain_now_attr, _last_rain_now_attr, ['when'] )
        if ((rain_now != _last_rain_now) or (not rain_now_attr_equal)):
            _last_rain_now = rain_now
            _last_rain_now_attr = rain_now_attr
            self._hass.states.set('sensor.neerslag_rain_now', rain_now, rain_now_attr, True)
            _LOGGER.error('sensor.neerslag_rain_now changed to ' + _last_rain_now + ': ' + json.dumps(_last_rain_now_attr, default=json_serial))


        # Expected state (stays dry/stays raining/starts/stops/etc.) + expected_duration_in_minutes + expected_change_in_minutes?
        rain_prediction = rain_prediction_attr['level']
        rain_prediction_attr['text'] = rain_prediction_text + '.'

        # Calculate how long this state 'lasts' but maximize it at 1.5hrs.
        # We maximize this because (depending on the data we get from both sources) otherwise it would sometimes be 105, sometimes 110 etc.
        rain_prediction_attr['for_at_least'] = (rain_prediction_attr['when'] - curDT).total_seconds() / 60.0
        if (rain_prediction_attr['for_at_least'] > 90):
            rain_prediction_attr['for_at_least'] = 90
        rain_prediction_attr['when'] = curDT

        # Compare states and update sensor if needed
        rain_prediction_attr_equal = self.equal_dicts(rain_prediction_attr, _last_rain_prediction_attr, ['when'] )
        if ((rain_prediction != _last_rain_prediction) or (not rain_prediction_attr_equal)):
            _last_rain_prediction = rain_prediction
            _last_rain_prediction_attr = rain_prediction_attr
            self._hass.states.set('sensor.neerslag_rain_prediction', rain_prediction, rain_prediction_attr, True)
            _LOGGER.error('sensor.neerslag_rain_prediction changed to ' + _last_rain_prediction + ': ' + json.dumps(_last_rain_prediction_attr, default=json_serial))

