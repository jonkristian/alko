"""Support for AL-KO number platform."""
import logging

from pyalko import Alko
from pyalko.exceptions import AlkoException
from pyalko.objects.device import AlkoDevice

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import AlkoDeviceEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _reported(device: AlkoDevice) -> dict:
    """Return raw reported state attributes dict for a device."""
    return device.thingState.state.reported.attributes


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO number platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        attrs = _reported(device)
        if not attrs:
            continue

        # ── Mower number entities ─────────────────────────────────────────────
        if "rainSensitivity" in attrs:
            entities.append(AlkoRainSensitivity(coordinator, device))
        if "rainDelay" in attrs:
            entities.append(AlkoRainDelay(coordinator, device))
        if "frostThreshold" in attrs:
            entities.append(AlkoFrostThreshold(coordinator, device))
        if "frostDelay" in attrs:
            entities.append(AlkoFrostDelay(coordinator, device))

    async_add_entities(entities, True)


# ════════════════════════════════════════════════════════════════════════════
# Mower number entities (unchanged from original)
# ════════════════════════════════════════════════════════════════════════════

class AlkoRainSensitivity(AlkoDeviceEntity, NumberEntity):
    _attr_icon = "mdi:water-percent"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "rain_sensitivity", "Rain Sensitivity")

    @property
    def native_value(self):
        return float(self.device.thingState.state.reported.rainSensitivity)

    async def async_set_native_value(self, value: float):
        try:
            await self._update_device(self.device, rainSensitivity=int(value))
            await self.coordinator.async_refresh()
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to set rain sensitivity: %s", exc)


class AlkoRainDelay(AlkoDeviceEntity, NumberEntity):
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 0
    _attr_native_max_value = 240
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "rain_delay", "Rain Delay")

    @property
    def native_value(self):
        return float(self.device.thingState.state.reported.rainDelay)

    async def async_set_native_value(self, value: float):
        try:
            await self._update_device(self.device, rainDelay=int(value))
            await self.coordinator.async_refresh()
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to set rain delay: %s", exc)


class AlkoFrostThreshold(AlkoDeviceEntity, NumberEntity):
    _attr_icon = "mdi:snowflake-thermometer"
    _attr_native_min_value = -10
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "frost_threshold", "Frost Threshold")

    @property
    def native_value(self):
        return float(self.device.thingState.state.reported.frostThreshold)

    async def async_set_native_value(self, value: float):
        try:
            await self._update_device(self.device, frostThreshold=int(value))
            await self.coordinator.async_refresh()
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to set frost threshold: %s", exc)


class AlkoFrostDelay(AlkoDeviceEntity, NumberEntity):
    _attr_icon = "mdi:timer"
    _attr_native_min_value = 0
    _attr_native_max_value = 240
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "frost_delay", "Frost Delay")

    @property
    def native_value(self):
        return float(self.device.thingState.state.reported.frostDelay)

    async def async_set_native_value(self, value: float):
        try:
            await self._update_device(self.device, frostDelay=int(value))
            await self.coordinator.async_refresh()
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to set frost delay: %s", exc)
