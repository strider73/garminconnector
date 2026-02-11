import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
from datetime import date

today = date.today().isoformat()
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

output_file = os.path.join(project_root, f"garmin_report_{today}.md")

print(f"Generating trainer report for {today}...")
print(f"Output: {output_file}\n")

print("  Running: pdm run trainer...")

try:
    result = subprocess.run(
        ["pdm", "run", "trainer"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=120,
    )
    output = result.stdout.strip()
except subprocess.TimeoutExpired:
    output = "(timed out)"
except Exception as e:
    output = f"(error: {e})"

# Strip the "Connecting..." / "Connected as..." lines
lines = output.splitlines()
filtered = []
for line in lines:
    if line.startswith("Connecting to Garmin") or line.startswith("Connected as:"):
        continue
    filtered.append(line)

report_body = "\n".join(filtered).strip()

with open(output_file, "w") as f:
    f.write(f"# Garmin Weekly Trainer Report - {today}\n\n")
    f.write("```\n")
    f.write(report_body)
    f.write("\n```\n")

print(f"\nDone! Report saved to: {output_file}")
