"""Constants for the AL-KO integration."""

from homeassistant.const import CONF_ACCESS_TOKEN


DOMAIN = "alko"

BASE_URL = "https://api.al-ko.com/v0/iot/things"
OAUTH2_AUTHORIZE = "https://idp.al-ko.com/connect/authorize"
OAUTH2_TOKEN = "https://idp.al-ko.com/connect/token"

SWITCHES = [
    "ecoMode",
    "rainSensor"
]
