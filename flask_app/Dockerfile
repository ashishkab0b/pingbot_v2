# flask_app/Dockerfile
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the /app directory to the new user and group
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Create logs directory
RUN mkdir -p /app/logs

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start the Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]