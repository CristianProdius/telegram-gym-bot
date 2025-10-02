# 📋 Deployment Checklist

## GitHub Secrets Setup

Make sure you have added these secrets in your GitHub repository:
https://github.com/CristianProdius/telegram-gym-bot/settings/secrets/actions

### Required Secrets:
- [ ] `VPS_HOST` - Your VPS IP address (e.g., `123.45.67.89`)
- [ ] `VPS_USER` - Should be `deploy`
- [ ] `VPS_SSH_KEY` - Your SSH private key (see below how to generate)

### Optional (for notifications):
- [ ] `TELEGRAM_BOT_TOKEN` - Your bot token
- [ ] `TELEGRAM_CHAT_ID` - Your Telegram user ID

## Generate SSH Key for GitHub Actions

Run these commands on your VPS as the deploy user:

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Switch to deploy user
su - deploy

# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions -N ""

# Add to authorized keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Display the private key (copy ALL of this including BEGIN and END lines)
cat ~/.ssh/github_actions
```

Copy the ENTIRE output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) and paste it as the `VPS_SSH_KEY` secret in GitHub.

## Test Deployment

1. Check GitHub Actions is running:
   https://github.com/CristianProdius/telegram-gym-bot/actions

2. Make a small test change:
   ```bash
   echo "# Deployment test" >> README.md
   git add README.md
   git commit -m "test: Testing auto-deployment"
   git push origin main
   ```

3. Watch the deployment in GitHub Actions tab

## Troubleshooting

### If deployment fails with "Permission denied":
- Make sure the SSH key is correctly added to GitHub secrets
- Verify the public key is in `/home/deploy/.ssh/authorized_keys` on VPS
- Check that `VPS_USER` is set to `deploy`

### If deployment fails with "Host key verification failed":
- First SSH manually from your local machine to accept the host key:
  ```bash
  ssh deploy@your-vps-ip
  ```

### If deployment succeeds but bot doesn't work:
- SSH into VPS and check logs:
  ```bash
  cd /home/deploy/telegram-gym-bot
  docker compose -f docker-compose.production.yml logs -f bot
  ```

### Common Issues:
1. **Repository not found**: Make sure the repo is cloned on VPS first
2. **Scripts not executable**: The workflow now handles this automatically
3. **Docker not installed**: Run the vps-setup.sh script first
4. **Wrong directory**: Ensure bot is in `/home/deploy/telegram-gym-bot`

## Manual Deployment (Backup Option)

If auto-deployment isn't working, you can always deploy manually:

```bash
ssh deploy@your-vps-ip
cd telegram-gym-bot
git pull origin main
./scripts/deploy.sh
```

## Success Indicators

✅ GitHub Actions shows green checkmark
✅ No error messages in the Actions log
✅ Bot responds to `/start` command in Telegram
✅ Docker containers are running on VPS

Check container status:
```bash
docker compose -f docker-compose.production.yml ps
```

All containers should show "Up" status.