# GarminConnector Project

## Overview
Python 3 API wrapper for Garmin Connect (`garminconnect` package, v0.2.36). Provides access to 100+ Garmin Connect API endpoints for health, fitness, and device data.

## Tech Stack
- **Language**: Python 3.10+
- **Package Manager**: PDM
- **Auth**: OAuth via [Garth](https://github.com/matin/garth) library
- **Testing**: pytest + pytest-vcr (VCR cassettes for HTTP replay)
- **Linting**: ruff, black, isort, mypy
- **Build**: pdm-backend

## Project Structure
- `garminconnect/` - Core library package (`__init__.py`, `fit.py`, `workout.py`)
- `tests/` - Test suite with VCR cassettes
- `config.py` - Garmin account credentials and HR thresholds
- `example.py` - Simple getting-started example
- `demo.py` - Comprehensive demo with 100+ API methods
- `*.py` (root) - Various data-fetching and reporting scripts

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
- Tokens stored at `~/.garminconnect`
- VCR cassettes in `tests/cassettes/` for HTTP interaction replay

## User Profile (Yehwan)
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 74 kg (163 lbs)
- **Sport**: Tennis (UTR 8 - advanced tournament level)
- **Resting HR**: ~44 bpm (athlete range)
- **BMI**: ~21.6 (lean/athletic)

## Sensitive Files
- `config.py` - Contains credentials, do NOT commit to public repos
- `~/.garminconnect` - OAuth tokens
