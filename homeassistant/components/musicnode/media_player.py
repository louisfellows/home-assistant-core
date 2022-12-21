"""Support to interact with a Music Player Daemon."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.media_player import (  # ATTR_APP_ID,; ATTR_APP_NAME,; ATTR_INPUT_SOURCE_LIST,; ATTR_MEDIA_ALBUM_ARTIST,; ATTR_MEDIA_CHANNEL,; ATTR_MEDIA_EPISODE,; ATTR_MEDIA_PLAYLIST,; ATTR_MEDIA_SEASON,; ATTR_MEDIA_SERIES_TITLE,; ATTR_MEDIA_TRACK,; ATTR_SOUND_MODE_LIST,; DEVICE_CLASSES_SCHEMA,; PLATFORM_SCHEMA,; BrowseMedia,; async_process_play_media_url,
    ATTR_INPUT_SOURCE,
    ATTR_MEDIA_ALBUM_NAME,
    ATTR_MEDIA_ARTIST,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_DURATION,
    ATTR_MEDIA_POSITION,
    ATTR_MEDIA_POSITION_UPDATED_AT,
    ATTR_MEDIA_REPEAT,
    ATTR_MEDIA_SEEK_POSITION,
    ATTR_MEDIA_SHUFFLE,
    ATTR_MEDIA_TITLE,
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_VOLUME_MUTED,
    ATTR_SOUND_MODE,
    DOMAIN,
    SERVICE_CLEAR_PLAYLIST,
    SERVICE_PLAY_MEDIA,
    SERVICE_SELECT_SOUND_MODE,
    SERVICE_SELECT_SOURCE,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    RepeatMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (  # ATTR_SUPPORTED_FEATURES,; CONF_DEVICE_CLASS,; CONF_HOST,; CONF_NAME,; CONF_PASSWORD,; CONF_PORT,; CONF_STATE,; CONF_STATE_TEMPLATE,; CONF_UNIQUE_ID,; EVENT_HOMEASSISTANT_START,; STATE_UNAVAILABLE,; STATE_UNKNOWN,
    ATTR_ENTITY_ID,
    ATTR_ENTITY_PICTURE,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_PLAY,
    SERVICE_MEDIA_PLAY_PAUSE,
    SERVICE_MEDIA_PREVIOUS_TRACK,
    SERVICE_MEDIA_SEEK,
    SERVICE_MEDIA_STOP,
    SERVICE_REPEAT_SET,
    SERVICE_SHUFFLE_SET,
    SERVICE_TOGGLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_SET,
    SERVICE_VOLUME_UP,
    STATE_ON,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

SUPPORT_MPD = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.CLEAR_PLAYLIST
    | MediaPlayerEntityFeature.REPEAT_SET
    | MediaPlayerEntityFeature.SHUFFLE_SET
    | MediaPlayerEntityFeature.SEEK
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
)

STATES_ORDER = [
    MediaPlayerState.OFF,
    MediaPlayerState.IDLE,
    MediaPlayerState.STANDBY,
    MediaPlayerState.ON,
    MediaPlayerState.PAUSED,
    MediaPlayerState.BUFFERING,
    MediaPlayerState.PLAYING,
]
STATES_ORDER_LOOKUP = {state: idx for idx, state in enumerate(STATES_ORDER)}
STATES_ORDER_IDLE = STATES_ORDER_LOOKUP[MediaPlayerState.IDLE]

STRING_TO_STATE = {
    "off": MediaPlayerState.OFF,
    "idle": MediaPlayerState.IDLE,
    "standby": MediaPlayerState.STANDBY,
    "on": MediaPlayerState.ON,
    "paused": MediaPlayerState.PAUSED,
    "buffering": MediaPlayerState.BUFFERING,
    "playing": MediaPlayerState.PLAYING,
}

VOLUME_RANGES = {
    "media_player.spotify_louis": [75, 100],
    "media_player.musicnode": [0, 25],
}


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the platform."""
    # host = config.get(CONF_HOST)
    entities = ["media_player.spotify_louis", "media_player.musicnode"]
    async_add_entities([CombinedMediaDevice(hass, entities)], True)


class CombinedMediaDevice(MediaPlayerEntity):
    """Representation of a Number of Mudia Players server."""

    _attr_media_content_type = MediaType.MUSIC
    _children: list[str] = []
    _child_states = dict[str, State]()

    # pylint: disable=no-member
    def __init__(self, hass, entities):
        """Initialize the device."""
        self.hass = hass

        self._attr_unique_id = "combined"

        # _LOGGER.info(f"entities: {entities}")
        self._children.extend(entities)
        _LOGGER.info(self._children)
        for child in self._children:
            _LOGGER.info(child)
            self._child_states[child] = State(child, MediaPlayerState.OFF)

        self._current_player = entities[0]

    async def async_update(self) -> None:
        """Get the latest data and update the state."""
        if self._children is None:
            return

        reversed_children = self._children
        reversed_children.reverse()
        highest_state_player = self._current_player

        for child_name in reversed_children:
            # _LOGGER.info(f"Updating: {child_name}")

            state = self.hass.states.get(child_name)
            if state is None:
                self._child_states[child_name] = State(child_name, MediaPlayerState.OFF)
            else:
                self._child_states[child_name] = state

            # _LOGGER.info(self.hass.states.get(child_name))
            child_state = STATES_ORDER_LOOKUP.get(
                self._get_state_from_string(self._child_states[child_name].state), 0
            )
            current_state = STATES_ORDER_LOOKUP.get(
                self._get_state_from_string(
                    self._child_states[highest_state_player].state
                ),
                0,
            )

            if child_state > current_state and child_state > STATES_ORDER_LOOKUP.get(
                MediaPlayerState.PAUSED, 0
            ):
                highest_state_player = child_name

            self._current_player = highest_state_player

    def _get_state_from_string(self, value: str) -> MediaPlayerState:
        if STRING_TO_STATE[value] is not None:
            return STRING_TO_STATE[value]

        return MediaPlayerState.OFF

    @property
    def _current_state(self) -> State:
        return self._child_states[self._current_player]

    @property
    def name(self) -> str | None:
        """Return the name of the device."""
        return "Combined Musicnode Media"

    @property
    def state(self) -> MediaPlayerState:
        """Return the media state."""
        return self._get_state_from_string(self._current_state.state)

    @property
    def is_volume_muted(self) -> bool | None:
        """Boolean if volume is currently muted."""
        return self._child_attr(ATTR_MEDIA_VOLUME_MUTED) in [
            True,
            STATE_ON,
        ]

    @property
    def media_content_id(self) -> str | None:
        """Return the content ID of current playing media."""
        return self._child_attr(ATTR_MEDIA_CONTENT_ID)

    @property
    def media_duration(self) -> int | None:
        """Return the duration of current playing media in seconds."""
        return self._child_attr(ATTR_MEDIA_DURATION)

    @property
    def media_position(self) -> int | None:
        """Position of current playing media in seconds."""
        return self._child_attr(ATTR_MEDIA_POSITION)

    @property
    def media_position_updated_at(self) -> datetime | None:
        """Last valid time of media position."""
        return self._child_attr(ATTR_MEDIA_POSITION_UPDATED_AT)

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        return self._child_attr(ATTR_MEDIA_TITLE)

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media (Music track only)."""
        return self._child_attr(ATTR_MEDIA_ARTIST)

    @property
    def media_album_name(self) -> str | None:
        """Return the album of current playing media (Music track only)."""
        return self._child_attr(ATTR_MEDIA_ALBUM_NAME)

    @property
    def media_image_hash(self) -> str | None:
        """Hash value for media image."""
        # TO DO
        return None

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        child_range = VOLUME_RANGES[self._current_player]
        child_vol = self._child_attr(ATTR_MEDIA_VOLUME_LEVEL)

        diff = child_range[1] - child_range[0]
        value = ((child_vol * 100) - child_range[0]) / diff

        return value

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        supported = SUPPORT_MPD
        return supported

    @property
    def source(self) -> str | None:
        """Name of the current input source."""
        return self._current_player

    @property
    def source_list(self) -> list[str] | None:
        """Return the list of available input sources."""
        return self._children

    @property
    def repeat(self) -> RepeatMode:
        """Return current repeat mode."""
        return self._child_attr(ATTR_MEDIA_REPEAT)

    @property
    def shuffle(self) -> bool | None:
        """Boolean if shuffle is enabled."""
        return self._child_attr(ATTR_MEDIA_SHUFFLE)

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        return self._child_attr(ATTR_ENTITY_PICTURE)

    async def async_select_source(self, source: str) -> None:
        """Choose a different available playlist and play it."""
        await self.async_update()
        self._current_player = source

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._async_call_service(SERVICE_TURN_ON, allow_override=True)

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._async_call_service(SERVICE_TURN_OFF, allow_override=True)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        data = {ATTR_MEDIA_VOLUME_MUTED: mute}
        await self._async_call_service(SERVICE_VOLUME_MUTE, data, allow_override=True)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        child_range = VOLUME_RANGES[self._current_player]
        diff = child_range[1] - child_range[0]
        value = ((volume * diff) + child_range[0]) / 100

        data = {ATTR_MEDIA_VOLUME_LEVEL: value}
        await self._async_call_service(SERVICE_VOLUME_SET, data, allow_override=True)

    async def async_media_play(self) -> None:
        """Send play command."""
        if self._current_player == "media_player.spotify_louis":
            data = {ATTR_INPUT_SOURCE: "Musicnode"}
            await self._async_call_service(
                SERVICE_SELECT_SOURCE, data, allow_override=True
            )
        await self._async_call_service(SERVICE_MEDIA_PLAY, allow_override=True)

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self._async_call_service(SERVICE_MEDIA_PAUSE, allow_override=True)

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self._async_call_service(SERVICE_MEDIA_STOP, allow_override=True)

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self._async_call_service(
            SERVICE_MEDIA_PREVIOUS_TRACK, allow_override=True
        )

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._async_call_service(SERVICE_MEDIA_NEXT_TRACK, allow_override=True)

    async def async_media_seek(self, position: float) -> None:
        """Send seek command."""
        data = {ATTR_MEDIA_SEEK_POSITION: position}
        await self._async_call_service(SERVICE_MEDIA_SEEK, data)

    async def async_play_media(
        self, media_type: MediaType | str, media_id: str, **kwargs: Any
    ) -> None:
        """Play a piece of media."""
        data = {ATTR_MEDIA_CONTENT_TYPE: media_type, ATTR_MEDIA_CONTENT_ID: media_id}
        await self._async_call_service(SERVICE_PLAY_MEDIA, data, allow_override=True)

    async def async_volume_up(self) -> None:
        """Turn volume up for media player."""
        await self._async_call_service(SERVICE_VOLUME_UP, allow_override=True)

    async def async_volume_down(self) -> None:
        """Turn volume down for media player."""
        await self._async_call_service(SERVICE_VOLUME_DOWN, allow_override=True)

    async def async_media_play_pause(self) -> None:
        """Play or pause the media player."""
        await self._async_call_service(SERVICE_MEDIA_PLAY_PAUSE, allow_override=True)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select sound mode."""
        data = {ATTR_SOUND_MODE: sound_mode}
        await self._async_call_service(
            SERVICE_SELECT_SOUND_MODE, data, allow_override=True
        )

    async def async_clear_playlist(self) -> None:
        """Clear players playlist."""
        await self._async_call_service(SERVICE_CLEAR_PLAYLIST, allow_override=True)

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Enable/disable shuffling."""
        data = {ATTR_MEDIA_SHUFFLE: shuffle}
        await self._async_call_service(SERVICE_SHUFFLE_SET, data, allow_override=True)

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set repeat mode."""
        data = {ATTR_MEDIA_REPEAT: repeat}
        await self._async_call_service(SERVICE_REPEAT_SET, data, allow_override=True)

    async def async_toggle(self) -> None:
        """Toggle the power on the media player."""
        await self._async_call_service(SERVICE_TOGGLE, allow_override=True)

    async def _async_call_service(
        self, service_name, service_data=None, allow_override=False
    ):
        """Call either a specified or active child's service."""
        if service_data is None:
            service_data = {}

        if (self._current_state) is None:
            # No child to call service on
            return

        service_data[ATTR_ENTITY_ID] = self._current_state.entity_id

        await self.hass.services.async_call(
            DOMAIN, service_name, service_data, blocking=True, context=self._context
        )

    def _child_attr(self, attr_name):
        """Return the active child's attributes."""
        return (
            self._current_state.attributes.get(attr_name)
            if self._current_state
            else None
        )
