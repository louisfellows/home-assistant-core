"""Helper class to communicate with the Musicnode API."""
import logging

import requests


class MusicnodeApi:
    """Musicnode API Helper."""

    _LOGGER = logging.getLogger(__name__)

    def __init__(self, host: str, port: int) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self._LOGGER.info("MusicNodeAPI: %d:%d", self.host, self.port)

    def async_send_media_update(self, request: dict) -> bool:
        """Send the thing."""
        api_response = requests.put(
            f"{self.host}:{self.port}/state", json=request, timeout=5000
        )
        return api_response.ok

    def async_send_screen_update(self, line1: str, line2: str) -> bool:
        """Send the thing."""
        mbody = {"Line1": line1, "Line2": line2}
        api_response = requests.put(
            f"{self.host}:{self.port}/message", json=mbody, timeout=5000
        )
        return api_response.ok

    def async_healthcheck(self) -> int:
        """Check we can see the API."""
        api_response = requests.get(
            f"{self.host}:{self.port}/api/Util/healthcheck", timeout=5000
        )
        return api_response.status_code
