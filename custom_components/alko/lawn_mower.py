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
from homeassistant.helpers import entity_registry as er

from . import AlkoDeviceEntity
from .const import DOMAIN
from .sensor import AlkoOperationSensor

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
            device.thingName,  # unique_id
            device.thingAttributes.thingModel,  # name from device model
        )
        self._state = self._get_state_from_device()

    def _get_state_from_device(self) -> str:
        """Get state from device."""
        if not self.device.thingState.state.reported.isConnected:
            return "unavailable"

        if self.device.thingState.state.reported.operationError.code != 999:
            return "error"

        state = self.device.thingState.state.reported.operationState
        substate = self.device.thingState.state.reported.operationSubState
        situation = self.device.thingState.state.reported.operationSituation

        # Check if mower is locked
        if substate == "LOCKED_PIN" or situation == "OPERATION_NOT_PERMITTED_LOCKED":
            return "error"

        if state == "IDLE":
            return "paused"
        if state == "WORKING":
            return "mowing"
        if state == "HOMING":
            return "returning"
        if state == "CHARGING":
            return "docked"
        if state == "IDLE_BASE_STATION":
            return "docked"

        return "unknown"

    @property
    def state(self) -> str:
        """Return the state of the mower."""
        return self._state

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._state = self._get_state_from_device()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._state = self._get_state_from_device()
        self.async_schedule_update_ha_state()

    async def async_start_mowing(self) -> None:
        """Start mowing."""
        try:
            # Check if mower is locked
            if (self.device.thingState.state.reported.operationSubState == "LOCKED_PIN" or
                    self.device.thingState.state.reported.operationSituation == "OPERATION_NOT_PERMITTED_LOCKED"):
                _LOGGER.error("Cannot start mower: Mower is locked")
                return

            # Make API call first
            await self._update_device(self.device, operationState="WORKING")
            await self.coordinator.async_refresh()

            # Update state last
            self._state = "mowing"
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to start mowing: %s", exception)

    async def async_pause(self) -> None:
        """Pause mowing."""
        try:
            # Make API call first
            await self._update_device(self.device, operationState="IDLE")
            await self.coordinator.async_refresh()

            # Update state last
            self._state = "paused"
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to pause mowing: %s", exception)

    async def async_dock(self) -> None:
        """Return to charging station."""
        try:
            # Make API call first
            await self._update_device(self.device, operationState="HOMING")
            await self.coordinator.async_refresh()

            # Update state last
            self._state = "returning"
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to dock mower: %s", exception)
