# 🚀 Quick Setup Guide - Run Your Gym Bot

## Step 1: Create Your Telegram Bot

1. **Open Telegram** on your phone or desktop
2. **Search for @BotFather** (official bot to create bots)
3. **Send `/newbot`** command
4. **Choose a name** for your bot (e.g., "My Gym Tracker")
5. **Choose a username** ending in 'bot' (e.g., `mygymtracker_bot`)
6. **Save the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Set Up on Your Mac

### 2.1 Install Python Dependencies

```bash
cd /Users/cristianprodius/Projects/Internship2025/telegram-gym-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2.2 Configure Your Bot Token

```bash
# Create your .env file from the example
cp .env.example .env

# Open .env in your editor
nano .env
# OR
open -e .env
```

**Add your bot token:**
```
TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE
```

Replace `YOUR_BOT_TOKEN_HERE` with the token from BotFather.

## Step 3: Run the Bot

```bash
# Make sure you're in the project directory
cd /Users/cristianprodius/Projects/Internship2025/telegram-gym-bot

# Run the bot
python run.py
```

You should see:
```
2025-01-14 10:00:00 - __main__ - INFO - Starting Telegram Gym Bot...
2025-01-14 10:00:01 - __main__ - INFO - Bot token loaded successfully
2025-01-14 10:00:01 - __main__ - INFO - Database initialized
2025-01-14 10:00:01 - __main__ - INFO - Timer manager started
2025-01-14 10:00:01 - __main__ - INFO - Starting bot polling...
```

## Step 4: Test from Your Phone

1. **Open Telegram on your phone**
2. **Search for your bot** using the username you created (e.g., @mygymtracker_bot)
3. **Start chatting** with `/start`

### Available Commands to Test:

```
/start - Start the bot
/help - See all commands
/log - Log a workout
/timer - Set rest timer
/stats - View statistics
/export - Export your data
```

## 📱 Testing Workflow

### Test 1: Basic Commands
1. Send `/start` - You should get a welcome message
2. Send `/help` - You should see all available commands

### Test 2: Log a Workout
1. Send `/log`
2. Select an exercise from the list
3. Choose number of sets
4. Enter reps and weight for each set

### Test 3: Rest Timer
1. Send `/timer`
2. Use buttons to set time
3. Press Start to begin timer

### Test 4: View Progress
1. Send `/today` - See today's workouts
2. Send `/stats` - See your statistics

## 🔧 Troubleshooting

### Issue: "TELEGRAM_TOKEN not found"
**Solution:** Make sure your .env file has the correct token:
```bash
cat .env | grep TELEGRAM_TOKEN
```

### Issue: "No module named 'aiogram'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Bot doesn't respond
**Solution:** Check if bot is running:
```bash
# Check if Python process is running
ps aux | grep python

# Check logs
tail -f bot.log
```

## 🌐 Keep Bot Running 24/7

### Option 1: Keep Terminal Open
Simply leave the terminal window open on your Mac.

### Option 2: Run in Background
```bash
# Run with nohup
nohup python run.py > output.log 2>&1 &

# Check if running
ps aux | grep run.py

# Stop the bot
pkill -f run.py
```

### Option 3: Use Screen (Recommended)
```bash
# Install screen if not available
brew install screen

# Start new screen session
screen -S gymbot

# Run the bot
python run.py

# Detach from screen (Ctrl+A, then D)
# To reattach later:
screen -r gymbot
```

## 📊 Monitor Your Bot

### View Logs
```bash
# Real-time logs
tail -f bot.log

# Last 50 lines
tail -n 50 bot.log
```

### Check Database
```bash
# Install sqlite3 if needed
brew install sqlite

# View database
sqlite3 main/gymbot.db
.tables
.quit
```

## 🚀 Advanced: Deploy to Cloud (Free Options)

### Option 1: Railway.app (Easiest)
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Add environment variables
4. Deploy automatically

### Option 2: Heroku Free Tier Alternative - Render.com
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub
4. Add environment variables
5. Deploy

### Option 3: Oracle Cloud (Always Free)
1. Sign up for Oracle Cloud Free Tier
2. Create compute instance
3. SSH and install bot
4. Run with systemd

## 📝 Quick Commands Reference

```bash
# Start bot
python run.py

# Stop bot (Ctrl+C)

# Run in background
nohup python run.py &

# Check if running
ps aux | grep python

# View logs
tail -f bot.log

# Kill background process
pkill -f run.py
```

## ✅ Success Checklist

- [ ] Created bot with @BotFather
- [ ] Got bot token
- [ ] Added token to .env file
- [ ] Installed dependencies
- [ ] Bot is running on Mac
- [ ] Can interact with bot from phone
- [ ] Bot responds to commands

## Need Help?

If you encounter issues:
1. Check the bot.log file for errors
2. Ensure all dependencies are installed
3. Verify your bot token is correct
4. Make sure no other instance is running

Happy training! 💪