#!/bin/bash

# Exit script on any error
set -e

# Log the start of the deployment
echo "Starting deployment process..."

# Navigate to the correct directory
cd oap_server_side

# Log the current directory for debugging
echo "Deploying from directory: $(pwd)"

# Ensure the latest changes are pulled
echo "Pulling the latest changes from the git repository..."
git pull --ff-only origin master
echo "Successfully pulled the latest changes."

# Build Docker images and start containers
echo "Building Docker containers (without cache)..."
docker-compose build --no-cache
echo "Starting Docker containers in detached mode..."
docker-compose up -d

# Log Docker container status
echo "Docker containers are up and running. Current container status:"
docker-compose ps

# Optional: If you want to check logs for debugging
# echo "Displaying the last 50 lines of logs for each container..."
# docker-compose logs --tail=50

# Finish deployment
echo "Deployment complete. Your application is running"
