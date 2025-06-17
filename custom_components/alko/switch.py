"""Support for AL-KO switch platform."""
import logging
from typing import Any
from datetime import datetime

from pyalko import Alko
from pyalko.objects.device import AlkoDevice
from pyalko.exceptions import AlkoException

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO switch platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        cls_list = []
        if device.thingState.state.reported is not None:
            if hasattr(device.thingState.state.reported, "ecoMode"):
                cls_list.append(AlkoEcoModeSwitch)
            if hasattr(device.thingState.state.reported, "rainSensor"):
                cls_list.append(AlkoRainSensorSwitch)
            if hasattr(device.thingState.state.reported, "frostSensor"):
                cls_list.append(AlkoFrostSensorSwitch)
            if hasattr(device.thingState.state.reported.situationFlags, "dayCancelled"):
                cls_list.append(AlkoCancelTodaySwitch)

        for cls in cls_list:
            entities.append(
                cls(
                    coordinator,
                    device,
                )
            )

    async_add_entities(entities, True)


class AlkoEcoModeSwitch(AlkoDeviceEntity, SwitchEntity):
    """Defines an AL-KO switch."""

    _attr_icon = "mdi:tree"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice
    ) -> None:
        """Initialize AL-KO switch."""
        super().__init__(
            coordinator,
            device,
            "eco_mode",
            "Eco Mode",
        )
        self._state = self.device.thingState.state.reported.ecoMode

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_state = self.device.thingState.state.reported.ecoMode
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off eco mode switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, ecoMode=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on eco mode switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, ecoMode=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)


class AlkoRainSensorSwitch(AlkoDeviceEntity, SwitchEntity):
    """Defines an AL-KO switch."""

    _attr_icon = "mdi:weather-rainy"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice
    ) -> None:
        """Initialize AL-KO switch."""
        super().__init__(
            coordinator,
            device,
            "rain_sensor",
            "Rain Sensor",
        )
        self._state = self.device.thingState.state.reported.rainSensor

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_state = self.device.thingState.state.reported.rainSensor
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off rain sensor switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, rainSensor=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on rain sensor switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, rainSensor=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)


class AlkoFrostSensorSwitch(AlkoDeviceEntity, SwitchEntity):
    """Defines an AL-KO frost sensor switch."""

    _attr_icon = "mdi:snowflake"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice
    ) -> None:
        """Initialize AL-KO frost sensor switch."""
        super().__init__(
            coordinator,
            device,
            "frost_sensor",
            "Frost Sensor",
        )
        self._state = self.device.thingState.state.reported.frostSensor

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_state = self.device.thingState.state.reported.frostSensor
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the frost sensor."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, frostSensor=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the frost sensor."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, frostSensor=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)


class AlkoCancelTodaySwitch(AlkoDeviceEntity, SwitchEntity):
    """Defines an AL-KO cancel today switch."""

    _attr_icon = "mdi:calendar-remove"
    _attr_name = "Paused for Today"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice
    ) -> None:
        """Initialize AL-KO cancel today switch."""
        super().__init__(
            coordinator,
            device,
            "cancel_today",
            "Paused for Today"
        )
        self._state = self.device.thingState.state.reported.situationFlags.dayCancelled

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._state

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_state = self.device.thingState.state.reported.situationFlags.dayCancelled
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off cancel today switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, dayCancelled=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on cancel today switch."""
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, dayCancelled=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error(exception)
