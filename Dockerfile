FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir "garth>=0.5.17,<0.6.0" "psycopg2-binary>=2.9"

# Copy project files
COPY garminconnect/ ./garminconnect/
COPY n8n-workflows/ ./n8n-workflows/

# Default script (override with any script at runtime)
CMD ["python3", "n8n-workflows/daily-report-930pm/daily_report.py"]
