"""Application credentials platform for AL-KO."""

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import AlkoLocalOAuth2Implementation
from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, DOMAIN


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return custom auth implementation."""
    return AlkoLocalOAuth2Implementation(
        hass,
        auth_domain,
        credential,
        AuthorizationServer(
            authorize_url="",  # Overridden in config flow.
            token_url=OAUTH2_TOKEN,
        ),
    )


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    return AuthorizationServer(
        authorize_url="",  # Overridden in config flow
        token_url=OAUTH2_TOKEN,
    )


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    """Return description placeholders for the credentials dialog."""
    return {
        "oauth_consent_url": "https://idp.al-ko.com/connect/consent",
        "more_info_url": "https://developer.al-ko.com",
    }


async def async_register_implementation(hass: HomeAssistant) -> None:
    """Register an implementation for AL-KO."""
    implementation = AlkoLocalOAuth2Implementation(
        hass,
        DOMAIN,
        # Empty credentials as they're provided in config flow
        ClientCredential("", ""),
        AuthorizationServer(
            authorize_url="",  # Overridden in config flow.
            token_url=OAUTH2_TOKEN,
        ),
    )
    await config_entry_oauth2_flow.async_get_implementations(hass, DOMAIN)
