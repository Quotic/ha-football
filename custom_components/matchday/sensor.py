"""Sensor platform for MatchDay."""
from datetime import datetime, timezone
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MatchDay sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Only add the sensors if we have a team ID
    team_id = entry.data.get("team_id")
    if team_id:
        async_add_entities([MatchDayNextMatchSensor(coordinator, entry)])
        async_add_entities([MatchDayLiveScoreSensor(coordinator, entry)])


class MatchDayNextMatchSensor(CoordinatorEntity, SensorEntity):
    """Representation of a MatchDay Next Match Sensor."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"MatchDay Next Match (Team {entry.data['team_id']})"
        self._attr_unique_id = f"{DOMAIN}_next_match_{entry.data['team_id']}"
        self._attr_icon = "mdi:soccer"

    @property
    def state(self) -> str | None:
        """Return the next match."""
        fixtures = self.coordinator.data.get("fixtures", [])
        now = datetime.now(timezone.utc)

        for item in fixtures:
            fixture = item["fixture"]
            timestamp = fixture.get("timestamp")
            
            if not timestamp:
                continue
                
            match_date = datetime.fromtimestamp(timestamp, timezone.utc)
            
            if match_date >= now:
                # We found the next match in the future
                teams = item.get("teams", {})
                home = teams.get("home", {}).get("name", "Unknown")
                away = teams.get("away", {}).get("name", "Unknown")
                return f"{home} vs {away}"

        return "No upcoming matches"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        fixtures = self.coordinator.data.get("fixtures", [])
        now = datetime.now(timezone.utc)

        for item in fixtures:
            fixture = item["fixture"]
            timestamp = fixture.get("timestamp")
            
            if not timestamp:
                continue
                
            match_date = datetime.fromtimestamp(timestamp, timezone.utc)
            
            if match_date >= now:
                league = item.get("league", {})
                return {
                    "Date": match_date.isoformat(),
                    "League": league.get("name", "Unknown"),
                    "Round": league.get("round", "Unknown"),
                    "Venue": fixture.get("venue", {}).get("name", "Unknown"),
                }

        return {}


class MatchDayLiveScoreSensor(CoordinatorEntity, SensorEntity):
    """Representation of a MatchDay Live Score Sensor."""

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"MatchDay Live Status (Team {entry.data['team_id']})"
        self._attr_unique_id = f"{DOMAIN}_live_score_{entry.data['team_id']}"
        self._attr_icon = "mdi:scoreboard-outline"

    @property
    def state(self) -> str | None:
        """Return the live match score."""
        fixtures = self.coordinator.data.get("fixtures", [])

        for item in fixtures:
            fixture = item["fixture"]
            status = fixture.get("status", {}).get("short", "")

            # Check if match is currently happening
            if status in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"]:
                teams = item.get("teams", {})
                goals = item.get("goals", {})
                
                home_team = teams.get("home", {}).get("name", "Unknown")
                away_team = teams.get("away", {}).get("name", "Unknown")
                
                home_score = goals.get("home", 0)
                away_score = goals.get("away", 0)
                
                # API sports returns None for goals quite frequently if none are scored
                home_score = 0 if home_score is None else home_score
                away_score = 0 if away_score is None else away_score
                
                return f"{home_team} {home_score} - {away_score} {away_team}"

        return "No Live Match"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        fixtures = self.coordinator.data.get("fixtures", [])

        for item in fixtures:
            fixture = item["fixture"]
            status = fixture.get("status", {}).get("short", "")

            if status in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"]:
                status_long = fixture.get("status", {}).get("long", "Unknown")
                elapsed = fixture.get("status", {}).get("elapsed", 0)
                
                return {
                    "Match Status": status_long,
                    "Elapsed Minutes": elapsed,
                }

        return {}
