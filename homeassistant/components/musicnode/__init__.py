"""The MusicNode integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .musicnode_api import MusicnodeApi
from .service import async_setup_services

LOGGER = logging.getLogger(__name__)

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MusicNode from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TO DO 1. Create API instance
    # TO DO 2. Validate the API connection (and authentication)
    # TO DO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, DOMAIN)},
        manufacturer="Louis",
        name="Musicnode",
        model="Musicnode",
        sw_version="1.0",
    )

    api = MusicnodeApi(entry.data["host"], entry.data["port"])
    hass.data[DOMAIN]["API"] = api

    await hass.async_add_executor_job(
        api.async_send_screen_update, "Hassio Connected", ""
    )

    # Services
    await async_setup_services(hass)

    # Platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
