import aiohttp
import csv
from datetime import datetime, timedelta
import json
import logging
import math
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
    async_add_entities([ NeerslagSensor(hass, config_entry, True) ])

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
        self._icon = "mdi:weather-rainy"

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
        self._icon = "mdi:weather-rainy"

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


class NeerslagSensor(mijnBasis):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, enabled: bool):
        super().__init__(hass=hass, config_entry=config_entry, enabled=enabled)
        self._name = "neerslag_sensor"
        self._state = STATE_UNKNOWN
        self._unique_id = "neerslag-sensor-1"
        self._enabled = enabled
        self._icon = "mdi:weather-rainy"

        # Save which 'sources' are available and assign change handler
        self._process_buienalarm = (config_entry.data.get("buienalarm") == True)
        self._process_buienradar = (config_entry.data.get("buienradar") == True)
        config_entry.add_update_listener(self.config_update_listener)

        # Reset buffer and assign change handlers
        self._buffer = { "buienradar": {}, "buienalarm": {} }
        async_track_state_change(hass, [ "sensor.neerslag_buienalarm_regen_data", "sensor.neerslag_buienradar_regen_data" ], self.parse_rain_source_data)

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        return self._buffer

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
                old_buffer = self._buffer["buienalarm"]
                for entry in val["precip"]:
                    # Add to dictionary
                    key = dt_entry.strftime("%Y%m%d%H%M%S")
                    rain_val = entry
                    old_buffer[key] = { "time": dt_entry.strftime("%X"), "precip": rain_val }

                    # Add the delta
                    dt_entry = dt_entry + timedelta(seconds=dt_delta)

                # Remove all 'keys' that occured in the past to keep the data clean.
                self._buffer["buienalarm"] = {}
                dt_remove_before = dt_today.strftime("%Y%m%d%H%M%S")
                for key, val in old_buffer.items():
                    if (key > dt_remove_before):
                        self._buffer["buienalarm"][key] = val

        # Get sensor data for Buienradar
        if (entity_id == "sensor.neerslag_buienradar_regen_data"):
            for key, val in new_state.attributes.items():
                if (key != "data"):
                    continue

                # Initialize
                dt_start_hour = None

                # Loop entries
                entries = csv.reader(val.strip().split(), delimiter='|')
                old_buffer = self._buffer["buienradar"]
                for entry in entries:
                    # Convert 'time' to include the date.
                    dt_entry = datetime.combine(dt_today, datetime.strptime(entry[1] + ":00", '%H:%M:%S').time())

                    # Make sure the date is correct
                    if (dt_start_hour is None):
                        dt_start_hour = dt_entry.hour
                    elif (dt_entry.hour < dt_start_hour):
                        # In case we pass midnight, add 1 day to make sure our 'garbage collector' still works later on.
                        dt_entry = dt_entry + timedelta(days=1)

                    # Add to dictionary
                    key = dt_entry.strftime("%Y%m%d%H%M%S")
                    rain_val = round(math.pow(10, ((int(entry[0]) - 109) / 32)), 3)
                    old_buffer[key] = { "time": dt_entry.strftime("%X"), "precip": rain_val }

                # Remove all 'keys' that occured in the past to keep the data clean.
                self._buffer["buienradar"] = {}
                dt_remove_before = dt_today.strftime("%Y%m%d%H%M%S")
                for key, val in old_buffer.items():
                    if (key > dt_remove_before):
                        self._buffer["buienradar"][key] = val

        # The first time we get here there is only 1 sensor filled, but we need both.
        max_elems = min(len(self._buffer["buienalarm"]), len(self._buffer["buienradar"]))
        if(max_elems == 0):
            return
        _LOGGER.error("parse_rain_source_data() --> will only process " + str(max_elems) + " items.")

        # At this stage of the method, we have 2 arrays which are 'normalized' and only contain 'future' rain predictions.
        # We can now loop both arrays and determine if it is raining...

        # Update the state of this sensor, but only if the input data changed.
        self.schedule_update_ha_state(True)

    async def async_update(self):
        if (self._enabled == True):
            self._state = random()
        return True
