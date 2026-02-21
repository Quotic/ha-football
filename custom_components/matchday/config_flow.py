import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_TEAM_ID,
    CONF_LEAGUE_ID,
    CONF_SEASON,
    DEFAULT_POLLING_INTERVAL,
    CONF_POLLING_INTERVAL,
    DEFAULT_LIVE_POLLING_INTERVAL,
    CONF_LIVE_POLLING_INTERVAL,
)

class MatchDayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MatchDay."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return MatchDayOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Here we could validate the API key and team ID by making a test request
            # For now, we will just accept the input and create the entry
            return self.async_create_entry(
                title=f"MatchDay: Team {user_input[CONF_TEAM_ID]}", data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_TEAM_ID): int,
                vol.Required(CONF_LEAGUE_ID): int,
                vol.Required(CONF_SEASON): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class MatchDayOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle MatchDay options."""

    def __init__(self, config_entry):
        """Initialize MatchDay options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the MatchDay options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_POLLING_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional(
                CONF_LIVE_POLLING_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_LIVE_POLLING_INTERVAL, DEFAULT_LIVE_POLLING_INTERVAL
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1)),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
