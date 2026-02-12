FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir "garth>=0.5.17,<0.6.0"

# Copy project files
COPY garminconnect/ ./garminconnect/
COPY custom_scripts/ ./custom_scripts/

# Default script (override with any script at runtime)
CMD ["python3", "custom_scripts/daily_report.py"]
