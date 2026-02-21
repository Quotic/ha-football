import logging
import asyncio
from datetime import timedelta, datetime, timezone

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    API_BASE_URL,
    API_HOST,
    CONF_API_KEY,
    CONF_TEAM_ID,
    CONF_LEAGUE_ID,
    CONF_SEASON,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_LIVE_POLLING_INTERVAL,
    CONF_POLLING_INTERVAL,
    CONF_LIVE_POLLING_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class MatchDayDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize."""
        self.entry = entry
        self.api_key = entry.data[CONF_API_KEY]
        self.team_id = entry.data[CONF_TEAM_ID]
        self.league_id = entry.data[CONF_LEAGUE_ID]
        self.season = entry.data[CONF_SEASON]
        
        self.polling_interval_hours = entry.options.get(
            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
        )
        self.live_polling_interval_minutes = entry.options.get(
            CONF_LIVE_POLLING_INTERVAL, DEFAULT_LIVE_POLLING_INTERVAL
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=self.polling_interval_hours),
        )

    def _determine_polling_interval(self, fixtures_data: list) -> timedelta:
        """Dynamically determine the polling interval based on match status."""
        now = datetime.now(timezone.utc)
        
        for fixture_obj in fixtures_data:
            fixture = fixture_obj.get("fixture", {})
            status = fixture.get("status", {}).get("short", "")
            
            # If a match is currently in progress (e.g., First Half, Second Half, Halftime, Penalty, Extra Time)
            if status in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"]:
                _LOGGER.debug("Match is active (Status: %s). Switching to live polling interval: %s minutes", status, self.live_polling_interval_minutes)
                return timedelta(minutes=self.live_polling_interval_minutes)
                
            # If the match is about to start (within the next 15 minutes), speed up polling
            timestamp = fixture.get("timestamp")
            if timestamp:
                match_start = datetime.fromtimestamp(timestamp, timezone.utc)
                time_until_match = match_start - now
                if timedelta(minutes=0) < time_until_match <= timedelta(minutes=15):
                    _LOGGER.debug("Match is about to start. Switching to live polling interval.")
                    return timedelta(minutes=self.live_polling_interval_minutes)

        _LOGGER.debug("No active matches. Using standard polling interval: %s hours", self.polling_interval_hours)
        return timedelta(hours=self.polling_interval_hours)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        # For API-Football we need to fetch the fixtures for the team
        headers = {
            "x-apisports-key": self.api_key,
            "x-apisports-host": API_HOST,
        }
        
        url = f"{API_BASE_URL}/fixtures"
        params = {
            "team": self.team_id,
            "season": self.season,
            "league": self.league_id,
        }

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, headers=headers, params=params) as response:
                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed("Invalid API key")
                if response.status != 200:
                    raise UpdateFailed(f"Error speaking with API: {response.status}")
                
                data = await response.json()
                
                if "errors" in data and data["errors"]:
                    # API-sports returns 200 but includes errors in the body sometimes
                    _LOGGER.error("API Error: %s", data["errors"])
                    raise UpdateFailed(f"API Error: {data['errors']}")

                fixtures = data.get("response", [])
                
                # Dynamically set the next update interval
                self.update_interval = self._determine_polling_interval(fixtures)
                
                return self._parse_fixtures(fixtures)
                
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def _parse_fixtures(self, fixtures_data):
        """Parse raw API data into a more usable format."""
        
        # Sort fixtures by timestamp
        fixtures_data.sort(key=lambda x: x["fixture"]["timestamp"])
        
        return {
            "fixtures": fixtures_data,
        }
