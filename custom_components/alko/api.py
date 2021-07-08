"""API for AL-KO bound to Home Assistant OAuth."""
import logging
from typing import cast

from aiohttp import BasicAuth, ClientSession
from pyalko import AlkoClient

from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class ConfigEntryAlkoClient(AlkoClient):
    """Provide AL-KO authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize AL-KO auth."""
        super().__init__(websession)
        self._oauth_session = oauth_session

    async def async_get_access_token(self):
        """Return a valid access token."""
        if not self._oauth_session.valid_token:
            await self._oauth_session.async_ensure_token_valid()

        return self._oauth_session.token["access_token"]


class AlkoLocalOAuth2Implementation(
    config_entry_oauth2_flow.LocalOAuth2Implementation
):
    """AL-KO Local OAuth2 implementation."""

    async def _token_request(self, data: dict) -> dict:
        """Make a token request."""
        session = async_get_clientsession(self.hass)

        data["client_id"] = self.client_id

        if self.client_secret is not None:
            data["client_secret"] = self.client_secret

        headers = {
            "Authorization": BasicAuth(self.client_id, self.client_secret).encode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        resp = await session.post(self.token_url, headers=headers, data=data)
        resp.raise_for_status()
        return cast(dict, await resp.json())
