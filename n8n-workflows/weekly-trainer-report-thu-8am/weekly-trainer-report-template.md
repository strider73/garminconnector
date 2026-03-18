# Weekly Trainer Report Output Template

This script produces both **stdout text** and a **PDF report**.

## Stdout Output

```
Connecting to Garmin...
Connected as: {full_name}

==========================================================================================
  WEEKLY TRAINER REPORT - {full_name}
  {YYYY-MM-DD (Day)} to {YYYY-MM-DD (Day)}
==========================================================================================

  Detecting naps...

-------------------------------------------------------------------------------------------------------------------
  SLEEP & RECOVERY
-------------------------------------------------------------------------------------------------------------------
Date       | Bedtime  | Wake Up  |   Hrs |  Deep |   REM |   HRV |  RHR | Nap
-------------------------------------------------------------------------------------------------------------------
Mon 03/10  | 11:30PM  |  6:45AM  |   6.8 |  85m  |  42m  |    68 |   50 | -
Tue 03/11  | 12:15AM  |  7:00AM  |   6.5 |  72m  |  38m  |    71 |   49 | 2:30pm-3:00pm (30m)
(repeated for 7 days)
-------------------------------------------------------------------------------------------------------------------

  Loading 2-week averages...
  2-week avg loaded (steps: XX,XXX, active cal: X,XXX, HRV: XXms)

  [PDF] Report saved: {path}/reports/trainer_report_{YYYY-MM-DD}.pdf
```

## PDF Report (single A4 page)

The PDF contains 4 sections on one page:

### Section 1: Sleep & Recovery Table
```
Day  | Bed     | Wake    | Hrs  | Deep | REM | HRV | RHR | Nap
Mon  | 11:30PM | 6:45AM  | 6.8  | 85m  | 42m | 68  | 50  | -
(7 rows)

Avg 6.5h/night (target 7.5h) | Deep 78m | REM 35m | Naps 3/7 days
```

### Section 2: Activity Chart
- Line chart: Steps (blue) + Active Calories (red) per day
- Dashed lines: 2-week averages for both
- 3-line text comment comparing to baselines

### Section 3: Heart & Recovery Chart
- Line chart: RHR (red) + Max HR (dark red) + HRV (blue) + Intensity mins (orange)
- Dashed lines: 2-week averages
- 3-line text comment on recovery patterns

### Section 4: Next Week Plan + Yearly Goal
```
NEXT WEEK PLAN
Cal target: X,XXX/day  |  Steps target: XX,XXX/day  |  Sleep: above 6.5h

2026 GOAL (+30%)
Cal:   [████████░░░░░░░] XX%   now X,XXX / target 1,838  — on track/below
Steps: [████████░░░░░░░] XX%   now XX,XXX / target 16,826  — on track/below
```

## Data Sources (Garmin API)
- `garmin.get_sleep_data(date)` → sleep table
- `garmin.get_heart_rates(date)` → RHR, Max HR
- `garmin.get_hrv_data(date)` → HRV values
- `garmin.get_stress_data(date)` → stress levels
- `garmin.get_body_battery(date)` → body battery
- `garmin.get_stats(date)` → steps, calories, intensity
- 2-week historical loop (day 8-21) → baseline averages
- Nap detection via `detect_nap.py` + PostgreSQL HR data

## Yearly Goal Constants
- Baseline Active Cal: 1,414/day (Mar 2026)
- Target Active Cal: 1,838/day (+30%)
- Baseline Steps: 12,943/day (Mar 2026)
- Target Steps: 16,826/day (+30%)
- Weekly progression: 0.5-1% increase
