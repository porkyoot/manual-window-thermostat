

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: 'HomeAssistant', entry: 'ConfigEntry') -> bool:
	"""Set up manual_window_thermostat from a config entry."""
	hass.async_create_task(
		hass.config_entries.async_forward_entry_setups(entry, ["climate"])
	)
	return True
