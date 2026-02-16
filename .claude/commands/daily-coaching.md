Read the Garmin daily report from stdin. Read these files for context:

1. `.claude/YEHWAN-profile.md` — baselines and thresholds
2. `.claude/YEHWAN-training-intensity-index.md` — intensity classification
3. `.claude/YEHWAN-weekly-schedule.md` — weekly schedule

STRICT RULES:
- Output ONLY the plain text block below, nothing else
- No markdown headers, no tables, no bold, no bullet narratives
- No preamble like "Here's the analysis" or "Let me analyze"
- Fill in the bracketed values and output the result
- Keep total output under 800 characters
- Use the piped-in report data + the reference files for numbers

OUTPUT THIS EXACT TEMPLATE (fill in values):

TODAY: [Day], [Date]
[INTENSITY LEVEL] — [active_cal] cal ([calorie range for that level])
Court time: ~[X]h ([N] sessions)

vs BASELINES:
Active Cal: [today] vs 759 avg — [above/below/normal]
HRV: [today] vs 70 avg — [status]
RHR: [today] vs 50 avg — [status]
Sleep: [today]h (score [X]) vs 6.5h avg — [status]
Acute Load: [today] vs typical [range] for [intensity]

LAST 7 DAYS:
[date]: [cal] — [level]
[date]: [cal] — [level]
[date]: [cal] — [level]
[date]: [cal] — [level]
[date]: [cal] — [level]
[date]: [cal] — [level]
[date]: [cal] — [level]
Pattern: [1 sentence]

TOMORROW ([Day] — scheduled: [from weekly schedule]):
Intensity: [LEVEL] ([cal range])
Sessions: [count], [times]
Focus: [specific activities]
Sleep target: [X]h

ALERTS: [any red flags from profile thresholds, or "None"]
