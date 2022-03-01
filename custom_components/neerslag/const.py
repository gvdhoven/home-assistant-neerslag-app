"""Constants for the Neerslag Sensor (Buienalarm / Buienradar) integration."""
from datetime import timedelta

DOMAIN = "neerslag"
FRONTEND_SCRIPT_URL = "/neerslag-card.js"
DATA_EXTRA_MODULE_URL = 'frontend_extra_module_url'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=3)
