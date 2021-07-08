"""Support for AL-KO switch platform."""
import logging

from pyalko.objects.device import AlkoDevice
from pyalko.exceptions import AlkoException

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import AlkoDeviceEntity
from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the AL-KO select platform based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        entities.append(
            AlkoSelect(
                coordinator, device
            )
        )

    async_add_entities(entities, True)


class AlkoSelect(AlkoDeviceEntity, SelectEntity):
    """Defines an AL-KO select."""

    _attr_icon = "mdi:playlist-play"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice
    ) -> None:
        """Initialize AL-KO select."""

        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_control_mode",
            "Control Mode",
        )

        self._attr_options = ['WORKING', 'HOMING']

    @property
    def current_option(self) -> str:
        """Return current option."""
        return self.device.thingState.state.reported.operationState

    async def async_select_option(self, option: str) -> None:
        """Change select option."""
        try:
            await self._update_device(
                self.device, f"operationState={option}"
            )
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()
