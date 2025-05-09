"""Support for AL-KO number platform."""
import logging
from typing import Any

from pyalko import Alko
from pyalko.objects.device import AlkoDevice
from pyalko.exceptions import AlkoException

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO number platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        # Check if device supports rain sensitivity
        if device.thingState.state.reported.rainSensitivity is not None:
            entities.append(
                AlkoRainSensitivity(coordinator, device)
            )
        # Check if device supports rain delay
        if device.thingState.state.reported.rainDelay is not None:
            entities.append(
                AlkoRainDelay(coordinator, device)
            )
        # Check if device supports frost threshold
        if device.thingState.state.reported.frostThreshold is not None:
            entities.append(
                AlkoFrostThreshold(coordinator, device)
            )
        # Check if device supports frost delay
        if device.thingState.state.reported.frostDelay is not None:
            entities.append(
                AlkoFrostDelay(coordinator, device)
            )

    async_add_entities(entities, True)


class AlkoRainSensitivity(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO rain sensitivity number."""

    _attr_icon = "mdi:water-percent"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO rain sensitivity number."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_rain_sensitivity",
            "Rain Sensitivity",
        )

    @property
    def native_value(self) -> float:
        """Return the current rain sensitivity value."""
        return float(self.device.thingState.state.reported.rainSensitivity)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._update_device(self.device, rainSensitivity=int(value))
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()


class AlkoRainDelay(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO rain delay number."""

    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 240  # Assuming 4 hours max, adjust if needed
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO rain delay number."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_rain_delay",
            "Rain Delay",
        )

    @property
    def native_value(self) -> float:
        """Return the current rain delay value."""
        return float(self.device.thingState.state.reported.rainDelay)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._update_device(self.device, rainDelay=int(value))
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()


class AlkoFrostThreshold(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO frost threshold number."""

    _attr_icon = "mdi:thermometer-snowflake"
    _attr_native_min_value = -10  # Assuming minimum temperature, adjust if needed
    _attr_native_max_value = 10   # Assuming maximum temperature, adjust if needed
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO frost threshold number."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_frost_threshold",
            "Frost Threshold",
        )

    @property
    def native_value(self) -> float:
        """Return the current frost threshold value."""
        return float(self.device.thingState.state.reported.frostThreshold)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._update_device(self.device, frostThreshold=int(value))
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()


class AlkoFrostDelay(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO frost delay number."""

    _attr_icon = "mdi:timer-snowflake"
    _attr_native_min_value = 0
    _attr_native_max_value = 240  # Assuming 4 hours max, adjust if needed
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO frost delay number."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_frost_delay",
            "Frost Delay",
        )

    @property
    def native_value(self) -> float:
        """Return the current frost delay value."""
        return float(self.device.thingState.state.reported.frostDelay)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self._update_device(self.device, frostDelay=int(value))
        except AlkoException as exception:
            _LOGGER.error(exception)
        await self.coordinator.async_refresh()