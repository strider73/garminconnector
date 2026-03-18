# Morning Readiness 8am — Process

## Trigger
Weekday + Sunday at 8:00am AEST, Saturday at 9:00am AEST

## Pipeline

### Step 1: Run Python Script (`training_readiness.py`)
- Connects to Garmin API via `garth` OAuth
- Fetches overnight recovery data:
  - Sleep: duration, stages, scores, start/end times
  - HRV: last night value, weekly average, status
  - Resting HR
  - Body Battery: charged/drained levels
- Fetches yesterday's activity summary (active calories, steps, workouts)
- Outputs structured plain-text readiness report to stdout
- Includes `[SLEEP_STATUS:PENDING]` or `[SLEEP_STATUS:NO_DATA]` tags if sleep data isn't ready

### Step 2: Format Report (n8n Set node)
- Captures stdout into `plainText`
- Creates email subject with today's date

### Step 3: Sleep Data Retry Loop (n8n If + Wait nodes)
- If sleep status is PENDING or NO_DATA: wait 30 minutes, re-run script
- Retries up to 8 times (4 hours total)
- If data arrives or retries exhausted: proceed to AI Coach

### Step 4: Claude AI Coach (`/morning-readiness` command)
- Reads the raw readiness report from Step 1
- Reads `.claude/reference/YEHWAN-profile.md` for personal baselines
- Reads `.claude/reference/YEHWAN-training-intensity-index.md` for intensity classification
- Reads `.claude/reference/YEHWAN-weekly-schedule.md` for today's scheduled sessions
- Assesses overnight recovery (HRV, RHR, sleep vs baselines)
- Classifies yesterday's training load
- Checks weekly schedule context
- Recommends today's intensity, court time, and focus areas
- Outputs plain-text coaching message (~600 chars)

### Step 5: Deliver (parallel)
- **Gmail** → Chris + Yehwan: raw data (dark block) + AI analysis (light block)
- **Telegram** → Yehwan: AI coaching message only
- **Telegram** → Chris: AI coaching message only

## Files Used
- `n8n-workflows/morning-readiness-8am/training_readiness.py`
- `.claude/commands/morning-readiness.md`
- `.claude/reference/YEHWAN-profile.md`
- `.claude/reference/YEHWAN-training-intensity-index.md`
- `.claude/reference/YEHWAN-weekly-schedule.md`
