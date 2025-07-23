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

# Get domain name
echo -e "${YELLOW}Enter your domain name (e.g., xenoscribe.example.com):${NC}"
read DOMAIN

# Update system
echo -e "${GREEN}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install required packages
echo -e "${GREEN}Installing required packages...${NC}"
apt-get install -y python3-pip python3-venv nginx ffmpeg

# Create system user for the service
echo -e "${GREEN}Creating system user...${NC}"
if ! id -u xenoscribe >/dev/null 2>&1; then
    useradd --system --user-group --shell /usr/sbin/nologin --home-dir /opt/xenoscribe xenoscribe
fi

# Set up application directory
APP_DIR="/opt/xenoscribe"
echo -e "${GREEN}Setting up application in ${APP_DIR}...${NC}"
mkdir -p ${APP_DIR}
chown xenoscribe:xenoscribe ${APP_DIR}

# Copy application files
echo -e "${GREEN}Copying application files...${NC}"
cp -r . ${APP_DIR}/
chown -R xenoscribe:xenoscribe ${APP_DIR}

# Set up Python virtual environment
echo -e "${GREEN}Setting up Python virtual environment...${NC}
sudo -u xenoscribe python3 -m venv ${APP_DIR}/venv
${APP_DIR}/venv/bin/pip install --upgrade pip
${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "${APP_DIR}/.env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp ${APP_DIR}/.env.example ${APP_DIR}/.env
    chown xenoscribe:xenoscribe ${APP_DIR}/.env
    echo -e "${YELLOW}Please edit ${APP_DIR}/.env to configure your settings${NC}"
    read -p "Press Enter to continue..."
    ${EDITOR:-nano} ${APP_DIR}/.env
fi

# Create systemd service file
echo -e "${GREEN}Creating systemd service...${NC}"
cat > /etc/systemd/system/xenoscribe.service <<EOL
[Unit]
Description=XENOScribe Transcription Service
After=network.target

[Service]
User=xenoscribe
Group=xenoscribe
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Set up Nginx
echo -e "${GREEN}Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/xenoscribe << 'EOL'
server {
    listen 80;
    server_name _;  # This will be replaced

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase max upload size to 2G
    client_max_body_size 2G;
}
EOL

# Replace the server_name in the Nginx config
sed -i "s/server_name _;/server_name ${DOMAIN};/" /etc/nginx/sites-available/xenoscribe

# Enable Nginx site
ln -sf /etc/nginx/sites-available/xenoscribe /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl reload nginx

# Enable and start the service
echo -e "${GREEN}Starting XENOScribe service...${NC}"
systemctl daemon-reload
systemctl enable xenoscribe
systemctl start xenoscribe

# Set up Certbot for SSL
echo -e "${YELLOW}Would you like to set up SSL with Let's Encrypt? (y/n):${NC}"
read SETUP_SSL

if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
    echo -e "${GREEN}Installing Certbot...${NC}"
    apt-get install -y certbot python3-certbot-nginx
    
    echo -e "${GREEN}Obtaining SSL certificate...${NC}"
    certbot --nginx -d ${DOMAIN}
    
    # Set up auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    echo -e "${GREEN}SSL certificate installed and auto-renewal configured.${NC}
    Your site will be available at: https://${DOMAIN}"
else
    echo -e "${YELLOW}SSL not configured. Your site will be available at: http://${DOMAIN}${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To check the status of the service: systemctl status xenoscribe${NC}"
echo -e "${YELLOW}To view logs: journalctl -u xenoscribe -f${NC}"
