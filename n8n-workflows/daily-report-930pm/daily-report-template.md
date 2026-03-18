# Daily Report Output Template

This is the output structure produced by `daily_report.py`.
The script prints this to stdout, which n8n captures and sends via email/Telegram.

```
Connecting to Garmin...
✅ Connected as: {full_name}

================================================================================
📊 DAILY HEALTH & ACTIVITY REPORT - {YYYY-MM-DD}
================================================================================

📈 Analyzing last 7 days for comparison...

💤 SLEEP ANALYSIS
--------------------------------------------------------------------------------
Sleep Period:       {HH:MM} → {HH:MM}
Total Duration:     {X.XX} hours ({XXX} mins)

Sleep Stages:
  Deep Sleep:       {XX} mins ({XX.X}%)
  Light Sleep:      {XX} mins ({XX.X}%)
  REM Sleep:        {XX} mins ({XX.X}%)
  Awake:            {XX} mins

Sleep Scores:
  Overall Score:    {XX}
  Quality Score:    {XX or N/A}
  Duration Score:   {XX or N/A}

🔄 Comparison to Best of Last 7 Days:
  Duration:         {↗/↘/=} Best was {X.XX}h (today: {+/-XXX} mins)
  Sleep Score:      {↗/↘/=} Best was {XX} (today: {+/-XX})

🏃 ACTIVITY & FITNESS
--------------------------------------------------------------------------------
Steps:              {XX,XXX} / {XX,XXX} ({XX.X}%)
Distance:           {XX.XX} km

Calories:
  Total Burned:     {X,XXX.X} kcal
  Active:           {X,XXX.X} kcal
  BMR (Resting):    {X,XXX.X} kcal

Intensity Minutes:
  Moderate:         {XX} mins
  Vigorous:         {XX} mins
  Total (Weekly):   {XXX} / {XXX} mins

Floors Climbed:     {X}

🔄 Comparison to Best of Last 7 Days:
  Steps:            {↗/↘/=} Best was {XX,XXX} (today: {XX.X}%, {+/-X,XXX})
  Distance:         {↗/↘/=} Best was {XX.XX} km (today: {XX.X}%, {+/-X.XX} km)
  Active Calories:  {↗/↘/=} Best was {X,XXX.X} kcal (today: {XX.X}%, {+/-XXX.X})
  Intensity Mins:   {↗/↘/=} Best was {XXX} mins (today: {XX.X}%, {+/-XXX})

❤️  HEART RATE
--------------------------------------------------------------------------------
Resting HR:         {XX} bpm
Max HR:             {XXX} bpm
Min HR:             {XX} bpm

🔄 Comparison to Best of Last 7 Days:
  Max HR:           {↗/↘/=} Best was {XXX} bpm (today: {+/-XX})

🧘 STRESS & RECOVERY
--------------------------------------------------------------------------------
Average Stress:     {XX}
Max Stress:         {XX}

🔄 Comparison to Best of Last 7 Days:
  Avg Stress:       {↗/↘/=} Best was {XX} (today: {+/-XX})

Body Battery:       {XX}    (if available)

🎯 WORKOUTS & ACTIVITIES
--------------------------------------------------------------------------------
Total Activities: {X}

1. {Activity Name}
   Type:            {activity_type}
   Start Time:      {YYYY-MM-DD HH:MM:SS}
   Duration:        {XXX.X} minutes
   Distance:        {XX.XX} km
   Avg Pace:        {XX.XX} min/km
   Calories:        {XXX.X} kcal
   Avg Heart Rate:  {XXX.X} bpm
   Max Heart Rate:  {XXX.X} bpm

(repeated for each activity)
```

## Data Sources (Garmin API)
- `garmin.get_sleep_data(date)` → sleep section
- `garmin.get_stats(date)` → activity & fitness section
- `garmin.get_heart_rates(date)` → heart rate section
- `garmin.get_stress_data(date)` → stress section
- `garmin.get_stats_and_body(date)` → body battery
- `garmin.get_activities_by_date(date, date)` → workouts section
- 7-day loop of the above → comparison values
