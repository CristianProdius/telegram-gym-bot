# VPS Server Setup Guide for Telegram Gym Bot

This guide will walk you through setting up your VPS server to host the Telegram Gym Bot.

## Prerequisites

- A VPS with at least:
  - 2 GB RAM (4 GB recommended)
  - 2 CPU cores
  - 20 GB storage
  - Ubuntu 22.04 LTS (or similar Linux distribution)
  - SSH access with root or sudo privileges

## Step 1: Initial Server Setup

Connect to your VPS via SSH:
```bash
ssh root@your-vps-ip
```

### 1.1 Update System Packages
```bash
apt update && apt upgrade -y
```

### 1.2 Create a Deploy User
```bash
# Create a new user for deployments
adduser deploy

# Add user to sudo group
usermod -aG sudo deploy

# Switch to deploy user
su - deploy
```

### 1.3 Setup SSH Key Authentication (Optional but recommended)
On your local machine:
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to server
ssh-copy-id deploy@your-vps-ip
```

## Step 2: Install Required Software

### 2.1 Install Docker
```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add deploy user to docker group
sudo usermod -aG docker deploy

# Verify installation
docker --version
docker compose version
```

### 2.2 Install Git
```bash
sudo apt-get install -y git
```

### 2.3 Install Nginx (for reverse proxy)
```bash
sudo apt-get install -y nginx
```

## Step 3: Setup Firewall

```bash
# Install ufw if not installed
sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow custom ports if needed (e.g., for monitoring)
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus (only if you need external access)

# Enable firewall
sudo ufw enable
```

## Step 4: Clone and Configure the Bot

### 4.1 Clone Repository
```bash
cd /home/deploy
git clone https://github.com/CristianProdius/telegram-gym-bot.git
cd telegram-gym-bot
```

### 4.2 Create Environment File
```bash
cp .env.example .env
nano .env
```

Update the following variables:
```env
# Bot Configuration
BOT_TOKEN=your-telegram-bot-token
BOT_MODE=webhook  # Use webhook for production
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8000

# Database
DB_USER=gymbot
DB_PASSWORD=strong-password-here
DB_HOST=postgres
DB_PORT=5432
DB_NAME=gymbot

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=another-strong-password

# Security
SECRET_KEY=generate-a-strong-secret-key

# Monitoring (optional)
GRAFANA_PASSWORD=admin-password
```

### 4.3 Create Data Directories
```bash
mkdir -p data logs
chmod 755 data logs
```

## Step 5: Setup Nginx Reverse Proxy

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

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

    # Optional: Grafana
    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: SSL Certificate (Using Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
sudo systemctl status snap.certbot.renew.service
```

## Step 7: Deploy the Bot

### 7.1 Build and Start Containers
```bash
cd /home/deploy/telegram-gym-bot

# Build the image
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f bot
```

### 7.2 Set Webhook
After the bot is running, set the webhook:
```bash
curl -F "url=https://your-domain.com/webhook" \
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

## Step 8: Setup Automatic Deployment

### 8.1 Create Deploy Script
The deploy script is already in `scripts/deploy.sh`. Make it executable:
```bash
chmod +x scripts/deploy.sh
```

### 8.2 Setup GitHub Actions Secrets
In your GitHub repository settings, add the following secrets:
- `DEPLOY_HOST`: Your VPS IP address
- `DEPLOY_USER`: deploy
- `DEPLOY_KEY`: Your private SSH key (the content of ~/.ssh/id_ed25519)
- `DEPLOY_PORT`: 22 (or custom SSH port)
- `TELEGRAM_BOT_TOKEN`: Your bot token (for notifications)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (for notifications)

### 8.3 Setup Webhook for Auto-Deploy (Alternative to GitHub Actions)
Create a webhook endpoint:
```bash
sudo nano /home/deploy/webhook-deploy.sh
```

```bash
#!/bin/bash
cd /home/deploy/telegram-gym-bot
git pull origin main
docker compose pull
docker compose down
docker compose up -d
```

```bash
chmod +x /home/deploy/webhook-deploy.sh
```

## Step 9: Monitoring and Maintenance

### 9.1 Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/telegram-bot
```

```
/home/deploy/telegram-gym-bot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 deploy deploy
    sharedscripts
    postrotate
        docker compose -f /home/deploy/telegram-gym-bot/docker-compose.yml restart bot
    endscript
}
```

### 9.2 Setup Monitoring
Access monitoring dashboards:
- Grafana: https://your-domain.com/grafana (default: admin/admin)
- Prometheus: http://your-vps-ip:9090 (if firewall allows)

### 9.3 Backup Strategy
Create a backup script:
```bash
nano /home/deploy/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker compose exec postgres pg_dump -U gymbot gymbot > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Backup .env file
cp /home/deploy/telegram-gym-bot/.env $BACKUP_DIR/env_backup_$TIMESTAMP

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "env_backup_*" -mtime +30 -delete
```

Setup cron job for daily backups:
```bash
crontab -e
# Add this line:
0 2 * * * /home/deploy/backup.sh
```

## Step 10: Security Hardening

### 10.1 Fail2ban
```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 10.2 Automatic Security Updates
```bash
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## Troubleshooting

### Check Bot Status
```bash
docker compose ps
docker compose logs bot
```

### Restart Bot
```bash
docker compose restart bot
```

### Check Webhook
```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

### Database Issues
```bash
# Access PostgreSQL
docker compose exec postgres psql -U gymbot

# Check database
\l
\dt
```

### Clear Docker Cache
```bash
docker system prune -a
```

## Support

For issues or questions:
- Check logs: `docker compose logs -f`
- Review documentation: `/docs` directory
- GitHub Issues: https://github.com/CristianProdius/telegram-gym-bot/issues