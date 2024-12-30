# Use the official Python image
FROM python:3.11-slim

# Create a non-root user and group first
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install dependencies as root
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to /app
COPY . .

# Create the logs directory and set proper permissions
RUN mkdir -p /app/logs \
    && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]