import aiohttp
import csv
from datetime import datetime, timedelta
import json
import logging
import math
import os
import random as rand
from random import random

from homeassistant.core import HomeAssistant, callback
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=180)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up sensor entity."""

    # if config_entry.data.get("buienalarm") == True:
    #     async_add_entities([NeerslagSensorBuienalarm(hass, config_entry)], update_before_add=True)

    # if config_entry.data.get("buienradar") == True:
    #     async_add_entities([NeerslagSensorBuienradar(hass, config_entry)], update_before_add=True)
    # # async_add_entities([NeerslagSensor(hass, config_entry)])

    # entity_registry_obj = await hass.helpers.entity_registry.async_get_registry()
    # registry_entry = entity_registry_obj.async_get(config_entry.unique_id)

    dev_reg = await hass.helpers.device_registry.async_get_registry()
    ent_reg = await hass.helpers.entity_registry.async_get_registry()

    # dds = async_get_platforms(hass, "neerslag")
    # _LOGGER.info(len(dds))
    # async_reset

    # _LOGGER.info("----------->>>")
    # _LOGGER.info(dev_reg.devices)
    # _LOGGER.info(ent_reg.entities)

    # xx = "neerslag_DummyABC"
    # aa = ent_reg.async_get("sensor.neerslag_dummyabc")

    # _LOGGER.info("<<1aa<<<<<<<<<<<<<<<<<----------->>>")
    # _LOGGER.info(aa)
    # _LOGGER.info("<<<bb<<<<<<<<<<<<<<<<----------->>>")

    # bb = ent_reg.async_get_entity_id(domain='sensor', platform='neerslag', unique_id='neerslag-sensor-DummyABC')
    # _LOGGER.info(bb)
    # _LOGGER.info("<<<cc<<<<<<<<<<<<<<<<----------->>>")

    # cc = async_entries_for_config_entry(ent_reg, config_entry.entry_id)
    # _LOGGER.info(cc)
    # _LOGGER.info("<<<dd<<<<<<<<<<<<<<<<----------->>>")

   # ent_reg = hass.helpers.entity_registry.async_get_registry()
   # aaa = ent_reg.async_get_entity_id("neerslag", "sensor", self._unique_id)

   # _LOGGER.info(aaa)

   # _LOGGER.info(config_entry.entry_id)
   # _LOGGER.info(config_entry.unique_id)

   # rr = await config_entry.ConfigEntries.async_reload(config_entry.entry_id)
   # _LOGGER.info(rr)

    # async_add_entities([DummyABC(hass, config_entry)], update_before_add=True)
    # async_add_entities([DummyABC(hass, config_entry)], update_before_add=True)

    # if config_entry.data.get("buienalarm") == True:
    #     _LOGGER.info("<><><><>----------------<><<><>")
    #     async_add_entities([DummyABC(hass, config_entry, True)], update_before_add=True)

    # if config_entry.data.get("buienalarm") == False:
    #     async_add_entities([DummyABC(hass, config_entry, False)], update_before_add=False)

    # if config_entry.data.get("buienradar") == True:
    #     async_add_entities([DummyDEF(hass, config_entry, True)], update_before_add=True)

    # if config_entry.data.get("buienradar") == False:
    #     async_add_entities([DummyDEF(hass, config_entry, False)], update_before_add=False)

    # Add buienalarm sensor
    doBuienalarm = (config_entry.data.get("buienalarm") == True)
    async_add_entities([ NeerslagSensorBuienalarm(hass, config_entry, doBuienalarm) ], update_before_add=doBuienalarm)

    # Add buienradar sensor
    doBuienradar = (config_entry.data.get("buienradar") == True)
    async_add_entities([ NeerslagSensorBuienradar(hass, config_entry, doBuienradar) ], update_before_add=doBuienradar)

    # Add 'main' sensor, it will be updated automatically by the others so we don't need to update before add.
    async_add_entities([ NeerslagStatus(hass, config_entry, True) ])

        # async_add_entities([NeerslagSensor(hass, config_entry)])

    # device_registry = await hass.helpers.device_registry.async_get_registry()
    # device_registry.async_get_or_create(
    #     config_entry_id=config_entry.entry_id,
    #     default_manufacturer="dummy data",
    #     default_model="dummy data",
    #     default_name="dummy data")


class mijnBasis(Entity):
    _enabled = None
    _unique_id = None
    _name = None

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        _LOGGER.info("--<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>--->>>>>>>>>>>>>>>>>>>>>>>>")
        # self._enabled = enabled
        # config_entry.add_update_listener(self.mine_update_listener)

    async def mine_update_listener(self, hass: HomeAssistant, config_entry: ConfigEntry, pp=None):
        """Handle options update."""

        # if(self._name == "neerslag_DummyABC"):
        #     self._enabled = config_entry.data.get("buienalarm")

        # if(self._name == "neerslag_DummyDEF"):
        #     self._enabled = config_entry.data.get("buienradar")

        if(self._name == "neerslag_buienalarm_regen_data"):
            self._enabled = config_entry.data.get("buienalarm")

        if(self._name == "neerslag_buienradar_regen_data"):
            self._enabled = config_entry.data.get("buienradar")

      # self._enabled = config_entry.data.get(enabled)
      # await hass.config_entries.async_remove(config_entry.entry_id)
      # rr = hass.config_entries.async_entries(DOMAIN)
      # hass.config_entries.async_update_entry(config_entry, data=config_entry.options)
      # await hass.config_entries.async_reload(config_entry.entry_id)

    @property
    def device_info(self):
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                ("neerslag", "neerslag-device")
            },
            "name": "Neerslag App",
            "manufacturer": "aex351",
            "model": "All-in-one package",
            "sw_version": "",
            "via_device": ("neerslag", "abcd"),
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._enabled

    @property
    def state(self):
        return self._state

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        """Return unique ID."""
        return self._unique_id

    async def async_update(self):
        self._state = random()
        return True


class DummyABC(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)
        self._name = "neerslag_DummyABC"
        self._state = "working"  # None
        self._attrs = {}
        self._unique_id = "neerslag-sensor-DummyABC"

        self._enabled = enabled
        config_entry.add_update_listener(self.mine_update_listener)


class DummyDEF(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)
        self._name = "neerslag_DummyDEF"
        self._state = "working"  # None
        self._attrs = {}
        self._unique_id = "neerslag-sensor-DummyDEF"

        # _LOGGER.info(">>>>>>>>>>>>>>>>>>>>>>>>")
        # _LOGGER.info(config_entry.entry_id)
        # _LOGGER.info(config_entry.unique_id)

        self._enabled = enabled
        config_entry.add_update_listener(self.mine_update_listener)


class NeerslagSensorBuienalarm(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)
        self._name = "neerslag_buienalarm_regen_data"
        self._state = "working"  # None
        self._attrs = {}
        self._unique_id = "neerslag-sensor-buienalarm-1"

        self._enabled = enabled
        config_entry.add_update_listener(self.mine_update_listener)

        if config_entry.data.get("NeerslagSensorUseHAforLocation") == True:
            self._lat = hass.config.latitude
            self._lon = hass.config.longitude

        else:
            self._lat = config_entry.data.get("buienalarmLatitude")
            self._lon = config_entry.data.get("buienalarmLongitude")

        # format values, enforce 3 decimals
        self._lat = f'{float(self._lat):.3f}'
        self._lon = f'{float(self._lon):.3f}'

        # self._entity_picture = "https://www.buienalarm.nl/assets/img/social.png"
        self._icon = "mdi:weather-cloudy"

    @property
    def icon(self):
        return self._icon

    @property
    def state_attributes(self):
        if not len(self._attrs):
            return
        return self._attrs
        # return {"data": self._attrs}

    async def async_update(self):
        if(self._enabled == True):
            self._state = random()
            self._attrs = await self.getBuienalarmData()
        return True

    async def getBuienalarmData(self) -> str:
        data = json.loads('{"data":""}')
        # return data
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession() as session:
                url = 'https://cdn-secure.buienalarm.nl/api/3.4/forecast.php?lat=' + self._lat + '&lon=' + self._lon + '&region=nl&unit=mm%2Fu&c=' + str(rand.randint(0, 999999999999999))
                async with session.get(url, timeout=timeout) as response:
                    html = await response.text()
                    dataRequest = html.replace('\r\n', ' ')
                    if dataRequest == "" :
                        dataRequest = ""
                    data = json.loads('{"data":' + dataRequest + '}')
                    # _LOGGER.info(data)
                    await session.close()
        except:
            _LOGGER.info("getBuienalarmData - timeout")
            pass

        return data


class NeerslagSensorBuienradar(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)

        self._name = "neerslag_buienradar_regen_data"
        self._state = "working"  # None
        self._attrs = {}
        self._unique_id = "neerslag-sensor-buienradar-1"

        self._enabled = enabled
        config_entry.add_update_listener(self.mine_update_listener)

        if config_entry.data.get("NeerslagSensorUseHAforLocation") == True:
            self._lat = hass.config.latitude
            self._lon = hass.config.longitude

        else:
            self._lat = config_entry.data.get("buienradarLatitude")
            self._lon = config_entry.data.get("buienradarLongitude")

        # format values, enforce 2 decimals
        self._lat = f'{float(self._lat):.2f}'
        self._lon = f'{float(self._lon):.2f}'

        # self._entity_picture = "https://cdn.buienradar.nl/resources/images/br-logo-square.png"
        self._icon = "mdi:weather-cloudy"

    @property
    def icon(self):
        return self._icon

    @property
    def state_attributes(self):
        if not len(self._attrs):
            return
        return self._attrs
        # return {"data": self._attrs}

    async def async_update(self):
        if(self._enabled == True):
            self._state = random()
            self._attrs = await self.getBuienradarData()
        return True

    async def getBuienradarData(self) -> str:
        data = json.loads('{"data":""}')
        # return data
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession() as session:
                # https://www.buienradar.nl/overbuienradar/gratis-weerdata
                url = 'https://gps.buienradar.nl/getrr.php?lat=' + self._lat + '&lon=' + self._lon + '&c=' + str(rand.randint(0, 999999999999999))
                # _LOGGER.info(url)
                async with session.get(url, timeout=timeout) as response:
                    html = await response.text()
                    dataRequest = html.replace('\r\n', ' ')
                    if dataRequest == "" :
                        dataRequest = ""
                    data = json.loads('{"data": "' + dataRequest + '"}')
                    # _LOGGER.info(data)
                    await session.close()
        except:
            _LOGGER.info("getBuienradarData - timeout")
            pass

        return data


class NeerslagStatus(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)
        self._name = "neerslag_status"
        self._state = STATE_UNKNOWN
        self._unique_id = "neerslag-status-1"
        self._enabled = enabled
        self._icon = "mdi:weather-cloudy"

        # Load translations
        if (config_entry.data.get("NeerslagStateInEnglish") == True):
            self._translations = self.load_translations('en')
        else:
            self._translations = self.load_translations('nl')

        # Save which 'sources' are available and assign change handler
        self._process_buienalarm = (config_entry.data.get("buienalarm") == True)
        self._process_buienradar = (config_entry.data.get("buienradar") == True)
        config_entry.add_update_listener(self.config_update_listener)

        # Reset buffer and assign change handlers
        self._attributes = { "icon": "mdi:weather-cloudy", "rain_level": "", "is_raining": False, "data": {} }
        async_track_state_change(hass, [ "sensor.neerslag_buienalarm_regen_data", "sensor.neerslag_buienradar_regen_data" ], self.parse_rain_source_data)

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        return self._attributes

    def load_translations(self, lang):
        data = {}
        translation_file = os.path.join(os.path.dirname(__file__), "translations/" + lang + ".json")

        try:
            f = open(translation_file)
            data = json.load(f)
            data = data['sensor'] # Only interested in sensor translations
            f.close()
        except:
            _LOGGER.error("NeerslagSensor->load_translations(): failed to load " + translation_file)
            pass

        return data

    async def config_update_listener(self, hass: HomeAssistant, config_entry: ConfigEntry, pp=None):
        self._process_buienalarm = (config_entry.data.get("buienalarm") == True)
        self._process_buienradar = (config_entry.data.get("buienradar") == True)
        self._enabled = (self._process_buienalarm or self._process_buienradar)

    @callback
    def parse_rain_source_data(self, entity_id, old_state, new_state):
        if (self._enabled == False):
            return
        elif (new_state is None):
            return
        elif (new_state.state in [STATE_UNKNOWN, STATE_UNAVAILABLE]):
            return

        # Save today date for comparison
        dt_today = datetime.today()
        old_data = self._attributes["data"]

        # Get sensor data for Buienalarm
        if (entity_id == "sensor.neerslag_buienalarm_regen_data"):
            for key, val in new_state.attributes.items():
                if (key != "data"):
                    continue

                # Initialize
                dt_start = datetime.fromtimestamp(val["start"])
                dt_delta = val["delta"]
                dt_entry = dt_start

                # Loop entries
                for entry in val["precip"]:
                    # Initialize dictionary if needed
                    data_key = dt_entry.strftime("%Y%m%d%H%M%S")
                    if (not data_key in old_data):
                        old_data[data_key] = { "time": dt_entry.strftime("%X") }

                    # Add to dictionary
                    old_data[data_key]["buienalarm"] = entry

                    # Add the delta
                    dt_entry = dt_entry + timedelta(seconds=dt_delta)

        # Get sensor data for Buienradar
        if (entity_id == "sensor.neerslag_buienradar_regen_data"):
            for key, val in new_state.attributes.items():
                if (key != "data"):
                    continue

                # Initialize
                dt_start_hour = None

                # Loop entries
                entries = csv.reader(val.strip().split(), delimiter='|')
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
        self._attributes["data"] = {}
        dt_remove_before = dt_today.strftime("%Y%m%d%H%M%S")
        for key, val in old_data.items():
            if (key > dt_remove_before):
                self._attributes["data"][key] = val

        # Data not yet complete
        if(not len(self._attributes["data"])):
            _LOGGER.error("No items in buffer!")
            return

        # Save current states
        prev_status = self._state
        prev_icon = self._attributes["icon"]
        prev_is_raining = self._attributes["is_raining"]
        prev_rain_level = self._attributes["rain_level"]

        # raining_state explained:
        # 0: Geen neerslag
        # 1: Neerslag
        # 2: Neerslag stopt rond {}
        # 3: Neerslag stopt rond {} en begint weer rond {}
        # 4: Neerslag begint rond {}
        # 5: Neerslag begint rond {} en duurt ongeveer tot {}
        raining_state = None
        maxP = 0
        maxDT = None
        new_status = ""

        # We can now loop the data and determine if it is dry or raining and when that will change...
        for key, val in self._attributes["data"].items():
            # Combine information from buienalarm and buienradar
            p = 0
            if ("buienalarm" in val):
                p += val["buienalarm"]

            if ("buienradar" in val):
                p += val["buienradar"]

            # We have a value, so now we can check it.
            dt = datetime.strptime(key,'%Y%m%d%H%M%S')
            if (raining_state is None):
                if (p == 0):
                    # Currently no rain
                    raining_state = 0
                    new_status = self._translations['status']['no_precip']
                else:
                    # It is raining now
                    raining_state = 1
                    new_status = self._translations['status']['precip']
            else:
                if (raining_state == 0):
                    if (p > 0):
                        # Rain starts within 2 hours
                        raining_state = 4
                        new_status = self._translations['status']['starts'].format(dt)
                elif (raining_state == 1):
                    if (p == 0):
                        # It is currently raining but will stop within 2 hours
                        raining_state = 2
                        new_status = self._translations['status']['stops'].format(dt)
                elif (raining_state == 2):
                    if (p > 0):
                        # Raining will stop but restart within 2 hours
                        raining_state = 3
                        new_status += self._translations['status']['starts_again'].format(dt)
                elif (raining_state == 4):
                    if (p == 0):
                        # Rain starts within 2 hours but will stop
                        raining_state = 5
                        new_status += self._translations['status']['stops_at'].format(dt)

            if (p > maxP):
                maxP = p
                maxDT = dt

        # Check previous values
        new_is_raining = (maxP > 0.1)

        # The following values are taken for the mm/hr precipitation:
        # - geen neerslag 0 mm
        # - lichte neerslag 0.1-1 mm
        # - matige neerslag 1-3 mm
        # - zware neerslag 3-10 mm
        # - zware buien > 10
        maxP = round(maxP, 1)
        if (maxP < 0.1):
            new_icon = "mdi:weather-cloudy"
            new_rain_level = self._translations['rain_level']['none']
        elif (maxP <= 1):
            new_icon = "mdi:weather-partly-rainy"
            new_rain_level = self._translations['rain_level']['light'].format(maxP, maxDT)
        elif (maxP <= 3):
            new_icon = "mdi:weather-rainy"
            new_rain_level = self._translations['rain_level']['moderate'].format(maxP, maxDT)
        elif (maxP <= 10):
            new_icon = "mdi:weather-pouring"
            new_rain_level = self._translations['rain_level']['heavy'].format(maxP, maxDT)
        elif (maxP > 10):
            new_icon = "mdi:weather-pouring"
            new_rain_level = self._translations['rain_level']['extreme'].format(maxP, maxDT)

        # Finish sentences
        new_status += "."
        new_rain_level += "."

        # Update the state of this sensor, but only if the input data changed.
        if ((new_status != prev_status) or
            (new_icon != prev_icon) or
            (new_is_raining != prev_is_raining) or
            (new_rain_level != prev_rain_level)):
            # Something changed, so update the state!
            self._state = new_status
            self._attributes["icon"] = new_icon
            self._attributes["is_raining"] = new_is_raining
            self._attributes["rain_level"] = new_rain_level
            self.schedule_update_ha_state(True)

    async def async_update(self):
        return True
