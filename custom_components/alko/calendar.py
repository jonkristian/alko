"""Support for AL-KO calendar platform."""
import logging
from datetime import datetime, timedelta

from pyalko import Alko
from pyalko.objects.device import AlkoDevice

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import AlkoDeviceEntity
from .const import DOMAIN

DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AL-KO calendar platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        if device.thingState.state.reported is not None:
            if hasattr(device.thingState.state.reported, "mowingWindows"):
                entities.append(
                    AlkoMowingCalendar(
                        coordinator,
                        device,
                    )
                )

    async_add_entities(entities, True)


class AlkoMowingCalendar(AlkoDeviceEntity, CalendarEntity):
    """Defines an AL-KO mowing calendar."""

    _attr_icon = "mdi:calendar-clock"
    _attr_name = "Mowing Schedule"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device: AlkoDevice,
    ) -> None:
        """Initialize AL-KO mowing calendar."""
        super().__init__(
            coordinator,
            device,
            "mowing_calendar",
            "Mowing Schedule",
        )
        self._events: list[CalendarEvent] = []

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self._events:
            return None

        now = dt_util.now()

        # First try to find a current event
        for event in self._events:
            if event.start <= now < event.end:
                return event

        # If no current event, return the next upcoming one
        for event in self._events:
            if event.start > now:
                return event

        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []

        if not hasattr(self.device.thingState.state.reported, "mowingWindows"):
            return events

        mowing_windows = self.device.thingState.state.reported.mowingWindows
        is_day_cancelled = self.device.thingState.state.reported.situationFlags.dayCancelled

        # Get current date and ensure we start from today
        today = dt_util.now().date()
        current_date = today

        # Generate events for the next 7 days
        for _ in range(7):
            day_name = DAYS_OF_WEEK[current_date.weekday()]

            # Get the day's windows using getattr
            day_windows = getattr(mowing_windows, day_name, None)
            if day_windows is not None:
                # Get window attributes
                window_1 = getattr(day_windows, "window_1", None)
                window_2 = getattr(day_windows, "window_2", None)

                for window_name, window in [("Window 1", window_1), ("Window 2", window_2)]:
                    if window is not None:
                        # Check if window is active
                        activity_mode = getattr(window, "activityMode", False)
                        is_window_active = activity_mode and not (
                            current_date == today and is_day_cancelled)

                        # Only add active windows
                        if is_window_active:
                            # Create event start time
                            start_time = datetime.combine(
                                current_date,
                                datetime.min.time().replace(
                                    hour=getattr(window, "startHour", 0),
                                    minute=getattr(window, "startMinute", 0),
                                ),
                            )
                            # Convert to local timezone
                            start_time = dt_util.as_local(start_time)

                            # Calculate end time based on duration (in minutes)
                            end_time = start_time + \
                                timedelta(minutes=getattr(
                                    window, "duration", 0))

                            # Only add events that fall within the requested range
                            if start_time <= end_date and end_time >= start_date:
                                # Create a concise summary with mutually exclusive modes
                                if getattr(window, 'marginMode', False):
                                    summary = "Mowing Border & Area"
                                elif getattr(window, 'narrowPassageMode', False):
                                    summary = "Mowing Narrow Passage"
                                else:
                                    summary = "Mowing"

                                events.append(
                                    CalendarEvent(
                                        summary=summary,
                                        start=start_time,
                                        end=end_time,
                                    )
                                )

            # Add manual mowing event if it exists and it's today
            if current_date == today and hasattr(self.device.thingState.state.reported, "manualMowing"):
                manual_mowing = self.device.thingState.state.reported.manualMowing
                if manual_mowing is not None and getattr(manual_mowing, "activityMode", False):
                    # Create event start time
                    start_time = datetime.combine(
                        current_date,
                        datetime.min.time().replace(
                            hour=getattr(manual_mowing, "startHour", 0),
                            minute=getattr(manual_mowing, "startMinute", 0),
                        ),
                    )
                    # Convert to local timezone
                    start_time = dt_util.as_local(start_time)

                    # Calculate end time based on duration (in minutes)
                    end_time = start_time + \
                        timedelta(minutes=getattr(
                            manual_mowing, "duration", 0))

                    # Only add if it falls within the requested range
                    if start_time <= end_date and end_time >= start_date:
                        # Create a concise summary for manual mowing
                        if getattr(manual_mowing, 'marginMode', False):
                            summary = "Manual Mowing Border & Area"
                        elif getattr(manual_mowing, 'narrowPassageMode', False):
                            summary = "Manual Mowing Narrow Passage"
                        else:
                            summary = "Manual Mowing"

                        events.append(
                            CalendarEvent(
                                summary=summary,
                                start=start_time,
                                end=end_time,
                            )
                        )

            # Move to next day
            current_date += timedelta(days=1)

        self._events = sorted(events, key=lambda x: x.start)
        return events
