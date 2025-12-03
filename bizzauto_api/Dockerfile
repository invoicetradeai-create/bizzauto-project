# Dockerfile for the FastAPI backend

# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app


# Install system dependencies for google-cloud-vision
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
COPY . .

# Expose the port the app runs on
EXPOSE 10000

# Copy the run script into the container
COPY run.sh .

# Make the script executable
RUN chmod +x run.sh

# Set this script as the default command
CMD ["./run.sh"]
