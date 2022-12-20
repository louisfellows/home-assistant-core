"""Provides device triggers for MusicNode."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant

# from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from . import DOMAIN

LOGGER = logging.getLogger(__name__)

CONF_MUSICNODE_EVENT = "musicnode_event"

TRIGGER_TYPES = {
    "back_button_press",
    "play_button_press",
    "forward_button_press",
    "up_button_press",
    "down_button_press",
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device triggers for MusicNode devices."""
    triggers = []

    # device_registry = dr.async_get(hass)
    # device = device_registry.devices[device_id]

    base_trigger = {
        CONF_PLATFORM: "device",
        CONF_DEVICE_ID: device_id,
        CONF_DOMAIN: DOMAIN,
    }
    for trigger in TRIGGER_TYPES:
        triggers.append({**base_trigger, CONF_TYPE: trigger})

    return triggers


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""

    # LOGGER.info(f"Trigger: {config}")
    # LOGGER.info(f"action: {action}")
    # LOGGER.info(f"trigger_info: {trigger_info}")

    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: CONF_MUSICNODE_EVENT,
            event_trigger.CONF_EVENT_DATA: {
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )

    # LOGGER.info(f"event_config: {event_config}")

    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
