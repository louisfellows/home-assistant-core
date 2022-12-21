"""Musicnode Services."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    CONF_ENTITY_ID,
    CONF_FRIENDLY_ENTITY,
    CONF_NEW_ALBUM,
    CONF_NEW_ARTIST,
    CONF_NEW_STATE,
    CONF_NEW_TITLE,
    CONF_OLD_ALBUM,
    CONF_OLD_ARTIST,
    CONF_OLD_STATE,
    CONF_OLD_TITLE,
    DOMAIN,
    SERVICES,
)

LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Service handler setup."""

    async def service_handler(call: ServiceCall) -> None:
        """Handle service call."""

        api = hass.data[DOMAIN]["API"]

        request = {
            "entityId": call.data[CONF_ENTITY_ID],
            "friendlyName": call.data[CONF_FRIENDLY_ENTITY],
            "oldState": {
                "state": call.data[CONF_OLD_STATE],
                "mediaTitle": call.data[CONF_OLD_TITLE],
                "mediaArtist": call.data[CONF_OLD_ARTIST],
                "mediaAlbum": call.data[CONF_OLD_ALBUM],
            },
            "newState": {
                "state": call.data[CONF_NEW_STATE],
                "mediaTitle": call.data[CONF_NEW_TITLE],
                "mediaArtist": call.data[CONF_NEW_ARTIST],
                "mediaAlbum": call.data[CONF_NEW_ALBUM],
            },
        }

        await hass.async_add_executor_job(api.async_send_media_update, request)

    for service in SERVICES:
        hass.services.async_register(DOMAIN, service, service_handler)
