FROM python:3.12-slim

# Set environment variables to ensure output is sent straight to logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Use Gunicorn for production instead of the Flask dev server
# This binds to the $PORT environment variable provided by Google Cloud
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "3", "app:app"]
