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
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _reported(device: AlkoDevice) -> dict:
    """Return raw reported state attributes dict for a device."""
    return device.thingState.state.reported.attributes


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO sensor platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        attrs = _reported(device)
        if not attrs:
            continue

        # ── Mower sensors ───────────────────────────────────────────────────
        if "operationState" in attrs:
            entities.append(AlkoOperationSensor(coordinator, device))
        if "operationError" in attrs:
            entities.append(AlkoErrorSensor(coordinator, device))
        if "operationTimeBlade" in attrs:
            entities.append(AlkoBladeSensor(coordinator, device))
        if "nextOperation" in attrs:
            entities.append(AlkoNextOperationSensor(coordinator, device))

        # ── Universal sensors (mowers + chargers) ───────────────────────────
        if "batteryLevel" in attrs:
            entities.append(AlkoBatterySensor(coordinator, device))
        if "rssi" in attrs:
            entities.append(AlkoRssiSensor(coordinator, device))

        # ── Smart charger sensors ────────────────────────────────────────────
        if "charger" in attrs:
            charger = attrs["charger"]

            entities.append(AlkoChargerInputVoltageSensor(coordinator, device))
            entities.append(AlkoChargerInputFrequencySensor(coordinator, device))
            entities.append(AlkoChargerErrorSensor(coordinator, device))

            for slot in (1, 2):
                slot_key = f"battery_{slot}"
                if slot_key in charger:
                    entities += [
                        AlkoChargerBatteryInserted(coordinator, device, slot),
                        AlkoChargerBatteryPercentage(coordinator, device, slot),
                        AlkoChargerBatteryVoltage(coordinator, device, slot),
                        AlkoChargerBatteryCurrent(coordinator, device, slot),
                        AlkoChargerBatteryTemperature(coordinator, device, slot),
                        AlkoChargerBatteryTotalCharges(coordinator, device, slot),
                    ]

        if "operationTime" in attrs:
            entities.append(AlkoChargerOperationTimeSensor(coordinator, device))

    async_add_entities(entities, True)


# ════════════════════════════════════════════════════════════════════════════
# Mower sensors (unchanged from original)
# ════════════════════════════════════════════════════════════════════════════

class AlkoSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO sensor."""

    def __init__(self, coordinator, device, key, name,
                 device_class=None, unit_of_measurement=None):
        """Initialize AL-KO sensor."""
        self._device_class = device_class
        self._unit_of_measurement = unit_of_measurement
        super().__init__(coordinator, device, key, name)

    @property
    def device_class(self):
        return self._device_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        return self.device.thingState.state.reported.operationState


class AlkoOperationSensor(AlkoSensor):
    """Defines an AL-KO State sensor."""

    def __init__(self, coordinator, device):
        self._attr_extra_state_attributes = {"substate": None, "situation": None}
        super().__init__(coordinator, device, "operation_state", "Operation State")
        reported = self.device.thingState.state.reported
        self._attr_extra_state_attributes["substate"] = reported.operationSubState
        self._attr_extra_state_attributes["situation"] = reported.operationSituation

    @property
    def state(self):
        return self.device.thingState.state.reported.operationState


class AlkoErrorSensor(AlkoSensor):
    """Defines an AL-KO Error sensor."""

    _attr_translation_key = "error"

    def __init__(self, coordinator, device):
        self._attr_extra_state_attributes = {"type": None, "description": None}
        super().__init__(coordinator, device, "operation_error", "Operation Error")
        err = self.device.thingState.state.reported.operationError
        if err.code is not None:
            self._attr_extra_state_attributes["type"] = err.type

    @property
    def state(self):
        return str(self.device.thingState.state.reported.operationError.code)


class AlkoBladeSensor(AlkoSensor):
    """Defines an AL-KO Blade sensor."""

    _attr_icon = "mdi:fan"
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device):
        self._attr_extra_state_attributes = {"operation_time": None}
        super().__init__(coordinator, device, "blade_remaining", "Remaining Blade Life",
                         None, UnitOfTime.HOURS)
        self._attr_extra_state_attributes["operation_time"] = (
            self.device.thingState.state.reported.operationTimeBlade
        )

    @property
    def state(self):
        return self.device.thingState.state.reported.remainingBladeLifetime


class AlkoBatterySensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO Battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Battery Level"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "battery_level", "Battery Level")

    @property
    def state(self):
        return self.device.thingState.state.reported.batteryLevel


class AlkoNextOperationSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO Next Operation sensor."""

    _attr_icon = "mdi:calendar-range"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "next_operation", "Next Operation")
        self._attr_extra_state_attributes = {
            "duration": None, "narrow_passage": None, "margin_mode": None,
        }

    @property
    def state(self):
        current_time = dt_util.now()
        today = current_time.strftime("%A").lower()
        mowing_windows = self.device.thingState.state.reported.mowingWindows
        is_day_cancelled = self.device.thingState.state.reported.situationFlags.dayCancelled
        next_operation = None
        next_window = None
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        today_index = days.index(today)

        if hasattr(self.device.thingState.state.reported, "manualMowing"):
            manual_mowing = self.device.thingState.state.reported.manualMowing
            if manual_mowing is not None and manual_mowing.activityMode:
                manual_time = current_time.replace(
                    hour=manual_mowing.startHour, minute=manual_mowing.startMinute,
                    second=0, microsecond=0
                )
                if manual_time > current_time:
                    next_operation = manual_time
                    next_window = manual_mowing

        if next_operation is None:
            for i in range(7):
                day = days[(today_index + i) % 7]
                if i == 0 and is_day_cancelled:
                    continue
                if hasattr(mowing_windows, day):
                    windows = getattr(mowing_windows, day)
                    for window_num in ['window_1', 'window_2']:
                        if hasattr(windows, window_num):
                            window = getattr(windows, window_num)
                            if window.activityMode:
                                window_time = current_time.replace(
                                    hour=window.startHour, minute=window.startMinute,
                                    second=0, microsecond=0
                                ) + timedelta(days=i)
                                if window_time > current_time and (
                                    next_operation is None or window_time < next_operation
                                ):
                                    next_operation = window_time
                                    next_window = window

        if next_operation:
            next_operation = dt_util.as_local(next_operation)
            if next_window:
                self._attr_extra_state_attributes["duration"] = next_window.duration
                self._attr_extra_state_attributes["margin_mode"] = next_window.marginMode
                self._attr_extra_state_attributes["narrow_passage"] = next_window.narrowPassageMode
            return next_operation.isoformat()

        self._attr_extra_state_attributes.update(
            {"duration": None, "narrow_passage": None, "margin_mode": None}
        )
        return "N/A"


class AlkoRssiSensor(AlkoDeviceEntity, SensorEntity):
    """Defines an AL-KO RSSI sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "RSSI"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "rssi", "RSSI")

    @property
    def state(self):
        return self.device.thingState.state.reported.rssi


# ════════════════════════════════════════════════════════════════════════════
# Smart charger sensors
# ════════════════════════════════════════════════════════════════════════════

class AlkoChargerInputVoltageSensor(AlkoDeviceEntity, SensorEntity):
    """Input voltage of the charger (mV → V)."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_input_voltage", "Input Voltage")

    @property
    def state(self):
        mv = _reported(self.device).get("charger", {}).get("inputVoltage", 0)
        return round(mv / 1000, 1)


class AlkoChargerInputFrequencySensor(AlkoDeviceEntity, SensorEntity):
    """Input frequency of the charger."""

    _attr_device_class = SensorDeviceClass.FREQUENCY
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_input_frequency", "Input Frequency")

    @property
    def state(self):
        return _reported(self.device).get("charger", {}).get("inputFrequency")


class AlkoChargerErrorSensor(AlkoDeviceEntity, SensorEntity):
    """Error code of the charger (0 = no error)."""

    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_error", "Charger Error")

    @property
    def state(self):
        return _reported(self.device).get("charger", {}).get("error")


class AlkoChargerOperationTimeSensor(AlkoDeviceEntity, SensorEntity):
    """Total operation time of the charger in seconds."""

    _attr_icon = "mdi:timer-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_operation_time", "Operation Time")

    @property
    def state(self):
        return (
            _reported(self.device)
            .get("operationTime", {})
            .get("operation", {})
            .get("total")
        )


# ── Per-slot battery sensors ─────────────────────────────────────────────────

class _AlkoChargerBatteryBase(AlkoDeviceEntity, SensorEntity):
    """Base class for per-slot charger battery sensors."""

    def __init__(self, coordinator, device, slot: int, key_suffix: str, name_suffix: str):
        self._slot = slot
        super().__init__(
            coordinator, device,
            f"charger_battery_{slot}_{key_suffix}",
            f"Battery {slot} {name_suffix}",
        )

    def _slot_data(self) -> dict:
        return (
            _reported(self.device)
            .get("charger", {})
            .get(f"battery_{self._slot}", {})
        )

    def _stats(self) -> dict:
        return self._slot_data().get("stats", {})


class AlkoChargerBatteryInserted(_AlkoChargerBatteryBase):
    """Whether a battery is inserted in this slot (shown as sensor for easy dashboard use)."""

    _attr_icon = "mdi:battery-outline"

    def __init__(self, coordinator, device, slot):
        # We expose inserted state as a sensor (True/False) rather than binary_sensor
        # so it appears alongside the other battery sensors in the same device card.
        super().__init__(coordinator, device, slot, "inserted", "Inserted")

    @property
    def state(self):
        return self._slot_data().get("inserted")


class AlkoChargerBatteryPercentage(_AlkoChargerBatteryBase):
    """Battery level percentage for this slot."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "percentage", "Level")

    @property
    def state(self):
        return self._stats().get("percentage")


class AlkoChargerBatteryVoltage(_AlkoChargerBatteryBase):
    """Battery voltage for this slot (mV → V)."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "voltage", "Voltage")

    @property
    def state(self):
        mv = self._stats().get("voltage", 0)
        return round(mv / 1000, 2) if mv else 0


class AlkoChargerBatteryCurrent(_AlkoChargerBatteryBase):
    """Charging current for this slot (mA → A)."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "current", "Current")

    @property
    def state(self):
        ma = self._stats().get("current", 0)
        return round(ma / 1000, 2) if ma else 0


class AlkoChargerBatteryTemperature(_AlkoChargerBatteryBase):
    """Battery temperature for this slot."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "temperature", "Temperature")

    @property
    def state(self):
        return self._stats().get("temperature")


class AlkoChargerBatteryTotalCharges(_AlkoChargerBatteryBase):
    """Total number of charging sessions for this slot."""

    _attr_icon = "mdi:battery-sync-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "total_charges", "Total Charges")

    @property
    def state(self):
        return self._stats().get("charging", {}).get("total")
