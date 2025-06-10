# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Set the working directoy in the container
WORKDIR /app

# Copy only the requirements file first
COPY requirements.txt /app/requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port your Flask app runs on
EXPOSE 8080

# Set the environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Run the Flask app
CMD ["flask", "run"]