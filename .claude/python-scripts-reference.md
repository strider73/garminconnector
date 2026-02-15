# Python Scripts & Technical Reference

## Tech Stack
- **Language**: Python 3.10+
- **Package Manager**: PDM
- **Auth**: OAuth via [Garth](https://github.com/matin/garth) library
- **Testing**: pytest + pytest-vcr (VCR cassettes for HTTP replay)
- **Linting**: ruff, black, isort, mypy
- **Build**: pdm-backend
- **Database**: PostgreSQL (garmin_daily_metrics table)
- **Deployment**: Docker on Raspberry Pi (STRIDER-PI)

## Project Structure
- `garminconnect/` - Core library package (`__init__.py`, `fit.py`, `workout.py`)
- `tests/` - Test suite with VCR cassettes
- `config.py` - Garmin credentials, DB connection, HR thresholds
- `custom_scripts/` - All reporting and data scripts (see below)

## Custom Scripts (`custom_scripts/`)

### Automated (run via n8n workflows on Pi)
| Script | Schedule | Purpose |
|--------|----------|---------|
| `store_daily_metrics.py` | 9:30pm daily | Fetches Garmin data → stores in PostgreSQL |
| `training_readiness.py` | 7:30am daily | Morning readiness score (ACWR, sleep, HRV, RHR, body battery) |
| `daily_report.py` | 10pm daily | Full daily report (Dockerfile entrypoint) |

### Manual / Ad-hoc
| Script | Purpose |
|--------|---------|
| `trainer_report.py` | Comprehensive coach report with weekly analysis |
| `weekly_report.py` | 7-day summary |
| `weekly_health_report.py` | Health-focused weekly metrics |
| `monthly_report.py` | 30-day trends |
| `generate_full_report.py` | Combined full report |
| `heart_rate_analysis.py` | HR zone analysis |
| `intensity_analysis.py` | Training intensity breakdown |
| `last_7days_activity.py` | Recent activity list |
| `fetch_today.py` | Today's raw data fetch |
| `fetch_workouts.py` | Workout history fetch |
| `fetch_4weeks_sleep.py` | 4-week sleep data |
| `show_profile.py` | Garmin profile display |
| `garmin_connect.py` | Connection utility |

## Development Commands
```bash
pdm run format      # Auto-format (ruff --fix, isort, black)
pdm run lint        # Check quality (isort, ruff, black, mypy)
pdm run test        # Run tests with coverage
pdm run testcov     # Tests + HTML/XML coverage reports
pdm run codespell   # Check spelling
pdm run all         # Run all checks (lint + codespell + pre-commit + test)
pdm run clean       # Clean __pycache__ and .pyc files
```

## Key Conventions
- Line length: 88 (black default)
- Import sorting: isort with "black" profile
- Security linting enabled (flake8-bandit)
- Tokens stored at `~/.garminconnect` (local) or `~/.garth` (Docker)
- VCR cassettes in `tests/cassettes/` for HTTP interaction replay

## Infrastructure
- **n8n**: `https://n8n.adventuretube.net` — workflow automation
- **Whisper**: `https://whisper.adventuretube.net` — speech-to-text (Docker on Pi, port 8000)
- **PostgreSQL**: on `adventuretube.net:5432`, database `adventuretube`, table `garmin_daily_metrics`

## Sensitive Files
- `config.py` - Contains credentials, do NOT commit to public repos
- `~/.garminconnect` - OAuth tokens
- `.claude/mcp.json` - n8n API key