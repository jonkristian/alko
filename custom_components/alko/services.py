"""Support for AL-KO services."""
import logging
from datetime import datetime

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util
from pyalko.exceptions import AlkoException

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_handle_update_mowing_window(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle updating a mowing window."""
    try:
        # Get the device from the target
        entity_id = call.data["target"]["entity_id"]
        registry = er.async_get(hass)
        entity = registry.async_get(entity_id)
        if not entity:
            _LOGGER.error("Entity not found in registry: %s", entity_id)
            return

        # Get the device from the device registry
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(entity.device_id)
        if not device_entry:
            _LOGGER.error(
                "Device not found in registry for entity: %s", entity_id)
            return

        # Get the device identifier and find the device
        device_identifier = next(iter(device_entry.identifiers))[1]
        coordinator = hass.data[DOMAIN][next(iter(hass.data[DOMAIN].keys()))]
        device = next(
            (dev for dev in coordinator.data.devices if dev.thingName == device_identifier), None)
        if not device:
            _LOGGER.error(
                "Device not found with thingName: %s", device_identifier)
            return

        # Get current windows
        current_windows = device.thingState.state.reported.mowingWindows
        new_windows = {}

        # Copy existing windows structure
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            day_windows = getattr(current_windows, day, None)
            if day_windows is not None:
                new_windows[day] = {}
                for window_num in ["window_1", "window_2"]:
                    window = getattr(day_windows, window_num, None)
                    if window is not None:
                        new_windows[day][window_num] = {
                            "activityMode": getattr(window, "activityMode", False),
                            "marginMode": getattr(window, "marginMode", False),
                            "startHour": getattr(window, "startHour", 0),
                            "startMinute": getattr(window, "startMinute", 0),
                            "duration": getattr(window, "duration", 0),
                            "entryPoint": getattr(window, "entryPoint", 0),
                            "narrowPassageMode": getattr(window, "narrowPassageMode", False),
                        }

        # Update the specified window
        day = call.data["day"]
        window = f"window_{call.data['window_number']}"
        mowing_type = call.data["type"]

        if day not in new_windows:
            new_windows[day] = {}

        new_windows[day][window] = {
            "activityMode": mowing_type != "deactivated",
            "marginMode": mowing_type == "first_mow_border_then_area",
            "startHour": call.data["start_hour"],
            "startMinute": call.data["start_minute"],
            "duration": call.data["duration"],
            "entryPoint": call.data["entry_point"],
            "narrowPassageMode": mowing_type == "narrow_passage",
        }

        # Update device and refresh coordinator
        await coordinator.data.update_device(device, mowingWindows=new_windows)
        await coordinator.async_refresh()

    except AlkoException as exception:
        _LOGGER.error("Failed to update mowing window: %s", exception)


async def async_handle_start_manual_mowing(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle starting a manual mowing operation."""
    try:
        # Get the device from the target
        entity_id = call.data["target"]["entity_id"]
        registry = er.async_get(hass)
        entity = registry.async_get(entity_id)
        if not entity:
            _LOGGER.error("Entity not found in registry: %s", entity_id)
            return

        # Get the device from the device registry
        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(entity.device_id)
        if not device_entry:
            _LOGGER.error(
                "Device not found in registry for entity: %s", entity_id)
            return

        # Get the device identifier and find the device
        device_identifier = next(iter(device_entry.identifiers))[1]
        coordinator = hass.data[DOMAIN][next(iter(hass.data[DOMAIN].keys()))]
        device = next(
            (dev for dev in coordinator.data.devices if dev.thingName == device_identifier), None)
        if not device:
            _LOGGER.error(
                "Device not found with thingName: %s", device_identifier)
            return

        # Get current time
        current_time = dt_util.now()

        # Create manual mowing configuration
        manual_mowing = {
            "activityMode": True,
            "marginMode": call.data["type"] == "first_mow_border_then_area",
            "narrowPassageMode": call.data["type"] == "narrow_passage",
            "startHour": current_time.hour,
            "startMinute": current_time.minute,
            "duration": call.data["duration"],
            "entryPoint": call.data["entry_point"]
        }

        # Update device and refresh coordinator
        await coordinator.data.update_device(device, manualMowing=manual_mowing)
        await coordinator.async_refresh()

    except AlkoException as exception:
        _LOGGER.error("Failed to start manual mowing: %s", exception)
