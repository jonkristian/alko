"""Config flow for AL-KO."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle AL-KO OAuth2 authentication."""

    DOMAIN = DOMAIN

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    def __init__(self):
        self.data_schema = {
            vol.Required("access_token"): str,
            vol.Required("refresh_token"): str,
        }

        self._access_token = None
        self._refresh_token = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=vol.Schema(self.data_schema)
            )

        self._access_token = user_input["access_token"]
        self._refresh_token = user_input["refresh_token"]

        return await self.async_oauth_create_entry(self)

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict) -> dict:
        """Create an oauth config entry or update existing entry for reauth."""

        now = dt_util.utcnow() + timedelta(seconds=30)
        expires_at = dt_util.as_timestamp(now)

        config_data = {
            "auth_implementation": DOMAIN,
            "token": {
                "access_token": self._access_token,
                "refresh_token": self._refresh_token,
                "expires_in": 1800,
                "token_type": "Bearer",
                "scope": "openid profile alkoCustomerId introspection offline_access",
                "expires_at": expires_at
            }
        }

        existing_entry = await self.async_set_unique_id(DOMAIN)
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        return self.async_create_entry(title="Alko", data=config_data)
