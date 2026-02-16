Read the Garmin morning readiness report from stdin. Output ONLY a single SMS message.

STRICT RULES:
- Maximum 150 characters total
- ONE sentence only
- No preamble, no explanation, no "Here's the summary"
- Just output the raw SMS text, nothing else
- Focus on recovery status and today's plan

FORMAT: [Recovery status]. [Key metric]. Today: [hours]h [intensity] — [activity]. See email.

EXAMPLE: "Good recovery, HRV 71 on baseline. Today: 2.5h moderate — technical drills, serve work. See email."

Use these baselines for comparison: RHR 50 bpm, HRV 70 ms, Sleep 6.5h avg (7.5h target).
