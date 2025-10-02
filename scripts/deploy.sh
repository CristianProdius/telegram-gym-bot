#!/bin/bash

# Deployment script for Telegram Gym Bot
# This script should be run on the server

set -e  # Exit on error

# Configuration
APP_DIR="/home/deploy/telegram-gym-bot"
BACKUP_DIR="/home/deploy/backups"
COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment of Telegram Gym Bot...${NC}"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Navigate to application directory
cd $APP_DIR

# Backup database if PostgreSQL is running
echo -e "${YELLOW}Backing up database...${NC}"
if docker compose -f $COMPOSE_FILE ps postgres 2>/dev/null | grep -q "Up"; then
    docker compose -f $COMPOSE_FILE exec -T postgres pg_dump -U gymbot gymbot > "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    echo -e "${GREEN}Database backed up successfully${NC}"
else
    echo -e "${YELLOW}Database container not running, skipping backup${NC}"
fi

# Pull latest code from GitHub
echo -e "${YELLOW}Pulling latest code from repository...${NC}"
git pull origin main

# Build the Docker image locally
echo -e "${YELLOW}Building Docker image...${NC}"
docker compose -f $COMPOSE_FILE build bot

# Stop current containers
echo -e "${YELLOW}Stopping current containers...${NC}"
docker compose -f $COMPOSE_FILE down

# Start new containers
echo -e "${YELLOW}Starting new containers...${NC}"
docker compose -f $COMPOSE_FILE up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check if all services are running
echo -e "${YELLOW}Checking service status...${NC}"
if docker compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    echo -e "${GREEN}✅ All services are running${NC}"
    docker compose -f $COMPOSE_FILE ps
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    docker compose -f $COMPOSE_FILE ps
    docker compose -f $COMPOSE_FILE logs --tail=50
    exit 1
fi

# Clean up old Docker images
echo -e "${YELLOW}Cleaning up old Docker images...${NC}"
docker image prune -f

# Show recent logs
echo -e "${YELLOW}Recent bot logs:${NC}"
docker compose -f $COMPOSE_FILE logs --tail=20 bot

echo -e "${GREEN}Deployment completed successfully!${NC}"