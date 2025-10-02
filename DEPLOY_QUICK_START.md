# Quick Deployment Guide to VPS

## What You Need
- VPS with Ubuntu 22.04 (minimum 2GB RAM)
- Your Telegram bot token from @BotFather
- SSH access to your VPS

## Step 1: Connect to Your VPS
```bash
ssh root@your-vps-ip
```

## Step 2: Run Setup Script
```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/CristianProdius/telegram-gym-bot/main/scripts/vps-setup.sh
chmod +x vps-setup.sh
./vps-setup.sh
```

This script will automatically install:
- Docker & Docker Compose
- Nginx (for reverse proxy)
- Git
- Security tools (firewall, fail2ban)
- Create deploy user
- Clone the repository

## Step 3: Configure Your Bot
```bash
# Switch to deploy user
su - deploy
cd telegram-gym-bot

# Edit configuration
nano .env
```

Add your bot token and settings:
```env
BOT_TOKEN=your_bot_token_here
BOT_MODE=polling  # Use 'webhook' if you have a domain
DB_PASSWORD=choose_a_strong_password
REDIS_PASSWORD=another_strong_password
```

## Step 4: Start the Bot
```bash
# Use production docker-compose file
docker compose -f docker-compose.production.yml up -d

# Check if it's running
docker compose -f docker-compose.production.yml ps

# View logs
docker compose -f docker-compose.production.yml logs -f bot
```

## Step 5: Test Your Bot
Open Telegram and message your bot with `/start`

## How Deployment Works

### The Simple Build-on-Server Approach:
1. **Code is on GitHub** - Your source code lives in the repository
2. **VPS pulls the code** - Using `git pull` to get latest changes
3. **Docker builds locally** - The VPS builds the Docker image from source
4. **Containers start** - Docker Compose starts all services (bot, database, redis)

### What Happens During Updates:
```bash
cd /home/deploy/telegram-gym-bot
./scripts/deploy.sh
```

This script will:
1. Backup your database
2. Pull latest code from GitHub
3. Build new Docker image on the VPS
4. Restart containers with new code

## File Structure on VPS
```
/home/deploy/
├── telegram-gym-bot/         # Your bot code
│   ├── .env                  # Configuration
│   ├── data/                 # Bot data
│   ├── logs/                 # Log files
│   └── docker-compose.production.yml
├── backups/                  # Database backups
└── deploy.sh                 # Deployment script
```

## Common Commands

### View logs:
```bash
docker compose -f docker-compose.production.yml logs -f bot
```

### Restart bot:
```bash
docker compose -f docker-compose.production.yml restart bot
```

### Stop everything:
```bash
docker compose -f docker-compose.production.yml down
```

### Update and redeploy:
```bash
cd /home/deploy/telegram-gym-bot
git pull
docker compose -f docker-compose.production.yml build bot
docker compose -f docker-compose.production.yml up -d
```

### Check database:
```bash
docker compose -f docker-compose.production.yml exec postgres psql -U gymbot
```

## Troubleshooting

### Bot not responding?
1. Check logs: `docker compose -f docker-compose.production.yml logs bot`
2. Verify token in `.env` file
3. Check if container is running: `docker ps`

### Port already in use?
```bash
# Find what's using the port
sudo lsof -i :8000
# Kill the process or change port in docker-compose
```

### Out of disk space?
```bash
# Clean up Docker
docker system prune -a
```

## Optional: Setup Domain & SSL

If you have a domain:

1. Point your domain to VPS IP
2. Update Nginx config:
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
# Change server_name from _ to your-domain.com
```

3. Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

4. Update .env:
```env
BOT_MODE=webhook
WEBHOOK_URL=https://your-domain.com/webhook
```

5. Restart bot:
```bash
docker compose -f docker-compose.production.yml restart bot
```

## That's It! 🎉

Your bot should now be running on your VPS. The deployment is simple:
- **No complex CI/CD needed** for small projects
- **Everything builds on the VPS** - no need for Docker registries
- **Simple git pull + rebuild** for updates