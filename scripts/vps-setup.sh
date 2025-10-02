#!/bin/bash

# VPS Initial Setup Script for Telegram Gym Bot
# Run this script as root on a fresh Ubuntu 22.04 VPS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
DEPLOY_USER="deploy"
APP_DIR="/home/${DEPLOY_USER}/telegram-gym-bot"
REPO_URL="https://github.com/CristianProdius/telegram-gym-bot.git"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Telegram Gym Bot VPS Setup Script  ${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt update && apt upgrade -y

# Install essential packages
echo -e "${YELLOW}Installing essential packages...${NC}"
apt install -y \
    curl \
    wget \
    git \
    nano \
    htop \
    ufw \
    fail2ban \
    unattended-upgrades \
    ca-certificates \
    gnupg \
    lsb-release

# Create deploy user if not exists
if ! id "$DEPLOY_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating deploy user...${NC}"
    adduser --disabled-password --gecos "" $DEPLOY_USER
    usermod -aG sudo $DEPLOY_USER
    echo -e "${GREEN}Deploy user created${NC}"
else
    echo -e "${GREEN}Deploy user already exists${NC}"
fi

# Setup Docker
echo -e "${YELLOW}Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    mkdir -m 0755 -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add deploy user to docker group
    usermod -aG docker $DEPLOY_USER

    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

# Install Nginx
echo -e "${YELLOW}Installing Nginx...${NC}"
apt install -y nginx

# Setup firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo -e "${GREEN}Firewall configured${NC}"

# Setup fail2ban
echo -e "${YELLOW}Configuring fail2ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban

# Configure automatic security updates
echo -e "${YELLOW}Enabling automatic security updates...${NC}"
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades

# Clone repository as deploy user
echo -e "${YELLOW}Cloning repository...${NC}"
su - $DEPLOY_USER -c "
    if [ ! -d '$APP_DIR' ]; then
        git clone $REPO_URL $APP_DIR
    else
        cd $APP_DIR && git pull origin main
    fi
"

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
su - $DEPLOY_USER -c "
    mkdir -p $APP_DIR/data
    mkdir -p $APP_DIR/logs
    mkdir -p /home/$DEPLOY_USER/backups
"

# Create environment file template
echo -e "${YELLOW}Creating environment configuration template...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    su - $DEPLOY_USER -c "cp $APP_DIR/.env.example $APP_DIR/.env"
    echo -e "${YELLOW}Please edit $APP_DIR/.env with your configuration${NC}"
fi

# Create Nginx configuration
echo -e "${YELLOW}Setting up Nginx configuration...${NC}"
cat > /etc/nginx/sites-available/telegram-bot << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    client_max_body_size 50M;

    location /webhook {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional: Grafana monitoring
    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Create systemd service for auto-start
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/telegram-bot.service << EOF
[Unit]
Description=Telegram Gym Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=$DEPLOY_USER
Group=$DEPLOY_USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker compose -f $APP_DIR/docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f $APP_DIR/docker-compose.yml down
ExecReload=/usr/bin/docker compose -f $APP_DIR/docker-compose.yml restart

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable telegram-bot

# Create backup script
echo -e "${YELLOW}Creating backup script...${NC}"
cat > /home/$DEPLOY_USER/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/deploy/telegram-gym-bot"

mkdir -p $BACKUP_DIR

# Backup database
cd $APP_DIR
docker compose exec -T postgres pg_dump -U gymbot gymbot > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Backup .env file
cp $APP_DIR/.env $BACKUP_DIR/env_backup_$TIMESTAMP

# Backup data directory
tar -czf $BACKUP_DIR/data_backup_$TIMESTAMP.tar.gz -C $APP_DIR data/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "env_backup_*" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chown $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/backup.sh
chmod +x /home/$DEPLOY_USER/backup.sh

# Setup cron for backups
echo -e "${YELLOW}Setting up automated backups...${NC}"
(crontab -u $DEPLOY_USER -l 2>/dev/null; echo "0 2 * * * /home/$DEPLOY_USER/backup.sh >> /home/$DEPLOY_USER/backups/backup.log 2>&1") | crontab -u $DEPLOY_USER -

# Create deployment helper script
echo -e "${YELLOW}Creating deployment helper script...${NC}"
cat > /home/$DEPLOY_USER/deploy.sh << 'EOF'
#!/bin/bash
cd /home/deploy/telegram-gym-bot
git pull origin main
docker compose pull
docker compose down
docker compose up -d
docker system prune -f
echo "Deployment completed at $(date)"
EOF

chown $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/deploy.sh
chmod +x /home/$DEPLOY_USER/deploy.sh

# Install Certbot for SSL
echo -e "${YELLOW}Installing Certbot for SSL certificates...${NC}"
apt install -y certbot python3-certbot-nginx

# Print summary
echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}    Setup Completed Successfully!    ${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit the environment configuration:"
echo "   ${YELLOW}nano $APP_DIR/.env${NC}"
echo ""
echo "2. Update Nginx configuration with your domain:"
echo "   ${YELLOW}nano /etc/nginx/sites-available/telegram-bot${NC}"
echo ""
echo "3. Start the bot:"
echo "   ${YELLOW}cd $APP_DIR && docker compose up -d${NC}"
echo ""
echo "4. Setup SSL certificate (after DNS is configured):"
echo "   ${YELLOW}certbot --nginx -d your-domain.com${NC}"
echo ""
echo "5. Set Telegram webhook:"
echo "   ${YELLOW}curl -F \"url=https://your-domain.com/webhook\" https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook${NC}"
echo ""
echo -e "${GREEN}System Information:${NC}"
echo "- Deploy user: $DEPLOY_USER"
echo "- App directory: $APP_DIR"
echo "- Backup directory: /home/$DEPLOY_USER/backups"
echo "- Logs directory: $APP_DIR/logs"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "- View logs: docker compose -f $APP_DIR/docker-compose.yml logs -f"
echo "- Restart bot: docker compose -f $APP_DIR/docker-compose.yml restart"
echo "- Deploy updates: /home/$DEPLOY_USER/deploy.sh"
echo "- Manual backup: /home/$DEPLOY_USER/backup.sh"
echo ""
echo -e "${YELLOW}Remember to configure GitHub secrets for CI/CD if using GitHub Actions!${NC}"