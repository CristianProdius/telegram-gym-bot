# 🚀 Automatic Deployment Setup

This guide shows you how to set up automatic deployment so your VPS updates automatically when you push to GitHub.

## Two Options for Auto-Deployment

### Option 1: GitHub Actions (Recommended - Easiest)
Deploy automatically using GitHub Actions with SSH.

### Option 2: GitHub Webhooks (Fastest - Advanced)
Your VPS listens for GitHub push events and deploys instantly.

---

## Option 1: GitHub Actions Setup (Recommended)

### Step 1: Generate SSH Key on Your VPS
```bash
# On your VPS as deploy user
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy -N ""

# Add to authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Show private key (you'll need this for GitHub)
cat ~/.ssh/github_deploy
```

### Step 2: Add Secrets to GitHub

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `VPS_HOST`: Your VPS IP address (e.g., `123.456.789.0`)
- `VPS_USER`: `deploy`
- `VPS_SSH_KEY`: The private key from step 1 (entire content including BEGIN/END lines)
- `VPS_PORT`: `22` (or your custom SSH port)

Optional (for notifications):
- `TELEGRAM_BOT_TOKEN`: Your bot token (for deployment notifications)
- `TELEGRAM_CHAT_ID`: Your Telegram user ID

### Step 3: Enable GitHub Actions

The workflow is already in `.github/workflows/auto-deploy.yml`

Now when you push to the `main` branch:
1. GitHub Actions connects to your VPS via SSH
2. Pulls latest code
3. Rebuilds Docker image
4. Restarts containers
5. Sends you a Telegram notification

### That's it! Test it:
```bash
# Make a small change locally
echo "# Test" >> README.md
git add .
git commit -m "Test auto-deployment"
git push origin main

# Watch the deployment in GitHub Actions tab
```

---

## Option 2: Webhook Setup (Advanced - Fastest)

### Step 1: Setup Webhook Listener on VPS
```bash
# On your VPS
cd /home/deploy/telegram-gym-bot

# Create webhook secret
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "Save this secret: $WEBHOOK_SECRET"

# Update the service file with your secret
sudo nano /etc/systemd/system/webhook-deploy.service
# Replace 'your-secret-here' with the generated secret

# Copy service file
sudo cp scripts/webhook-deploy.service /etc/systemd/system/

# Start webhook listener
sudo systemctl daemon-reload
sudo systemctl enable --now webhook-deploy

# Check if it's running
sudo systemctl status webhook-deploy
```

### Step 2: Open Webhook Port
```bash
# Allow webhook port through firewall
sudo ufw allow 9001/tcp
```

### Step 3: Configure GitHub Webhook

1. Go to your GitHub repository → Settings → Webhooks
2. Click "Add webhook"
3. Fill in:
   - **Payload URL**: `http://your-vps-ip:9001/webhook-deploy`
   - **Content type**: `application/json`
   - **Secret**: The secret you generated in Step 1
   - **Events**: Select "Just the push event"
4. Click "Add webhook"

### Step 4: Test
Push any change to the `main` branch and watch the webhook trigger!

```bash
# Monitor webhook logs
sudo journalctl -u webhook-deploy -f
```

---

## How It Works

### GitHub Actions Method:
```
You push code → GitHub Actions runs → SSH to VPS → Pull & rebuild → Deploy
(~2-3 minutes total)
```

### Webhook Method:
```
You push code → GitHub sends webhook → VPS receives → Pull & rebuild → Deploy
(~1-2 minutes total)
```

---

## Comparison

| Feature | GitHub Actions | Webhooks |
|---------|---------------|----------|
| Setup Difficulty | Easy | Medium |
| Speed | 2-3 min | 1-2 min |
| GitHub Secrets Required | Yes | No |
| Open Port Required | No | Yes (9001) |
| Logs Location | GitHub UI | VPS logs |
| Best For | Most users | Advanced users |

---

## Troubleshooting

### GitHub Actions Issues

**Error: Permission denied (publickey)**
- Check that `VPS_SSH_KEY` secret contains the full private key
- Verify the public key is in `/home/deploy/.ssh/authorized_keys`

**Error: Host key verification failed**
- SSH to VPS once manually first to accept the host key
- Or disable strict host checking (less secure)

### Webhook Issues

**Webhook not triggering:**
```bash
# Check if service is running
sudo systemctl status webhook-deploy

# Check logs
sudo journalctl -u webhook-deploy -f

# Test webhook manually
curl -X POST http://localhost:9001/webhook-deploy
```

**Firewall blocking webhook:**
```bash
# Check if port is open
sudo ufw status
sudo netstat -tlnp | grep 9001
```

---

## Security Notes

### For GitHub Actions:
- Use a dedicated SSH key (not your personal one)
- Limit the deploy user's permissions
- Use `fail2ban` to prevent brute force

### For Webhooks:
- Always use a webhook secret
- Consider using Nginx reverse proxy with SSL
- Monitor webhook logs for suspicious activity

---

## Manual Deployment (Fallback)

If auto-deployment fails, you can always deploy manually:

```bash
# SSH to your VPS
ssh deploy@your-vps-ip

# Run deployment
cd telegram-gym-bot
./scripts/deploy.sh
```

---

## Complete Setup Commands Summary

### Quick GitHub Actions Setup:
```bash
# On VPS (one time)
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N ""
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_deploy  # Copy this to GitHub secrets

# On GitHub
# Add secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_PORT

# Test
git push origin main
```

### Quick Webhook Setup:
```bash
# On VPS (one time)
sudo cp /home/deploy/telegram-gym-bot/scripts/webhook-deploy.service /etc/systemd/system/
sudo systemctl enable --now webhook-deploy
sudo ufw allow 9001

# On GitHub
# Add webhook: http://your-vps-ip:9001/webhook-deploy

# Test
git push origin main
```

---

## Congratulations! 🎉

Your bot now deploys automatically when you push to GitHub. No more manual SSH deployments!