FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy detector code
COPY . .

# Expose dashboard port
EXPOSE 8080

# Production-ready Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "detector.dashboard:app"]
