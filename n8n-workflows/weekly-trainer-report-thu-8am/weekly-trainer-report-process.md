# Weekly Trainer Report Thursday 8am — Process

## Trigger
Every Thursday at 8:00am AEST

## Pipeline

### Step 1: Run Python Script (`trainer_report.py`)
- Connects to Garmin API via `garth` OAuth
- Fetches last 7 days of data:
  - Daily activity: steps, distance, active calories, intensity minutes
  - Heart rate: resting HR, max HR per day
  - Sleep: duration, scores per night
  - Workouts: all activities with type, duration, HR, calories
- Generates charts using matplotlib:
  - Weekly activity overview
  - Heart rate and recovery trends
  - Training load distribution
- Combines everything into a PDF report
- Saves to `reports/trainer_report_YYYY-MM-DD.pdf`

### Step 2: Get PDF (n8n SSH node)
- Reads the generated PDF file as base64 from the server

### Step 3: Convert to File (n8n Code node)
- Decodes base64 into a PDF binary attachment

### Step 4: Deliver
- **Gmail** → Chris only: email with PDF attached
- Designed as a quick 5-minute read for the trainer (Royden) before Thursday session

## No AI Coach
This workflow generates a visual PDF report directly from Python — no Claude command involved.

## Files Used
- `n8n-workflows/weekly-trainer-report-thu-8am/trainer_report.py`
