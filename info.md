# MatchDay Integration

![MatchDay Logo/Image](https://img.shields.io/badge/integration-matchday-41BDF5.svg?style=for-the-badge)

MatchDay brings your favorite football team's fixtures and live match data straight into Home Assistant using the `api-football.com` API.

**Note:** You must register for a free API-Football key to use this integration.

## Features
- **Calendar**: Shows all upcoming and past fixtures.
- **Next Match Sensor**: Tracks the details of your team's next game.
- **Live Score Sensor**: Activates during a match to show the live score and match status.
- **Smart Polling**: Polls the API every 12 hours normally, but dynamically switches to polling every 5 minutes during a live match to aggressively save API usage on the free tier (100 daily requests max).

## Configuration
Added via the Home Assistant UI (Settings -> Devices & Services -> Add Integration).
Required fields:
- **API Key**: from api-football.com
- **Team ID**: Obtainable via the API or football sites.
- **League ID**: The primary league the team plays in.
- **Season**: e.g., 2023 

***

For full instructions and updates, please consult the [README](https://github.com/TODO/ha-football).
