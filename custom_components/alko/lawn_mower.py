"""Support for AL-KO mower platform."""
import logging
from typing import Any

from pyalko import Alko
from pyalko.objects.device import AlkoDevice
from pyalko.exceptions import AlkoException

from homeassistant.components.lawn_mower import (
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO mower platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        # Only add mower entities for devices that have operation state
        if device.thingState.state.reported.operationState is not None:
            entities.append(
                AlkoMower(coordinator, device)
            )

    async_add_entities(entities, True)


class AlkoMower(AlkoDeviceEntity, LawnMowerEntity):
    """Defines an AL-KO mower."""

    _attr_icon = "mdi:robot-mower"
    _attr_supported_features = (
        LawnMowerEntityFeature.START_MOWING
        | LawnMowerEntityFeature.PAUSE
        | LawnMowerEntityFeature.DOCK
    )

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO mower."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_mower",
            "Mower",
        )

    @property
    def state(self) -> str:
        """Return the state of the mower."""
        if not self.device.thingState.state.reported.isConnected:
            return "unavailable"

        if self.device.thingState.state.reported.operationError.code != 999:
            return "error"

        state = self.device.thingState.state.reported.operationState
        if state == "IDLE":
            return "docked"
        if state == "WORKING":
            return "mowing"
        if state == "HOMING":
            return "returning"
        if state == "CHARGING":
            return "docked"
        if state == "IDLE_BASE_STATION":
            return "docked"

        return "unknown"

    async def async_start_mowing(self) -> None:
        """Start mowing."""
        try:
            await self._update_device(self.device, operationState="WORKING")
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()

    async def async_pause(self) -> None:
        """Pause mowing."""
        try:
            await self._update_device(self.device, operationState="IDLE")
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()

    async def async_dock(self) -> None:
        """Return to charging station."""
        try:
            await self._update_device(self.device, operationState="HOMING")
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()
