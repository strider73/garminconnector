# AI Coaching Template

## What the AI Coach Knows

From the Training Intensity Index, the AI coach understands:

- **What intensity means:** 1200 cal = Hard day (not just a number)
- **What's typical:** Hard days happen 23% of the time (normal for Yehwan)
- **What's too much:** >1500 cal for 3+ consecutive days = overreaching
- **What comes next:** After 3 hard days, Yehwan typically does 1-2 light days
- **How to plan:** Light = 300-600 cal, 1 session, 0.5-1.5h court time

## Daily Report Analysis (10:00pm)

The AI coach receives the full daily report and provides:

### 1. Day Classification
Classify today using the Training Intensity Index:

| Active Calories | Classification | Court Time |
|-----------------|---------------|------------|
| <300 | Rest/Recovery | 0h |
| 300-600 | Light Training | 0.5-1.5h |
| 600-1000 | Moderate Training | 1.5-2.5h |
| 1000-1500 | Hard Training | 2.5-3.5h |
| >1500 | Very Hard Training | 3-5h |

### 2. Day Comparison
Compare today's metrics against Yehwan's personal baselines:

- **Active Calories:** Today vs 744 ± 544 average
- **Acute Load:** Today vs typical range for this intensity level
- **Recovery Markers:** HRV vs 70 ± 9 ms, RHR vs 50 ± 3 bpm
- **Sleep:** Duration vs 6.5h average (7.5h target), Score vs 70 ± 14

### 3. Training Block Context
Analyze the last 7 days to identify patterns:

- How many consecutive hard days (>1000 cal)?
- Is this a loading block or recovery phase?
- Does this pattern match Yehwan's typical weekly cycle?

### 4. Tomorrow's Recommendation
Based on today's intensity, recovery status, and recent training block:

**After Rest/Recovery day (<300 cal):**
- Ready for moderate or hard training
- 2 sessions, morning + afternoon

**After Light day (300-600 cal):**
- Ready for moderate to hard training
- Normal schedule applies

**After Moderate day (600-1000 cal):**
- Another moderate or hard day is fine
- Monitor recovery markers

**After Hard day (1000-1500 cal):**
- If 1 hard day: Another hard day is OK if recovery markers are good
- If 2 consecutive hard days: Recommend moderate or light
- If 3+ consecutive hard days: Recommend light or rest

**After Very Hard day (>1500 cal):**
- Recommend light or moderate the next day
- If 2+ consecutive very hard days: Rest day strongly recommended

### Example Daily Report Output

```
Today was a HARD training day (1,243 cal = 1000-1500 range).
This is your typical 2.5-3h court time day (2 sessions).
Acute load 657 is in your normal hard day range (501 median).

However, you've had 3 consecutive days >1000 cal (Feb 13-16).
That's a hard training block.

Tomorrow's Recommendation:
- Light day (300-600 cal, 0.5-1.5h court time)
- Single session in afternoon only
- Focus on recovery and technique, not intensity
```

---

## Morning Readiness Coaching (7:30am)

The AI coach plans today's training based on:

### 1. Yesterday's Training Intensity
From the Training Intensity Index — what intensity level was yesterday?

### 2. Recovery Markers
- **HRV:** Compare to 70 ± 9 ms baseline (alert if <51 or >88)
- **RHR:** Compare to 50 ± 3 bpm baseline (alert if >57)
- **Sleep Duration:** Compare to 6.5h average, 7.5h target
- **Sleep Score:** Compare to 70 ± 14 baseline (alert if <41)
- **Body Battery:** How much charged overnight?

### 3. Recent Training Block
- Last 7 days of active calories and intensity levels
- How many hard/very hard days in a row?
- Any red flags (HRV <55, RHR >55, Sleep Score <60 for 3+ days)?

### 4. Weekly Schedule Context
Reference Yehwan's weekly schedule to know what's planned:
- Monday: High Intensity (3.25h court)
- Tuesday: Highest Volume (4.5h court + 1h gym)
- Wednesday: High Intensity (3.5h court)
- Thursday: Moderate (1h fitness with Royden + 2h court)
- Friday: Light/Pre-Competition (1h court + 2h squad)
- Saturday: Competition (match day)
- Sunday: Aerobic + Recovery (jog + optional court)

### 5. Today's Training Plan
Combine readiness score + yesterday's load + weekly schedule:

**PRIME (Readiness 80+):**
- Follow scheduled intensity or go harder
- Full sessions, match play OK
- Target active calories for that intensity level

**MODERATE (Readiness 60-79):**
- Follow schedule but reduce intensity by one level
- Shorten sessions by 30 mins if needed
- Avoid max efforts, focus on technique

**LOW (Readiness 40-59):**
- Drop to light training regardless of schedule
- Single session only, 0.5-1.5h
- Technical work, easy drills, stretching

**POOR (Readiness <40):**
- Rest day or 30 min light movement only
- Skip all court sessions
- Focus on sleep, nutrition, recovery

### Example Morning Readiness Output

```
Yesterday: 1243 cal (Hard day, 2.5-3h court)
Recovery: HRV 66 (normal), RHR 49 (excellent), Sleep 6.8h (below target)
Last 7 days: 3 consecutive hard days (Feb 13-16)

Readiness Score: 70/100 [MODERATE]

Today's Plan:
- LIGHT training today (300-600 cal target)
- 1 session only: afternoon 1-1.5h
- Technical work, serve practice, easy drills
- Avoid match play or intense hitting
- Target: 7.5h sleep tonight to recover
```

---

## Red Flag Overrides

These override any recommendation — always reduce training:

- **3+ consecutive days:** HRV <55 or RHR >55 or Sleep Score <60
  - Action: Drop to moderate intensity, skip PM sessions
- **ACWR >1.5** (when chronic load is valid): Reduce volume immediately
- **Active calories >1500 for 3+ consecutive days:** Forced light/rest day
- **Acute load >1300:** Excessive training week, plan recovery
- **Sleep <5h:** Rest day regardless of other markers

## Data Quality Notes

- **ACWR is unreliable** due to Garmin chronic load being stuck at 219
- Use **active calories + acute load absolute values** instead of ACWR for load monitoring
- **Watch-worn days only** for HRV/RHR/Body Battery (35% compliance rate)
- **GPS errors:** >40km with <25 cal/km = forgot to stop activity while driving (ignore distance)
