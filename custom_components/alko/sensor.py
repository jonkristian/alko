"""Support for AL-KO sensor platform."""
import logging
from datetime import datetime, timedelta

from pyalko.objects.device import AlkoDevice, Thingstate

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_TIMESTAMP,
    DEVICE_CLASS_BATTERY,
    PERCENTAGE
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import AlkoDeviceEntity
from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up the AL-KO sensor platform based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        cls_list = []
        if device.thingState.state.reported.operationState:
            cls_list.append(AlkoOperationSensor)
            cls_list.append(AlkoErrorSensor)
            cls_list.append(AlkoBladeSensor)
        if device.thingState.state.reported.batteryLevel:
            cls_list.append(AlkoBatterySensor)
        for cls in cls_list:
            entities.append(
                cls(
                    coordinator,
                    device,
                )
            )

    async_add_entities(entities, True)


class AlkoSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        key: str,
        name: str,
        device_class: str = None,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize AL-KO sensor."""
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement

        super().__init__(coordinator, device, key, name)

    @property
    def device_class(self) -> str:
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement


class AlkoOperationSensor(AlkoSensor):
    """Defines an AL-KO State sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "substate": None,
            "situation": None,
        }

        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_operation_state",
            "Operation State",
            unit_of_measurement,
        )

        self._attr_extra_state_attributes["substate"] = self.device.thingState.state.reported.operationSubState
        self._attr_extra_state_attributes["situation"] = self.device.thingState.state.reported.operationSituation

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.operationState


class AlkoErrorSensor(AlkoSensor):
    """Defines an AL-KO Error sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "type": None,
            "description": None,
        }

        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_operation_error",
            "Operation Error",
            unit_of_measurement,
        )

        if self.device.thingState.state.reported.operationError.code is not None:
            self._attr_extra_state_attributes["type"] = self.device.thingState.state.reported.operationError.type
            self._attr_extra_state_attributes["description"] = self.device.thingState.state.reported.operationError.description

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.operationError.code


class AlkoBladeSensor(AlkoSensor):
    """Defines an AL-KO Blade sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "operation_time": None,
        }

        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_blade_remaining",
            "Remaining Blade Life",
            unit_of_measurement,
        )

        self._attr_extra_state_attributes["operation_time"] = self.device.thingState.state.reported.operationTimeBlade

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.remainingBladeLifetime


class AlkoBatterySensor(AlkoSensor):
    """Defines an AL-KO Battery sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize AL-KO sensor."""

        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_battery_level",
            "Battery Level",
            DEVICE_CLASS_BATTERY,
            "%",
        )

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.batteryLevel
