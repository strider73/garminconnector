Read the Garmin daily report from stdin. Output ONLY a single SMS message.

STRICT RULES:
- Maximum 150 characters total
- ONE sentence only
- No preamble, no explanation, no "Here's the summary"
- Just output the raw SMS text, nothing else

FORMAT: [Intensity] [cal]cal. [Key concern]. Tomorrow: [hours]h [intensity] — [activity]. Sleep [X]h.

EXAMPLE: "Hard day 1243cal. Sleep 6.3h low. Tomorrow: 1.5h light — drills only. Sleep 8h."

Use these baselines for comparison: RHR 50 bpm, HRV 70 ms, Sleep 6.5h avg (7.5h target), Active Cal 759 avg.
