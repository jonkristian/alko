"""Config flow for AL-KO."""
from datetime import timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.util import dt as dt_util
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle AL-KO OAuth2 authentication."""

    DOMAIN = DOMAIN

    def __init__(self):
        """Initialize the config flow."""
        super().__init__()
        self.data_schema = {
            vol.Required("username"): str,
            vol.Required("password"): str,
        }

        self._username = None
        self._password = None

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_user(self, user_input=None) -> dict:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Check if we have application credentials
        implementations = await config_entry_oauth2_flow.async_get_implementations(
            self.hass, self.DOMAIN
        )
        if not implementations:
            return self.async_abort(
                reason="missing_credentials",
                description_placeholders={
                    "url": "https://www.home-assistant.io/integrations/alko/#application-credentials"
                }
            )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(self.data_schema)
            )

        self._username = user_input["username"]
        self._password = user_input["password"]

        implementation_id = list(implementations.keys())[0]
        self._auth_implementation = implementation_id
        return await self.async_oauth_create_entry(self)

    async def async_step_reauth(self, user_input=None) -> dict:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> dict:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> dict:
        """Create an oauth config entry or update existing entry for reauth."""
        try:
            implementations = await config_entry_oauth2_flow.async_get_implementations(
                self.hass, self.DOMAIN
            )
            implementation = implementations[self._auth_implementation]

            token_data = {
                "client_id": implementation.client_id,
                "client_secret": implementation.client_secret,
                "grant_type": "password",
                "username": self._username,
                "password": self._password,
                "scope": "alkoCustomerId alkoCulture offline_access introspection"
            }

            token_response = await aiohttp_client.async_get_clientsession(self.hass).post(
                "https://idp.al-ko.com/connect/token", data=token_data
            )
            token_response.raise_for_status()
            token_info = await token_response.json()

            now = dt_util.utcnow() + timedelta(seconds=30)
            expires_at = dt_util.as_timestamp(now)

            config_data = {
                "auth_implementation": self._auth_implementation,
                "token": {
                    "access_token": token_info["access_token"],
                    "refresh_token": token_info["refresh_token"],
                    "expires_in": token_info["expires_in"],
                    "token_type": token_info["token_type"],
                    "scope": token_info["scope"],
                    "expires_at": expires_at
                },
                "username": self._username,
                "password": self._password
            }

            existing_entry = await self.async_set_unique_id(DOMAIN)
            if existing_entry:
                self.hass.config_entries.async_update_entry(
                    existing_entry, data=config_data)
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            return self.async_create_entry(title="Alko", data=config_data)
        except Exception as e:
            _LOGGER.error(f"Error obtaining tokens: {e}")
            return self.async_abort(reason="token_request_failed")

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> dict:
        """Handle reconfiguration of the integration."""
        if user_input is None:
            # Get existing entry data
            entry = self._get_reconfigure_entry()
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=vol.Schema({
                    vol.Required("username", default=entry.data.get("username", "")): str,
                    vol.Required("password", default=entry.data.get("password", "")): str,
                }),
            )

        self._username = user_input["username"]
        self._password = user_input["password"]

        # Get the implementation ID from the existing entry
        entry = self._get_reconfigure_entry()
        self._auth_implementation = entry.data["auth_implementation"]

        return await self.async_oauth_create_entry(self)
