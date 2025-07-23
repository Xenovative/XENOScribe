#!/bin/bash

# Exit on error
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root${NC}" >&2
    exit 1
fi

# Configuration
APP_DIR="/opt/xenoscribe"
BACKUP_DIR="/opt/xenoscribe_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/xenoscribe_${TIMESTAMP}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

echo -e "${GREEN}Starting XENOScribe update process...${NC}"

# Stop the service
echo -e "${YELLOW}Stopping XENOScribe service...${NC}"
systemctl stop xenoscribe || true

# Backup current installation
echo -e "${GREEN}Backing up current installation to ${BACKUP_PATH}...${NC}"
mkdir -p "${BACKUP_PATH}"
rsync -a --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' "${APP_DIR}/" "${BACKUP_PATH}/"

# Backup the virtual environment
echo -e "${GREEN}Backing up virtual environment...${NC}"
if [ -d "${APP_DIR}/venv" ]; then
    cp -r "${APP_DIR}/venv" "${BACKUP_PATH}/venv_backup"
fi

# Backup .env file
if [ -f "${APP_DIR}/.env" ]; then
    cp "${APP_DIR}/.env" "${BACKUP_PATH}/.env.bak"
fi

# Update application files
echo -e "${GREEN}Updating application files...${NC}"
# Copy only necessary files and directories
rsync -av --delete \
    --exclude='.env' \
    --exclude='venv' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "${PROJECT_DIR}/app.py" \
    "${PROJECT_DIR}/requirements.txt" \
    "${PROJECT_DIR}/.env.example" \
    "${PROJECT_DIR}/assets/" \
    "${PROJECT_DIR}/templates/" \
    "${APP_DIR}/"

# Ensure required directories exist with proper permissions
mkdir -p "${APP_DIR}/assets" "${APP_DIR}/templates" "${APP_DIR}/logs"
chown -R xenoscribe:xenoscribe "${APP_DIR}"
chmod 755 "${APP_DIR}"
find "${APP_DIR}" -type d -exec chmod 755 {} \;
find "${APP_DIR}" -type f -name "*.py" -o -name "*.txt" -o -name "*.md" | xargs chmod 644 2>/dev/null || true

# Update Python dependencies
echo -e "${GREEN}Updating Python dependencies...${NC}"
sudo -u xenoscribe "${APP_DIR}/venv/bin/pip" install --upgrade pip
sudo -u xenoscribe "${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt" --upgrade

# Restart the service
echo -e "${GREEN}Restarting XENOScribe service...${NC}"
systemctl daemon-reload
systemctl start xenoscribe

# Check service status
if systemctl is-active --quiet xenoscribe; then
    echo -e "${GREEN}XENOScribe has been successfully updated and restarted!${NC}
"
    echo -e "${YELLOW}Backup location: ${BACKUP_PATH}${NC}"
    echo -e "${YELLOW}To check service status: systemctl status xenoscribe${NC}"
    echo -e "${YELLOW}To view logs: journalctl -u xenoscribe -f${NC}"
else
    echo -e "${RED}Error: Failed to start XENOScribe service${NC}"
    echo -e "${YELLOW}Check the logs with: journalctl -u xenoscribe -f${NC}"
    echo -e "${YELLOW}To restore from backup: rsync -a ${BACKUP_PATH}/ ${APP_DIR}/${NC}"
    exit 1
fi
