# YEHWAN — Training Intensity Index

**Analysis Period:** March 6, 2025 - February 16, 2026 (340 days)
**Data Source:** Active calories from garmin_daily_metrics (reliable indicator of training load)

## Training Intensity Classification

Based on 242 days with valid active calorie data:

| Intensity Level | Active Calories | Frequency | % of Time | Typical Acute Load |
|-----------------|-----------------|-----------|-----------|-------------------|
| 🛌 **Rest/Recovery** | <300 | 41 days | 16.9% | ~90 (range: 6-986) |
| 🚶 **Light Training** | 300-600 | 53 days | 21.9% | ~71 (range: 10-1541) |
| 🏃 **Moderate Training** | 600-1000 | 57 days | 23.6% | ~315 (range: 4-1508) |
| 💪 **Hard Training** | 1000-1500 | 56 days | 23.1% | ~501 (range: 17-1611) |
| 🔥 **Very Hard Training** | >1500 | 35 days | 14.5% | ~1084 (range: 6-1719) |

## Estimated Court Time by Intensity Level

### 🛌 Rest/Recovery (<300 active calories)
**Court Time:** 0 hours
- Morning: Off | Afternoon: Off
- Activities: Light stretching (15-30 mins), recovery walk, foam rolling
- Frequency: 1 day per week (17%)

### 🚶 Light Training (300-600 active calories)
**Court Time:** 0.5-1.5 hours
- Morning: 0-1h (optional) | Afternoon: 0.5-1.5h
- Activities: Easy groundstroke drills, serve practice, footwork, light hitting
- Single session day
- Frequency: 1-2 days per week (22%)

### 🏃 Moderate Training (600-1000 active calories)
**Court Time:** 1.5-2.5 hours
- Morning: 1-1.5h | Afternoon: 1-1.5h
- Activities: Technical drills + serve practice (~500 cal/hr), practice sets (~600 cal/hr)
- Two sessions: 1-1.5h each
- Frequency: 2 days per week (24%)

### 💪 Hard Training (1000-1500 active calories)
**Court Time:** 2.5-3.5 hours
- Morning: 1.5-2h | Afternoon: 1.5-2h
- Activities: Hard hitting + match play (~650 cal/hr), tournament simulation
- Two sessions: 1.5-2h each. May include fitness training.
- Frequency: 1-2 days per week (23%)

### 🔥 Very Hard Training (>1500 active calories)
**Court Time:** 3-5 hours
- Morning: 2-2.5h | Afternoon: 1.5-2.5h
- Activities: Full matches (~700 cal/hr), multiple sessions, tournament days
- 2-3 sessions per day
- Frequency: 1 day per week (15%)

## Weekly Volume

| Component | Hours/Week |
|-----------|-----------|
| Court time | 12-15h |
| Gym/fitness + running | ~5h (Thursday 1h with trainer Royden + own gym + 2-3 jogs of 3.6-4.2km) |
| **Total** | **~17-20h** |

## Weekly Intensity Pattern

```
Mon   ████████░░  HIGH         (3.25h court)
Tue   ██████████  VERY HIGH    (4.5h court + 1h gym)
Wed   ████████░░  HIGH         (3.5h court)
Thu   ██████░░░░  MODERATE     (1h fitness + 2h court + light coaching)
Fri   ████░░░░░░  LOW-MOD      (1h court + 2h fun squad)
Sat   █████████░  VERY HIGH    (competition @ 1pm)
Sun   ███░░░░░░░  LOW          (jog + optional court)
```

**Natural taper:** Mon-Wed hard → Thu-Fri easing off → Sat competition
For exact session times: @import .claude/YEHWAN-weekly-schedule.md

## Training Philosophy

Data reveals a **periodized, balanced approach:**
1. **Recovery Built In:** 39% of days are rest/light (<600 cal)
2. **High Intensity When Needed:** 37% of days are hard/very hard (>1000 cal)
3. **Not Constant Grinding:** Varies intensity throughout the week
4. **Tournament Peaks:** Very hard days (>1500 cal) = competition/tournament days

## Calorie Burn Reference (75kg competitive player)

| Activity | Cal/hr |
|----------|--------|
| Light hitting/drills | ~400 |
| Moderate intensity practice | ~500 |
| Match play (competitive) | ~650 |
| Tournament/intense matches | ~750 |

Varies by: rally intensity, court coverage, rest intervals, environmental conditions.

## Training Load Monitoring

**Why active calories, not ACWR:** Garmin chronic load is stuck at 219 (see YEHWAN-profile.md data quality notes). Use active calories as primary load indicator.

### Load Thresholds
| Threshold | Value | Action |
|-----------|-------|--------|
| Excessive acute load | >1,296 | 90th percentile — reduce volume |
| High-output day | >1,500 active cal | Watch for multiple consecutive days |
| Very high intensity | >100 vigorous mins | Needs extra recovery |
| Overreaching risk | 3+ days with Acute >800 | Plan light/rest day |
| Overload | >1,500 cal for 3+ days | Forced rest day |
| Detraining risk | <300 cal for 7+ days | Resume training |

### Intensity Management Notes
- Tuesday is the biggest load day — monitor Garmin data closely
- Friday squad session is social but watch HR — competitive players can go hard unconsciously

### Sunday Tempo Run Protocol
- **Purpose:** Fill aerobic high zone shortage (Garmin: AEROBIC_HIGH_SHORTAGE)
- Post-match: 20 min / 3.5–4.0 km
- No-match: 25–30 min / 4.5–5.5 km
- Pace: 5:20–5:40/km | HR ceiling: 165 bpm
- Progression: 20 min (weeks 1-2) → 25 min (weeks 3-4) → 30 min (weeks 5+)

## Progression Plan
- **Weeks 1–2:** Establish Sunday jog habit at 20 min. Let chronic load build naturally.
- **Weeks 3–4:** Extend Sunday jog to 25–30 min. ACWR should normalize toward 1.0–1.2.
- **Weeks 5–6:** Garmin should show PRODUCTIVE. Aerobic high numbers climbing. Reassess.
