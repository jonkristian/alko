"""Support for AL-KO sensor platform."""
import logging
from datetime import timedelta

from pyalko import Alko
from pyalko.objects.device import AlkoDevice

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE
)
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
    """Set up the AL-KO sensor platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        cls_list = []
        if device.thingState.state.reported is not None:
            # Check if device supports operation state
            if hasattr(device.thingState.state.reported, "operationState"):
                cls_list.append(AlkoOperationSensor)

            # Check if device supports operation error
            if hasattr(device.thingState.state.reported, "operationError"):
                cls_list.append(AlkoErrorSensor)

            # Check if device supports blade remaining
            if hasattr(device.thingState.state.reported, "operationTimeBlade"):
                cls_list.append(AlkoBladeSensor)

            # Check if device supports battery level
            if hasattr(device.thingState.state.reported, "batteryLevel"):
                cls_list.append(AlkoBatterySensor)

            # Check if device supports next operation
            if hasattr(device.thingState.state.reported, "nextOperation"):
                cls_list.append(AlkoNextOperationSensor)

            # Check if device supports RSSI
            if hasattr(device.thingState.state.reported, "rssi"):
                cls_list.append(AlkoRssiSensor)

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

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.operationState


class AlkoOperationSensor(AlkoSensor):
    """Defines an AL-KO State sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "substate": None,
            "situation": None,
        }

        super().__init__(
            coordinator,
            device,
            "operation_state",
            "Operation State",
        )

        self._attr_extra_state_attributes["substate"] = self.device.thingState.state.reported.operationSubState
        self._attr_extra_state_attributes["situation"] = self.device.thingState.state.reported.operationSituation

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.operationState


class AlkoErrorSensor(AlkoSensor):
    """Defines an AL-KO Error sensor."""

    _attr_translation_key = "error"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "type": None,
            "description": None,
        }

        super().__init__(
            coordinator,
            device,
            "operation_error",
            "Operation Error",
        )

        if self.device.thingState.state.reported.operationError.code is not None:
            self._attr_extra_state_attributes["type"] = self.device.thingState.state.reported.operationError.type

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return str(self.device.thingState.state.reported.operationError.code)


class AlkoBladeSensor(AlkoSensor):
    """Defines an AL-KO Blade sensor."""

    _attr_icon = "mdi:fan"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO sensor."""

        self._attr_extra_state_attributes = {
            "operation_time": None,
        }

        super().__init__(
            coordinator,
            device,
            "blade_remaining",
            "Remaining Blade Life",
            None,
            "h",
        )

        self._attr_extra_state_attributes["operation_time"] = self.device.thingState.state.reported.operationTimeBlade

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.remainingBladeLifetime


class AlkoBatterySensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO Battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Battery Level"

    def __init__(self, coordinator, device):
        super().__init__(
            coordinator,
            device,
            "battery_level",
            "Battery Level",
        )

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.batteryLevel


class AlkoNextOperationSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO Next Operation sensor."""

    _attr_icon = "mdi:calendar-range"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, device):
        super().__init__(
            coordinator,
            device,
            "next_operation",
            "Next Operation"
        )
        self._attr_extra_state_attributes = {
            "duration": None,
            "narrow_passage": None,
            "margin_mode": None,
        }

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        current_time = dt_util.now()
        today = current_time.strftime("%A").lower()
        mowing_windows = self.device.thingState.state.reported.mowingWindows
        is_day_cancelled = self.device.thingState.state.reported.situationFlags.dayCancelled

        # Find next operation time
        next_operation = None
        next_window = None
        days = ['monday', 'tuesday', 'wednesday',
                'thursday', 'friday', 'saturday', 'sunday']
        today_index = days.index(today)

        # Check today and next 6 days
        for i in range(7):
            day = days[(today_index + i) % 7]
            # Skip today if day is cancelled
            if i == 0 and is_day_cancelled:
                continue
            if hasattr(mowing_windows, day):
                windows = getattr(mowing_windows, day)
                for window_num in ['window_1', 'window_2']:
                    if hasattr(windows, window_num):
                        window = getattr(windows, window_num)
                        if window.activityMode:
                            window_time = current_time.replace(
                                hour=window.startHour,
                                minute=window.startMinute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=i)
                            if window_time > current_time and (next_operation is None or window_time < next_operation):
                                next_operation = window_time
                                next_window = window

        if next_operation:
            next_operation = dt_util.as_local(next_operation)

            # Update extra state attributes
            if next_window:
                self._attr_extra_state_attributes["duration"] = next_window.duration
                self._attr_extra_state_attributes["margin_mode"] = next_window.marginMode
                self._attr_extra_state_attributes["narrow_passage"] = next_window.narrowPassageMode

            # Return ISO 8601 formatted timestamp
            return next_operation.isoformat()

        # Reset attributes if no next operation
        self._attr_extra_state_attributes.update({
            "duration": None,
            "narrow_passage": None,
            "margin_mode": None,
        })
        return "N/A"


class AlkoRssiSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO RSSI sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "RSSI"

    def __init__(self, coordinator, device):
        super().__init__(
            coordinator,
            device,
            "rssi",
            "RSSI"
        )

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.rssi
