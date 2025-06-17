"""Support for AL-KO button platform."""
import logging

from pyalko import Alko
from pyalko.exceptions import AlkoException

from homeassistant.components.button import ButtonEntity
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
    """Set up the AL-KO button platform based on a config entry."""
    coordinator: DataUpdateCoordinator[Alko] = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for device in coordinator.data.devices:
        cls_list = []
        if device.thingState.state.reported is not None:
            if hasattr(device.thingState.state.reported, "resetBladesService"):
                cls_list.append(AlkoResetBladeLifeButton)

        for cls in cls_list:
            entities.append(
                cls(
                    coordinator,
                    device,
                )
            )

    async_add_entities(entities, True)


class AlkoResetBladeLifeButton(AlkoDeviceEntity, ButtonEntity):
    """Defines a button to reset blade life."""

    _attr_name = "Reset Blade Life"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator, device):
        super().__init__(
            coordinator,
            device,
            "reset_blade_life",
            "Reset Blade Life"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._update_device(self.device, resetBladesService=True)
        except AlkoException as exception:
            _LOGGER.error("Failed to reset blade life: %s", exception)
        await self.coordinator.async_refresh()
