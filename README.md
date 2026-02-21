# MatchDay Integration for Home Assistant

![GitHub release (latest by date)](https://img.shields.io/github/v/release/TODO/ha-football?style=for-the-badge)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

MatchDay is a custom integration for Home Assistant that pulls in football (soccer) fixtures and live match data using the `api-football.com` API.

## Features
- Upcoming matches as a **Calendar** entity
- **Next Match** sensor
- **Live Match Status/Score** sensor
- Dynamic polling rate: 12 hours normally, switching to 5 minutes when a match is active (to keep API requests well inside the free tier).

## Installation

### Method 1: HACS (Recommended)
1. Open HACS in Home Assistant.
2. Go to "Integrations".
3. Click the 3 dots in the top right corner and select "Custom repositories".
4. Add the URL to this repository and select category "Integration".
5. Click "Add".
6. Search for "MatchDay" in HACS and install it.
7. Restart Home Assistant.

### Method 2: Manual
1. Download the `custom_components/matchday` folder.
2. Copy it into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration
Go to **Settings -> Devices & Services -> Add Integration -> MatchDay** and provide:
- `api-football` API key (Free tier is sufficient)
- Team ID
- League ID
- Season
