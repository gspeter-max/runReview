#!/bin/bash

# start.sh - Auto-launch script for runReview

# Function to check if Docker is running
is_docker_running() {
    docker info >/dev/null 2>&1
}

echo "Checking Docker status..."

# Detect OS
OS="$(uname)"

# Check for docker command
if ! command -v docker &> /dev/null; then
    echo "Error: 'docker' command not found. Please install Docker."
    exit 1
fi

# Start Docker if not running (macOS specific)
if ! is_docker_running; then
    if [ "$OS" = "Darwin" ]; then
        echo "Docker is not running. Attempting to start Docker Desktop..."
        open -a Docker
        
        echo "Waiting for Docker daemon to start..."
        # Wait for Docker to become responsive
        COUNTER=0
        while ! is_docker_running; do
            if [ $COUNTER -gt 60 ]; then
                echo -e "\nError: Docker failed to start within the timeout period."
                exit 1
            fi
            sleep 2
            ((COUNTER++))
            echo -n "."
        done
        echo -e "\nDocker is ready."
    else
        echo "Error: Docker is not running. Please start the Docker daemon."
        exit 1
    fi
fi

# Determine if we should use 'docker compose' or 'docker-compose'
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' found."
    exit 1
fi

echo "Starting application with $DOCKER_COMPOSE..."
if $DOCKER_COMPOSE up --build -d; then
    URL="http://localhost:80"
    echo "------------------------------------------------"
    echo "Success! Application is running at: $URL"
    echo "------------------------------------------------"
    
    if [ "$OS" = "Darwin" ]; then
        echo "Opening $URL in your browser..."
        open "$URL"
    fi
else
    echo "Failed to start application. Please check the logs above."
    exit 1
fi
