# Daily Report 9:30pm — Process

## Trigger
Every day at 9:30pm AEST

## Pipeline

### Step 1: Run Python Script (`daily_report.py`)
- Connects to Garmin API via `garth` OAuth
- Fetches last 7 days of data (steps, sleep, HR, stress) for comparison
- Fetches today's data across 5 sections:
  - Sleep: duration, stages (deep/light/REM/awake), scores
  - Activity: steps, distance, calories (active/BMR), intensity minutes
  - Heart Rate: resting/max/min
  - Stress: average/max
  - Workouts: each activity with type, duration, distance, calories, HR
- Outputs structured plain-text report to stdout

### Step 2: Format Report (n8n Set node)
- Captures stdout into `plainText`
- Creates email subject with today's date

### Step 3: Claude AI Coach (`/daily-coaching-email` command)
- Reads the raw report from Step 1
- Reads `.claude/reference/YEHWAN-profile.md` for personal baselines
- Reads `.claude/reference/YEHWAN-training-intensity-index.md` for intensity classification
- Classifies today's intensity (Rest/Light/Moderate/Hard/Very Hard) by active calories
- Assesses recovery (sleep, RHR, stress vs baselines)
- Checks weekly context (is today matching the expected schedule?)
- Recommends tomorrow's intensity and court time
- Outputs plain-text coaching message (~600 chars)

### Step 4: Deliver (parallel)
- **Gmail** → Chris + Yehwan: raw data (dark block) + AI analysis (light block)
- **Telegram** → Yehwan: AI coaching message only
- **Telegram** → Chris: AI coaching message only

## Files Used
- `n8n-workflows/daily-report-930pm/daily_report.py`
- `.claude/commands/daily-coaching-email.md`
- `.claude/reference/YEHWAN-profile.md`
- `.claude/reference/YEHWAN-training-intensity-index.md`
