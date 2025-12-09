# Use a full Debian-based image to get access to package managers like apt
FROM python:3.11-slim

# Install FFmpeg, which is required by moviepy and whisper
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the necessary files for installing dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the web server will run on
EXPOSE 5000

# The command to run the celery worker.
# It assumes you have a celery_app instance in app/tasks/tasks.py or similar.
# The command in docker-compose.yml will override this.
CMD ["celery", "-A", "app.tasks.tasks", "worker", "--loglevel=info"]
