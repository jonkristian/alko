"""Support for AL-KO switch platform."""
import logging
from typing import Any

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

_STORAGE_LIMIT = 60   # % — winter / long-term storage charge limit
_FULL_LIMIT    = 100  # % — normal full charge


def _reported(device: AlkoDevice) -> dict:
    """Return raw reported state attributes dict for a device."""
    return device.thingState.state.reported.attributes


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO switch platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        attrs = _reported(device)
        if not attrs:
            continue

        # ── Mower switches ───────────────────────────────────────────────────
        if "ecoMode" in attrs:
            entities.append(AlkoEcoModeSwitch(coordinator, device))
        if "rainSensor" in attrs:
            entities.append(AlkoRainSensorSwitch(coordinator, device))
        if "frostSensor" in attrs:
            entities.append(AlkoFrostSensorSwitch(coordinator, device))
        if "dayCancelled" in attrs.get("situationFlags", {}):
            entities.append(AlkoCancelTodaySwitch(coordinator, device))

        # ── Smart charger switches ────────────────────────────────────────────
        charger = attrs.get("charger", {})
        if "ecoMode" in charger.get("settings", {}):
            entities.append(AlkoChargerEcoModeSwitch(coordinator, device))
        for slot in (1, 2):
            if "percentage_charging_limit" in charger.get(f"battery_{slot}", {}).get("settings", {}):
                entities.append(AlkoChargerStorageModeSwitch(coordinator, device, slot))

    async_add_entities(entities, True)


# ════════════════════════════════════════════════════════════════════════════
# Mower switches (unchanged from original)
# ════════════════════════════════════════════════════════════════════════════

class AlkoEcoModeSwitch(AlkoDeviceEntity, SwitchEntity):
    _attr_icon = "mdi:tree"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "eco_mode", "Eco Mode")
        self._state = self.device.thingState.state.reported.ecoMode

    @property
    def is_on(self):
        return self._state

    def _handle_coordinator_update(self):
        new_state = self.device.thingState.state.reported.ecoMode
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, ecoMode=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)

    async def async_turn_on(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, ecoMode=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)


class AlkoRainSensorSwitch(AlkoDeviceEntity, SwitchEntity):
    _attr_icon = "mdi:weather-rainy"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "rain_sensor", "Rain Sensor")
        self._state = self.device.thingState.state.reported.rainSensor

    @property
    def is_on(self):
        return self._state

    def _handle_coordinator_update(self):
        new_state = self.device.thingState.state.reported.rainSensor
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, rainSensor=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)

    async def async_turn_on(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, rainSensor=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)


class AlkoFrostSensorSwitch(AlkoDeviceEntity, SwitchEntity):
    _attr_icon = "mdi:snowflake"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "frost_sensor", "Frost Sensor")
        self._state = self.device.thingState.state.reported.frostSensor

    @property
    def is_on(self):
        return self._state

    def _handle_coordinator_update(self):
        new_state = self.device.thingState.state.reported.frostSensor
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, frostSensor=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)

    async def async_turn_on(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, frostSensor=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)


class AlkoCancelTodaySwitch(AlkoDeviceEntity, SwitchEntity):
    _attr_icon = "mdi:calendar-remove"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "cancel_today", "Paused for Today")
        self._state = self.device.thingState.state.reported.situationFlags.dayCancelled

    @property
    def is_on(self):
        return self._state

    def _handle_coordinator_update(self):
        new_state = self.device.thingState.state.reported.situationFlags.dayCancelled
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, dayCancelled=False, rtc=rtc)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)

    async def async_turn_on(self, **kwargs: Any):
        try:
            rtc = dt_util.now().strftime("%Y-%m-%dT%H:%M:%S")
            await self._update_device(self.device, dayCancelled=True, rtc=rtc)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error(exc)


# ════════════════════════════════════════════════════════════════════════════
# Smart charger switches
# ════════════════════════════════════════════════════════════════════════════

class AlkoChargerEcoModeSwitch(AlkoDeviceEntity, SwitchEntity):
    """Eco mode — reduced charging current (~1.5 A instead of ~3 A)."""

    _attr_icon = "mdi:leaf"

    def __init__(self, coordinator, device):
        super().__init__(coordinator, device, "charger_eco_mode", "Eco Mode")
        self._state = self._get_state()

    def _get_state(self) -> bool:
        return bool(
            _reported(self.device)
            .get("charger", {})
            .get("settings", {})
            .get("ecoMode", False)
        )

    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        eco_ma = _reported(self.device).get("charger", {}).get("settings", {}).get("ecoCurrent", 0)
        return {"eco_current_a": round(eco_ma / 1000, 2)}

    def _handle_coordinator_update(self):
        new_state = self._get_state()
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any):
        try:
            await self._update_device(self.device, charger={"settings": {"ecoMode": False}})
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to disable charger eco mode: %s", exc)

    async def async_turn_on(self, **kwargs: Any):
        try:
            await self._update_device(self.device, charger={"settings": {"ecoMode": True}})
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to enable charger eco mode: %s", exc)


class AlkoChargerStorageModeSwitch(AlkoDeviceEntity, SwitchEntity):
    """Winter / long-term storage mode for one battery slot.

    ON  → charging limit set to 60 % (recommended for storage)
    OFF → charging limit set to 100 % (normal full charge)
    """

    _attr_icon = "mdi:snowflake-variant"

    def __init__(self, coordinator, device, slot: int):
        self._slot = slot
        super().__init__(
            coordinator, device,
            f"charger_battery_{slot}_storage_mode",
            f"Battery {slot} Storage Mode",
        )
        self._state = self._get_state()

    def _get_limit(self) -> int:
        return (
            _reported(self.device)
            .get("charger", {})
            .get(f"battery_{self._slot}", {})
            .get("settings", {})
            .get("percentage_charging_limit", _FULL_LIMIT)
        )

    def _get_state(self) -> bool:
        """Return True when storage mode is active (limit == 60 %)."""
        return self._get_limit() == _STORAGE_LIMIT

    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def extra_state_attributes(self) -> dict:
        return {"charging_limit_pct": self._get_limit()}

    def _handle_coordinator_update(self):
        new_state = self._get_state()
        if new_state != self._state:
            self._state = new_state
        super()._handle_coordinator_update()

    async def _set_limit(self, limit: int) -> None:
        await self._update_device(
            self.device,
            charger={
                f"battery_{self._slot}": {
                    "settings": {"percentage_charging_limit": limit}
                }
            },
        )

    async def async_turn_on(self, **kwargs: Any):
        """Enable storage mode — set limit to 60 %."""
        try:
            await self._set_limit(_STORAGE_LIMIT)
            self._state = True
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to enable storage mode for battery %d: %s", self._slot, exc)

    async def async_turn_off(self, **kwargs: Any):
        """Disable storage mode — restore full charge (100 %)."""
        try:
            await self._set_limit(_FULL_LIMIT)
            self._state = False
            self.async_write_ha_state()
        except AlkoException as exc:
            _LOGGER.error("Failed to disable storage mode for battery %d: %s", self._slot, exc)
