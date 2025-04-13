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
        # Check if device supports rain detection
        if device.thingState.state.reported.situationFlags.rainDetected is not None:
            entities.append(
                AlkoRainDetectedSensor(coordinator, device)
            )
        # Check if device supports rain allows mowing status
        if device.thingState.state.reported.situationFlags.rainAllowsMowing is not None:
            entities.append(
                AlkoRainAllowsMowingSensor(coordinator, device)
            )
        # Check if device supports frost detection
        if device.thingState.state.reported.situationFlags.frostDetected is not None:
            entities.append(
                AlkoFrostDetectedSensor(coordinator, device)
            )
        # Check if device supports frost allows mowing status
        if device.thingState.state.reported.situationFlags.frostAllowsMowing is not None:
            entities.append(
                AlkoFrostAllowsMowingSensor(coordinator, device)
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
            f"{device.thingName}_rain_detected",
            "Rain Detected",
        )

    @property
    def is_on(self) -> bool:
        """Return true if rain is detected."""
        return self.device.thingState.state.reported.situationFlags.rainDetected


class AlkoRainAllowsMowingSensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO rain allows mowing binary sensor."""

    _attr_icon = "mdi:robot-mower"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO rain allows mowing sensor."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_rain_allows_mowing",
            "Mowing Allowed (Rain)",
        )

    @property
    def is_on(self) -> bool:
        """Return true if mowing is allowed despite rain."""
        return self.device.thingState.state.reported.situationFlags.rainAllowsMowing


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
            f"{device.thingName}_frost_detected",
            "Frost Detected",
        )

    @property
    def is_on(self) -> bool:
        """Return true if frost is detected."""
        return self.device.thingState.state.reported.situationFlags.frostDetected


class AlkoFrostAllowsMowingSensor(AlkoDeviceEntity, BinarySensorEntity):
    """Defines an AL-KO frost allows mowing binary sensor."""

    _attr_icon = "mdi:robot-mower"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO frost allows mowing sensor."""
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_frost_allows_mowing",
            "Mowing Allowed (Frost)",
        )

    @property
    def is_on(self) -> bool:
        """Return true if mowing is allowed despite frost."""
        return self.device.thingState.state.reported.situationFlags.frostAllowsMowing