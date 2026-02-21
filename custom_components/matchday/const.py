"""Constants for the MatchDay integration."""

DOMAIN = "matchday"

CONF_API_KEY = "api_key"
CONF_TEAM_ID = "team_id"
CONF_LEAGUE_ID = "league_id"
CONF_SEASON = "season"

DEFAULT_POLLING_INTERVAL = 12  # in hours
CONF_POLLING_INTERVAL = "polling_interval"

DEFAULT_LIVE_POLLING_INTERVAL = 5  # in minutes
CONF_LIVE_POLLING_INTERVAL = "live_polling_interval"

API_HOST = "v3.football.api-sports.io"
API_BASE_URL = f"https://{API_HOST}"
