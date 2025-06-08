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

from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    ConfigEntryAlkoClient,
    AlkoLocalOAuth2Implementation,
    OAuth2SessionAlko
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.LAWN_MOWER,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ALKO from a config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )
    if not isinstance(implementation, AlkoLocalOAuth2Implementation):
        raise TypeError(
            "Unexpected auth implementation; can't find oauth client id")

    session = aiohttp_client.async_get_clientsession(hass)
    oauth_session = OAuth2SessionAlko(hass, entry, implementation)

    client = ConfigEntryAlkoClient(session, oauth_session)
    client_id = implementation.client_id
    alko = Alko(client, client_id)

    async def async_update_data() -> Alko:
        """Fetch data from Alko."""
        try:
            async with async_timeout.timeout(60):
                await alko.get_devices()
                _LOGGER.debug("Fetched devices: %s", repr(alko.devices))
            return alko
        except AlkoAuthenticationException as exception:
            raise ConfigEntryAuthFailed from exception
        except (AlkoException, ClientResponseError) as exception:
            raise UpdateFailed(exception) from exception

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="alko_coordinator",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=60),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AlkoEntity(CoordinatorEntity[DataUpdateCoordinator[Alko]]):
    """Defines a base AL-KO entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[Alko],
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
        self._hardware_main = device.thingAttributes.hardwareVersionMain
        self._serial_number = device.thingAttributes.serialNumber
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
            "sw_version": self._firmware_main,
            "hw_version": self._hardware_main,
            "serial_number": self._serial_number,
        }
