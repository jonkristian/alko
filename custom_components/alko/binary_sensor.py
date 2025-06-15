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


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO binary sensor platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        cls_list = []
        if hasattr(device.thingState.state.reported, "situationFlags"):
            # Check if device supports rain detection
            if hasattr(device.thingState.state.reported.situationFlags, "rainDetected"):
                cls_list.append(AlkoRainDetectedSensor)
            # Check if device supports frost detection
            if hasattr(device.thingState.state.reported.situationFlags, "frostDetected"):
                cls_list.append(AlkoFrostDetectedSensor)
            # Check if device supports charger contact status
            if hasattr(device.thingState.state.reported.situationFlags, "chargerContact"):
                cls_list.append(AlkoChargerContactBinarySensor)
            # Check if device supports day cancelled status
            if hasattr(device.thingState.state.reported.situationFlags, "dayCancelled"):
                cls_list.append(AlkoDayCancelledBinarySensor)
            # Check if device supports robot is active status
            if hasattr(device.thingState.state.reported.situationFlags, "robotIsActive"):
                cls_list.append(AlkoRobotIsActiveBinarySensor)
            # Check if device supports is connected status
            if hasattr(device.thingState.state.reported, "isConnected"):
                cls_list.append(AlkoIsConnectedBinarySensor)
            # Check if device supports user interaction status
            if hasattr(device.thingState.state.reported.situationFlags, "userInteraction"):
                cls_list.append(AlkoUserInteractionBinarySensor)

        for cls in cls_list:
            entities.append(
                cls(
                    coordinator,
                    device,
                )
            )

    async_add_entities(entities, True)


class AlkoRainDetectedSensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO rain detected binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOISTURE
    _attr_icon = "mdi:water"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO rain detected sensor."""
        super().__init__(
            coordinator,
            device,
            "rain_detected",
            "Rain Detected",
        )

    @property
    def is_on(self) -> bool:
        """Return true if rain is detected."""
        return self.device.thingState.state.reported.situationFlags.rainDetected


class AlkoFrostDetectedSensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO frost detected binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.COLD
    _attr_icon = "mdi:snowflake"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO frost detected sensor."""
        super().__init__(
            coordinator,
            device,
            "frost_detected",
            "Frost Detected",
        )

    @property
    def is_on(self) -> bool:
        """Return true if frost is detected."""
        return self.device.thingState.state.reported.situationFlags.frostDetected


class AlkoChargerContactBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO Charger Contact binary sensor."""

    _attr_icon = "mdi:power-plug"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO binary sensor."""
        super().__init__(
            coordinator,
            device,
            "charger_contact",
            "Charger Contact",
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.device.thingState.state.reported.situationFlags.chargerContact


class AlkoDayCancelledBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO Day Cancelled binary sensor."""

    _attr_icon = "mdi:calendar-remove"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO binary sensor."""
        super().__init__(
            coordinator,
            device,
            "day_cancelled",
            "Day Cancelled",
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.device.thingState.state.reported.situationFlags.dayCancelled


class AlkoRobotIsActiveBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO Robot Is Active binary sensor."""

    _attr_icon = "mdi:robot-mower-outline"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO robot is active sensor."""
        super().__init__(
            coordinator,
            device,
            "is_active",
            "Is Active",
        )

    @property
    def is_on(self) -> bool:
        """Return true if robot is active."""
        return self.device.thingState.state.reported.situationFlags.robotIsActive


class AlkoIsConnectedBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO Is Connected sensor."""

    _attr_icon = "mdi:signal"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO is connected binary sensor."""
        super().__init__(
            coordinator,
            device,
            "is_connected",
            "Is Connected"
        )

    @property
    def state(self) -> bool:
        """Return the state of the sensor."""
        return self.device.thingState.state.reported.isConnected


class AlkoUserInteractionBinarySensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO User Interaction sensor."""

    _attr_icon = "mdi:hand-wave"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO user interaction binary sensor."""
        super().__init__(
            coordinator,
            device,
            "user_interaction",
            "User Interaction"
        )

    @property
    def is_on(self) -> bool:
        """Return true if user interaction is required."""
        # Get the reported state
        reported = self.device.thingState.state.reported

        # Check if the device is locked (PIN required)
        if reported.operationSubState == "LOCKED_PIN":
            return True

        # Check for any error code other than 999
        if reported.operationError.code != 999:
            return True

        # Check for critical issues that require attention
        flags = reported.situationFlags
        if (
            flags.batteryFailure or
            flags.chargerFailure or
            flags.bladeService or
            flags.wheelMotorTemperatureHigh or
            flags.stopAfterIssue or
            not flags.operationPermitted
        ):
            return True

        # Check operation situation for critical states
        if reported.operationSituation == "OPERATION_NOT_PERMITTED_LOCKED":
            return True

        return False
