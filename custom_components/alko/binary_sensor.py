"""Support for AL-KO binary sensor platform."""
import logging

from pyalko import Alko
from pyalko.objects.device import AlkoDevice

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _reported(device: AlkoDevice) -> dict:
    """Return raw reported state attributes dict for a device."""
    return device.thingState.state.reported.attributes


def _situation_flags(device: AlkoDevice) -> dict:
    """Return raw situationFlags dict for a device."""
    return _reported(device).get("situationFlags", {})


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO binary sensor platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        attrs = _reported(device)
        if not attrs:
            continue

        flags = _situation_flags(device)

        # ── Universal: available for mowers and chargers ─────────────────────
        if "isConnected" in attrs:
            entities.append(AlkoIsConnectedBinarySensor(coordinator, device))

        # ── Mower situationFlags sensors ─────────────────────────────────────
        if "rainDetected" in flags:
            entities.append(AlkoRainDetectedSensor(coordinator, device))
        if "frostDetected" in flags:
            entities.append(AlkoFrostDetectedSensor(coordinator, device))
        if "chargerContact" in flags:
            entities.append(AlkoChargerContactBinarySensor(coordinator, device))
        if "dayCancelled" in flags:
            entities.append(AlkoDayCancelledBinarySensor(coordinator, device))
        if "robotIsActive" in flags:
            entities.append(AlkoRobotIsActiveBinarySensor(coordinator, device))
        if "userInteraction" in flags:
            entities.append(AlkoUserInteractionBinarySensor(coordinator, device))

        # ── Smart charger: per-slot battery sensors ───────────────────────────
        if "charger" in attrs:
            for slot in (1, 2):
                if f"battery_{slot}" in attrs["charger"]:
                    entities.append(AlkoChargerBatteryInserted(coordinator, device, slot))
                    entities.append(AlkoChargerBatteryCharging(coordinator, device, slot))

    async_add_entities(entities, True)


# ════════════════════════════════════════════════════════════════════════════
# Mower binary sensors (unchanged from original)
# ════════════════════════════════════════════════════════════════════════════

class AlkoRainDetectedSensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:water"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "rain_detected", "Rain Detected")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.situationFlags.rainDetected


class AlkoFrostDetectedSensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.COLD
    _attr_icon = "mdi:snowflake"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "frost_detected", "Frost Detected")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.situationFlags.frostDetected


class AlkoChargerContactBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_icon = "mdi:power-plug"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_contact", "Charger Contact")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.situationFlags.chargerContact


class AlkoDayCancelledBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_icon = "mdi:calendar-remove"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "day_cancelled", "Day Cancelled")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.situationFlags.dayCancelled


class AlkoRobotIsActiveBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_icon = "mdi:robot-mower-outline"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "is_active", "Is Active")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.situationFlags.robotIsActive


class AlkoIsConnectedBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_icon = "mdi:signal"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "is_connected", "Is Connected")

    @property
    def is_on(self):
        return self.device.thingState.state.reported.isConnected


class AlkoUserInteractionBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    _attr_icon = "mdi:hand-wave"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "user_interaction", "User Interaction")

    @property
    def is_on(self):
        reported = self.device.thingState.state.reported
        if reported.operationSubState == "LOCKED_PIN":
            return True
        if reported.operationError.code != 999:
            return True
        flags = reported.situationFlags
        if (
            flags.batteryFailure or flags.chargerFailure or flags.bladeService or
            flags.wheelMotorTemperatureHigh or flags.stopAfterIssue or
            not flags.operationPermitted
        ):
            return True
        if reported.operationSituation == "OPERATION_NOT_PERMITTED_LOCKED":
            return True
        return False


# ════════════════════════════════════════════════════════════════════════════
# Smart charger binary sensors
# ════════════════════════════════════════════════════════════════════════════

class _AlkoChargerBatteryBinaryBase(AlkoDeviceEntity, BinarySensorEntity):
    """Base class for per-slot charger battery binary sensors."""

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


class AlkoChargerBatteryInserted(_AlkoChargerBatteryBinaryBase):
    """Whether a battery is physically inserted in this charger slot."""

    _attr_device_class = BinarySensorDeviceClass.PLUG
    _attr_icon = "mdi:battery-outline"

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "inserted", "Inserted")

    @property
    def is_on(self) -> bool:
        return bool(self._slot_data().get("inserted"))


class AlkoChargerBatteryCharging(_AlkoChargerBatteryBinaryBase):
    """Whether the battery in this slot is currently charging."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_icon = "mdi:battery-charging"

    def __init__(self, coordinator, device, slot):
        super().__init__(coordinator, device, slot, "charging", "Charging")

    @property
    def is_on(self) -> bool:
        return bool(self._slot_data().get("charging"))
