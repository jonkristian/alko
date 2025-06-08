"""Constants for the AL-KO integration."""

DOMAIN = "alko"

BASE_URL = "https://api.al-ko.com/v1/iot/things"

DATA_ALKO = "alko"
DATA_ALKO_CONFIG = "alko_config"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
ALKO_SCOPES = "alkoCulture alkoCustomerId introspection offline_access"

OAUTH2_AUTHORIZE = "https://idp.al-ko.com/connect/token"
OAUTH2_TOKEN = "https://idp.al-ko.com/connect/token"
