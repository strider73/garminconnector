# Yehwan — Athlete Profile

## Basic Information
- **Name**: Yehwan
- **Age**: 20
- **Height**: 6'1" (185 cm)
- **Weight**: 75 kg (165 lbs)
- **Sport**: Tennis (UTR 8 — advanced tournament level)
- **BMI**: 22.8 (healthy/athletic)
- **Recent Injury**: Shoulder (fully recovered as of Feb 2026)

## Baseline Performance Metrics

**Dataset:** Mar 6, 2025 - Feb 16, 2026 (340 days, 120 watch-worn days for recovery metrics, 8 GPS errors filtered)

### Recovery Markers (watch-worn days only)
- **Resting HR**: 50.4 ± 3.0 bpm
  - Range: 45-64 bpm
  - Baseline target: 44 bpm (excellent athlete level)
  - Alert threshold: <44 or >57 bpm

- **HRV (Last Night)**: 69.9 ± 9.4 ms
  - Range: 37-96 ms
  - Normal range: 50-89 ms
  - Alert threshold: <51 or >88 ms

- **HRV (Weekly Average)**: 71.3 ± 5.0 ms
  - Range: 59-83 ms
  - More stable metric than nightly HRV

- **VO2 Max**: 60.4 ± 2.5
  - Range: 56-63
  - Status: Excellent for age 20
  - Indicates strong aerobic fitness

### Sleep Patterns
- **Duration**: 6.5 ± 1.4h
  - Range: 2-10h
  - Target: 7.5h minimum, 8h on pre-match nights
  - Alert threshold: <3.7h or >9.3h
  - **Note**: Currently averaging below target

- **Sleep Score**: 69.5 ± 14.3
  - Range: 32-94
  - Alert threshold: <41 (poor recovery)

- **Deep Sleep**: 19.3% ± 7.1%
  - Range: 0-44%
  - Critical for physical recovery

- **REM Sleep**: 15.0% ± 6.5%
  - Range: 0-31%
  - Critical for mental recovery and skill consolidation

### Daily Activity
- **Steps**: 8,751 ± 4,471
  - Range: 17-22,954
  - Alert threshold: >17,692 (possible GPS error if distance also high)

- **Distance**: 8.8 ± 6.2 km
  - Range: 0-39 km (GPS errors >40km filtered)
  - Alert: >40km with <25 cal/km = forgot to stop activity while driving

- **Active Calories**: 744 ± 544
  - Range: 0-3,081
  - Highly variable based on training intensity

- **Moderate Intensity**: 21.9 ± 24.8 mins/day
  - Range: 0-161 mins

- **Vigorous Intensity**: 26.8 ± 31.0 mins/day
  - Range: 0-152 mins

### Training Load

**⚠️ DATA QUALITY ISSUE:** Chronic Load from Garmin API is stuck at 219 for 206 out of 346 days, making ACWR calculations unreliable. This causes false high-risk alerts.

**Based on 243 days with valid training data:**

**Training Day Distribution:**
- **Active Training Days** (>500 cal or >30 vig mins): 170 days (70%)
  - Acute Load: Mean 587, Median 430 (range: 4-1,719)
  - Chronic Load: Mean 690, Median 674 (when not stuck at 219)
  - ACWR: Mean 0.72, Median 0.70

- **Light/Rest Days**: 73 days (30%)
  - Acute Load: Mean 198, Median 71

**Acute Load Zones** (based on percentiles):
- **Recovery/Light** (<58): 25% of days (minimal training)
- **Normal** (58-849): 50% of days (typical training)
- **High Training** (>849): 25% of days (intense periods)
- **Alert Threshold**: >1,296 (90th percentile - excessive load)

**Chronic Load (Fitness Level):**
- **Low Fitness** (<219): 25% of days
- **Normal** (219-949): 50% of days
- **High Fitness** (>949): 25% of days
- **Note**: Chronic load represents 28-day rolling fitness baseline

**ACWR (Acute/Chronic Workload Ratio):**
- **Median ACWR**: 0.70 (typical ratio: Acute 205 / Chronic 219)
- **Distribution**:
  - Under-training (<0.8): 57.5% (recovery/deload weeks)
  - Optimal (0.8-1.3): 35.5% (balanced training)
  - Elevated Risk (1.3-1.5): 3.3%
  - High Risk (1.5-1.9): 2.8%
  - Critical (>1.9): 0.9%
- **Injury risk days** (ACWR >1.3): 7.0% of training days (15 total days)

## Key Thresholds & Red Flags

### Training Load Alerts

**IMPORTANT:** Due to Garmin API providing stale Chronic Load data (stuck at 219 for most days), ACWR alerts should be interpreted with caution. Focus on:
1. Acute Load absolute values (>1,296 = excessive)
2. Active calories and intensity minutes trends
3. Multiple consecutive high-load days

**ACWR Zones (when Chronic Load is valid):**
- **ACWR 0.8-1.3**: Safe training zone (optimal progression)
- **ACWR 1.3-1.5**: Elevated risk (monitor recovery closely)
- **ACWR 1.5-1.9**: High injury risk (reduce training volume)
- **ACWR >1.9**: Critical injury risk — reduce training immediately

**Alternative Load Monitoring (when ACWR unreliable):**
- **Acute Load >1,296**: Excessive training week (90th percentile)
- **Active Calories >1,500**: High-output day (watch for multiple consecutive days)
- **Vigorous Minutes >100**: Very high intensity (needs extra recovery)
- **3+ consecutive days** with Acute Load >800: Overreaching risk

### Recovery Alerts
- **RHR >57 bpm**: Elevated, may indicate fatigue or illness
- **RHR >60 bpm for 3+ days**: Overtraining risk
- **HRV <51 ms**: Low recovery status
- **HRV <55 ms for 3+ days**: Chronic fatigue — reduce intensity

### Sleep Alerts
- **<6.5h**: Below average, monitor recovery
- **<3.7h**: Critical — rest day recommended
- **Sleep Score <60 for 3+ days**: Poor recovery pattern
- **Sleep Score <41**: Severe sleep deficit

### Red Flag Actions
When 3+ consecutive days show:
- HRV <55 ms
- RHR >55 bpm
- Sleep Score <60

**Action:** Drop Wednesday training to moderate intensity, skip Sunday PM court session

## Data Quality Notes
- **Watch-worn detection**: Only days with HRV present and Body Battery >0 are used for recovery metrics
- **GPS errors**: Days with >40km distance and <25 cal/km are flagged as "forgot to stop activity" (driving)
- **Missing data**: Some days have incomplete metrics due to watch not worn or connectivity issues
- **Typical watch-worn rate**: ~35% of days (120/340) — indicates need for better compliance
