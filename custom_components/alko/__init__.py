"""The AL-KO integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp.client_exceptions import ClientResponseError
from pyalko import Alko
from pyalko.exceptions import AlkoAuthenticationException, AlkoException
from pyalko.objects.device import AlkoDevice
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import (
    aiohttp_client,
    config_entry_oauth2_flow,
    config_validation as cv,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ConfigEntryAlkoClient, AlkoLocalOAuth2Implementation
from .config_flow import OAuth2FlowHandler
from .const import DOMAIN, OAUTH2_AUTHORIZE, OAUTH2_TOKEN

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): cv.string,
                vol.Required(CONF_CLIENT_SECRET): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = (SENSOR_DOMAIN, SELECT_DOMAIN, SWITCH_DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AL-KO component."""
    hass.data[DOMAIN] = {}

    if DOMAIN not in config:
        return True

    hass.data[DOMAIN][CONF_CLIENT_ID] = config[DOMAIN][CONF_CLIENT_ID]

    OAuth2FlowHandler.async_register_implementation(
        hass,
        AlkoLocalOAuth2Implementation(
            hass,
            DOMAIN,
            config[DOMAIN][CONF_CLIENT_ID],
            config[DOMAIN][CONF_CLIENT_SECRET],
            OAUTH2_AUTHORIZE,
            OAUTH2_TOKEN,
        ),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AL-KO from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = aiohttp_client.async_get_clientsession(hass)
    oauth_session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    client = ConfigEntryAlkoClient(session, oauth_session)

    client_id = hass.data[DOMAIN][CONF_CLIENT_ID]
    alko = Alko(client, client_id)

    async def async_update_data() -> Alko:
        """Fetch data from Alko."""
        try:
            async with async_timeout.timeout(60):
                await alko.get_devices()
            return alko
        except AlkoAuthenticationException as exception:
            raise ConfigEntryAuthFailed from exception
        except (AlkoException, ClientResponseError) as exception:
            raise UpdateFailed(exception) from exception

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="alko_coordinator",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=120),
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AlkoEntity(CoordinatorEntity):
    """Defines a base AL-KO entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        key: str,
        name: str,
    ) -> None:
        """Initialize the AL-KO entity."""
        super().__init__(coordinator)
        self._key = key
        self._name = name
        self._device_name = device.thingAttributes.thingName
        self._device_type = device.thingAttributes.thingType
        self._device_model = device.thingAttributes.thingModel
        self._firmware_main = device.thingAttributes.firmwareMain
        self._update_device = coordinator.data.update_device

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self._key

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def device(self) -> AlkoDevice:
        """Get the AL-KO Device."""
        return self.coordinator.data.devices_dict[self._device_name]


class AlkoDeviceEntity(AlkoEntity):
    """Defines an AL-KO device entity."""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this AL-KO instance."""
        return {
            "identifiers": {(DOMAIN, self._device_name)},
            "manufacturer": "AL-KO",
            "model": self._device_model,
            "name": self._device_name,
            "device_type": self._device_type,
            "sw_version": self._firmware_main,
        }
