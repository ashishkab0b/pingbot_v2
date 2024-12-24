# bot/Dockerfile
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create the cron jobs by running build_schedule.py
# RUN python build_schedule.py

# Start the bot
CMD ["python", "telegram_bot.py"]