"""Support for AL-KO number platform."""
import logging

from pyalko import Alko
from pyalko.exceptions import AlkoException
from pyalko.objects.device import AlkoDevice

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
        cls_list = []
        if device.thingState.state.reported is not None:
            # Check if device supports rain sensitivity
            if hasattr(device.thingState.state.reported, "rainSensitivity"):
                cls_list.append(AlkoRainSensitivity)
            # Check if device supports rain delay
            if hasattr(device.thingState.state.reported, "rainDelay"):
                cls_list.append(AlkoRainDelay)
            # Check if device supports frost threshold
            if hasattr(device.thingState.state.reported, "frostThreshold"):
                cls_list.append(AlkoFrostThreshold)
            # Check if device supports frost delay
            if hasattr(device.thingState.state.reported, "frostDelay"):
                cls_list.append(AlkoFrostDelay)

        for cls in cls_list:
            entities.append(
                cls(
                    coordinator,
                    device,
                )
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
            "rain_sensitivity",
            "Rain Sensitivity",
        )

    @property
    def native_value(self) -> float:
        """Return the current rain sensitivity value."""
        return float(self.device.thingState.state.reported.rainSensitivity)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            # Make API call first
            await self._update_device(self.device, rainSensitivity=int(value))
            await self.coordinator.async_refresh()

            # Update state immediately
            self._value = value
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to set value: %s", exception)


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
            "rain_delay",
            "Rain Delay",
        )

    @property
    def native_value(self) -> float:
        """Return the current rain delay value."""
        return float(self.device.thingState.state.reported.rainDelay)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            # Make API call first
            await self._update_device(self.device, rainDelay=int(value))
            await self.coordinator.async_refresh()

            # Update state immediately
            self._value = value
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to set value: %s", exception)


class AlkoFrostThreshold(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO frost threshold number."""

    _attr_icon = "mdi:snowflake-thermometer"
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
            "frost_threshold",
            "Frost Threshold",
        )

    @property
    def native_value(self) -> float:
        """Return the current frost threshold value."""
        return float(self.device.thingState.state.reported.frostThreshold)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            # Make API call first
            await self._update_device(self.device, frostThreshold=int(value))
            await self.coordinator.async_refresh()

            # Update state immediately
            self._value = value
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to set value: %s", exception)


class AlkoFrostDelay(AlkoDeviceEntity, NumberEntity):
    """Defines an AL-KO frost delay number."""

    _attr_icon = "mdi:timer"
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
            "frost_delay",
            "Frost Delay",
        )

    @property
    def native_value(self) -> float:
        """Return the current frost delay value."""
        return float(self.device.thingState.state.reported.frostDelay)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            # Make API call first
            await self._update_device(self.device, frostDelay=int(value))
            await self.coordinator.async_refresh()

            # Update state immediately
            self._value = value
            self.async_write_ha_state()
        except AlkoException as exception:
            _LOGGER.error("Failed to set value: %s", exception)
