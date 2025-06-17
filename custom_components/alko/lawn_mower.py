"""Support for AL-KO mower platform."""
import logging
from typing import Any
import json

import voluptuous as vol

from pyalko import Alko
from pyalko.exceptions import AlkoException
from pyalko.objects.device import AlkoDevice

from homeassistant.components.lawn_mower import (
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

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

    # Register services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        "update_mowing_window",
        {
            vol.Required("day"): str,
            vol.Required("window_number"): int,
            vol.Required("start_hour"): int,
            vol.Required("start_minute"): int,
            vol.Required("duration"): int,
            vol.Required("type"): str,
            vol.Optional("entry_point"): int,
        },
        "async_update_mowing_window",
    )
    platform.async_register_entity_service(
        "start_manual_mowing",
        {
            vol.Required("start_hour"): int,
            vol.Required("start_minute"): int,
            vol.Required("duration"): int,
            vol.Required("type"): str,
            vol.Required("entry_point"): int,
        },
        "async_start_manual_mowing",
    )
    platform.async_register_entity_service(
        "stop_manual_mowing",
        {},
        "async_stop_manual_mowing",
    )
    platform.async_register_entity_service(
        "show_device_state",
        {},
        "async_show_device_state",
    )


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
            "mower",
            "Mower",
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
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, operationState="WORKING", rtc=rtc)
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
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, operationState="IDLE", rtc=rtc)
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
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, operationState="HOMING", rtc=rtc)
            await self.coordinator.async_refresh()

            # Update state last
            self._state = "returning"
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to dock mower: %s", exception)

    async def async_update_mowing_window(
        self,
        day: str,
        window_number: int,
        start_hour: int,
        start_minute: int,
        duration: int,
        type: str,
        entry_point: int | None = None,
    ) -> None:
        """Update mowing window."""
        try:
            window = f"window_{window_number}"
            window_data = {
                "activityMode": type != "deactivated",
                "marginMode": type == "first_mow_border_then_area",
                "narrowPassageMode": type == "narrow_passage",
                "startHour": start_hour,
                "startMinute": start_minute,
                "duration": duration,
            }

            if entry_point is not None:
                window_data["entryPoint"] = entry_point

            window_update = {
                day: {
                    window: window_data
                }
            }

            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, mowingWindows=window_update, rtc=rtc)
            await self.coordinator.async_refresh()
        except AlkoException as exception:
            _LOGGER.error("Failed to update mowing window: %s", exception)

    async def async_start_manual_mowing(
        self,
        start_hour: int,
        start_minute: int,
        duration: int,
        type: str,
        entry_point: int,
    ) -> None:
        """Start manual mowing."""
        try:
            manual_mowing = {
                "activityMode": True,
                "marginMode": type == "first_mow_border_then_area",
                "narrowPassageMode": type == "narrow_passage",
                "startHour": start_hour,
                "startMinute": start_minute,
                "duration": duration,
                "entryPoint": entry_point,
            }

            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, manualMowing=manual_mowing, rtc=rtc)
            await self.coordinator.async_refresh()
        except AlkoException as exception:
            _LOGGER.error("Failed to start manual mowing: %s", exception)

    async def async_stop_manual_mowing(self) -> None:
        """Stop manual mowing."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(
                self.device,
                manualMowing={"activityMode": False},
                operationState="HOMING",
                rtc=rtc
            )
            await self.coordinator.async_refresh()
        except AlkoException as exception:
            _LOGGER.error("Failed to stop manual mowing: %s", exception)

    async def async_show_device_state(self) -> None:
        """Show the current device state as a notification."""
        try:
            state_data = self.device.thingState.state.reported.__dict__
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "AL-KO Device State",
                    "message": f"```json\n{json.dumps(state_data, indent=2)}\n```",
                },
            )
            _LOGGER.info("Device state shown in notification")
        except Exception as e:
            _LOGGER.error("Failed to show device state: %s", e)
