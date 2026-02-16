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
- **ACWR (Acute/Chronic Workload Ratio)**: 0.4 ± 0.5
  - Range: 0-2.9
  - Safe zone: 0.8-1.3
  - Alert: >1.4 (outside mean + 2σ)
  - Critical: >1.9 (injury risk zone)

- **Acute Load**: 317 ± 463
  - Range: 0-1,719
  - Highly variable (reflects training periodization)

- **Chronic Load**: 463 ± 426
  - Range: 100-1,707
  - Baseline fitness level

## Key Thresholds & Red Flags

### Training Load Alerts
- **ACWR 0.8-1.3**: Safe training zone
- **ACWR 1.5-1.9**: Elevated injury risk
- **ACWR >1.9**: Critical injury risk — reduce training immediately

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
