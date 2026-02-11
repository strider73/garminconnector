# Getting Started

## 1. Setup

### Install dependencies
```bash
pdm install --group :all
```

### Configure credentials
```bash
cp config.example.py config.py
```
Edit `config.py` with your Garmin Connect email and password:
```python
email = "your_email@example.com"
password = "your_password"
```

## 2. Login / Create Session

Run any script and it will auto-login and save the session to `~/.garth/`:
```bash
pdm run profile
```

Or test the connection explicitly:
```bash
pdm run python3 custom_scripts/garmin_connect.py
```

## 3. Run Scripts

All scripts are run via PDM from the project root:

```bash
pdm run profile        # Show logged-in account
pdm run report         # Daily health & activity report
pdm run weekly         # 7-day breakdown
pdm run health         # Weekly tennis health report
pdm run monthly        # 4-week trending report
pdm run activity       # Last 7 days activity
pdm run today          # Today's snapshot
pdm run sleep          # 28-day sleep data
pdm run workouts       # Recent workouts
pdm run heart-rate     # Heart rate analysis
pdm run intensity      # Intensity minutes
pdm run readiness      # Training readiness & status
pdm run trainer        # Weekly trainer report (for your fitness trainer)
pdm run full-report    # Generate printable markdown report
```

## 4. Session Management

### Session location
Garmin OAuth tokens are stored at:
```
~/.garth/
```

### Delete session / force re-login
If your session expires or you want to switch accounts:
```bash
rm -rf ~/.garth
```
The next `pdm run` command will automatically log in again using `config.py` credentials.

### Switch Garmin accounts
1. Delete the current session:
   ```bash
   rm -rf ~/.garth
   ```
2. Edit `config.py` with the new account credentials
3. Run any script to create a new session:
   ```bash
   pdm run profile
   ```

## 5. Virtual Environment (optional)

PDM handles the venv automatically when you use `pdm run`. If you want to activate it manually:

```bash
# Activate
source .venv/bin/activate

# Now you can run scripts directly
python3 custom_scripts/show_profile.py

# Deactivate when done
deactivate
```
