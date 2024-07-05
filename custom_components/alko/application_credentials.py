"""Application credentials platform for the ALKO integration."""

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import AlkoLocalOAuth2Implementation
from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    """Return custom auth implementation."""
    return AlkoLocalOAuth2Implementation(
        hass,
        auth_domain,
        credential,
        AuthorizationServer(
            # authorize_url=OAUTH2_AUTHORIZE,
            authorize_url="",  # Overridden in config flow.
            token_url=OAUTH2_TOKEN,
        ),
    )
