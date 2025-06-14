"""Support for AL-KO button platform."""
import logging
from typing import Any

from pyalko import Alko
from pyalko.objects.device import AlkoDevice
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
            # Add reset blade life button if supported
            if hasattr(device.thingState.state.reported, "resetBladesService"):
                cls_list.append(AlkoResetBladeLifeButton)
            if hasattr(device.thingState.state.reported, "manualMarginMowing"):
                cls_list.append(AlkoEdgeCuttingButton)

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
            f"{device.thingName}_reset_blade_life",
            "Reset Blade Life"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._update_device(self.device, resetBladesService=True)
        except AlkoException as exception:
            _LOGGER.error("Failed to reset blade life: %s", exception)
        await self.coordinator.async_refresh()


class AlkoEdgeCuttingButton(AlkoDeviceEntity, ButtonEntity):
    """Defines a button to start edge cutting."""

    _attr_name = "Start Edge Cutting"
    _attr_icon = "mdi:border-all"

    def __init__(self, coordinator, device):
        super().__init__(
            coordinator,
            device,
            f"{device.thingName}_edge_cutting",
            "Start Edge Cutting"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            # First set edge cutting mode
            await self._update_device(self.device, manualMarginMowing=True)
            # Then start the mower
            await self._update_device(self.device, operationState="WORKING")
        except AlkoException as exception:
            _LOGGER.error("Failed to start edge cutting: %s", exception)
        await self.coordinator.async_refresh()
