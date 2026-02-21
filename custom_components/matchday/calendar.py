"""Calendar platform for MatchDay."""
from datetime import datetime, timezone
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    """Set up the MatchDay calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Only add the calendar if we have a team ID
    team_id = entry.data.get("team_id")
    if team_id:
        async_add_entities([MatchDayCalendar(coordinator, entry)])


class MatchDayCalendar(CoordinatorEntity, CalendarEntity):
    """Representation of a MatchDay Calendar."""

    def __init__(self, coordinator, entry):
        """Initialize the calendar."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_name = f"MatchDay Appointments (Team {entry.data['team_id']})"
        self._attr_unique_id = f"{DOMAIN}_calendar_{entry.data['team_id']}"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        fixtures = self.coordinator.data.get("fixtures", [])
        now = datetime.now(timezone.utc)

        for item in fixtures:
            fixture = item["fixture"]
            timestamp = fixture.get("timestamp")
            
            if not timestamp:
                continue
                
            match_date = datetime.fromtimestamp(timestamp, timezone.utc)
            
            # Find the next match that hasn't finished yet
            # Check if it's in the future OR currently live
            if match_date >= now or fixture.get("status", {}).get("short") in ["1H", "HT", "2H", "ET", "BT", "P", "SUSP", "INT", "LIVE"]:
                return self._create_calendar_event(item)

        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events = []
        fixtures = self.coordinator.data.get("fixtures", [])

        for item in fixtures:
            fixture = item["fixture"]
            timestamp = fixture.get("timestamp")
            
            if not timestamp:
                continue

            match_date = datetime.fromtimestamp(timestamp, timezone.utc)

            if start_date <= match_date <= end_date:
                events.append(self._create_calendar_event(item))

        return events

    def _create_calendar_event(self, match_data: dict) -> CalendarEvent:
        """Create a CalendarEvent from API match data."""
        fixture = match_data["fixture"]
        league = match_data.get("league", {})
        teams = match_data.get("teams", {})
        
        home_team = teams.get("home", {}).get("name", "Unknown Home")
        away_team = teams.get("away", {}).get("name", "Unknown Away")
        
        summary = f"{home_team} vs {away_team}"
        description = f"League: {league.get('name', 'Unknown')}\nRound: {league.get('round', '')}"
        
        if fixture.get("venue", {}).get("name"):
            location = f"{fixture['venue']['name']}, {fixture['venue'].get('city', '')}"
        else:
            location = "Unknown Venue"

        start = datetime.fromtimestamp(fixture["timestamp"], timezone.utc)
        
        # Assume a standard match duration of roughly 120 minutes (including half time)
        from datetime import timedelta
        end = start + timedelta(minutes=120)

        return CalendarEvent(
            summary=summary,
            start=start,
            end=end,
            description=description,
            location=location,
        )
