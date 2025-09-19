#!/usr/bin/env python3
"""
Quick test script to verify bot setup
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all required packages are installed"""
    required = ['aiogram', 'sqlalchemy', 'pandas', 'matplotlib', 'fuzzywuzzy']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    return True

def check_token():
    """Check if bot token is configured"""
    token = os.getenv("TELEGRAM_TOKEN")

    if not token:
        print("❌ TELEGRAM_TOKEN not found in .env file")
        print("\n📝 To fix:")
        print("1. Create .env file: cp .env.example .env")
        print("2. Add your token: TELEGRAM_TOKEN=your_token_here")
        return False

    if token == "your_bot_token_here":
        print("❌ You need to replace the example token with your real bot token")
        print("\n📝 Get your token from @BotFather on Telegram")
        return False

    # Hide most of the token for security
    hidden_token = token[:10] + "..." + token[-4:]
    print(f"✅ Bot token configured: {hidden_token}")
    return True

async def test_bot_connection():
    """Test if bot can connect to Telegram"""
    from aiogram import Bot

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        return False

    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        print(f"   Bot name: {bot_info.first_name}")
        print(f"   Bot ID: {bot_info.id}")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")
        print("\n📝 Check that your token is correct")
        return False

def check_database():
    """Check if database can be initialized"""
    try:
        from src.database.connection import Base
        from sqlalchemy import create_engine

        engine = create_engine("sqlite:///test.db")
        Base.metadata.create_all(engine)

        # Clean up test database
        import os
        if os.path.exists("test.db"):
            os.remove("test.db")

        print("✅ Database system working")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all checks"""
    print("🏋️ Telegram Gym Bot - Setup Checker\n")
    print("=" * 50)

    all_good = True

    # Check 1: Requirements
    print("\n📦 Checking Python packages...")
    if not check_requirements():
        all_good = False

    # Check 2: Token
    print("\n🔑 Checking bot token...")
    if not check_token():
        all_good = False
        print("\n⚠️  Cannot continue without a valid token")
        return

    # Check 3: Database
    print("\n💾 Checking database...")
    if not check_database():
        all_good = False

    # Check 4: Bot connection
    print("\n🤖 Testing bot connection...")
    if not asyncio.run(test_bot_connection()):
        all_good = False

    print("\n" + "=" * 50)

    if all_good:
        print("✅ All checks passed! Your bot is ready to run.")
        print("\n🚀 Start your bot with: python run.py")
        print("\n📱 Then open Telegram on your phone and search for your bot!")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Need help? Check SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()