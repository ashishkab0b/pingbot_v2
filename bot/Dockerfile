# bot/Dockerfile
FROM python:3.11-slim

# Set build-time variables for UID and GID
ARG UID=1000
ARG GID=1000

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Start the bot
CMD ["python", "telegram_bot.py"]