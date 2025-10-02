# 🏋️ Telegram Gym Bot

A comprehensive fitness tracking Telegram bot with advanced analytics, multilingual support, and data export capabilities.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Bot](https://img.shields.io/badge/bot-%40profiusgymbot-blue)

## 📌 Current Status (January 2025)

✅ **PRODUCTION READY** - Bot is fully functional and running!

### Recent Major Update
Complete rewrite and enhancement completed on January 14, 2025:
- Fixed all critical bugs and compatibility issues
- Implemented all core features from documentation
- Added 39 pre-loaded exercises with smart search
- Full multi-language support (EN/RU)
- Production-ready architecture

## 🌟 Implemented Features

### ✅ Core Features (Completed)
- **📝 Workout Tracking**: Log exercises with sets, reps, weight, and RPE
- **📚 Exercise Library**: 39 pre-loaded exercises with fuzzy search
- **🌍 Multi-language**: Full support for English and Russian
- **👤 User Management**: Registration, profiles, and preferences
- **⏱ Rest Timers**: Configurable timers with memory
- **📊 Basic Analytics**: Workout history and statistics
- **🗄 Database**: SQLAlchemy with async support
- **🤖 Smart Conversations**: FSM-based workout logging flow
- **🔍 Exercise Search**: Category browsing and fuzzy name matching

### 🚧 Features In Progress
- **📈 Advanced Analytics**: Progress charts and visualizations
- **📤 Data Export**: Excel, PDF, and CSV export functionality
- **🎯 Custom Routines**: Create and manage workout programs
- **🏆 Personal Records**: Automatic PR tracking and notifications
- **👥 Social Features**: Share workouts and compete with friends
- **🥗 Nutrition Tracking**: Meal logging and calorie counting

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/veacheslavv/telegram-gym-bot.git
cd telegram-gym-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_TOKEN
```

4. **Run the bot**
```bash
python run.py
```

### 🤖 Live Bot
The bot is currently running at **[@profiusgymbot](https://t.me/profiusgymbot)**

## 📱 Available Commands

| Command | Description | Status |
|---------|-------------|--------|
| `/start` | Start bot and select language | ✅ Working |
| `/help` | Show available commands | ✅ Working |
| `/log` | Log a workout | ✅ Working |
| `/today` | View today's workouts | ✅ Working |
| `/timer` | Set rest timer | ✅ Working |
| `/stats` | View statistics | ✅ Working |
| `/history` | Workout history | ✅ Working |
| `/profile` | View profile | ✅ Working |
| `/language` | Change language | ✅ Working |
| `/records` | Personal records | 🚧 In Progress |
| `/export` | Export data | 🚧 In Progress |
| `/routines` | Manage routines | 🚧 In Progress |

## 🏗 Architecture

```
telegram-gym-bot/
├── src/
│   ├── bot/           # Bot initialization and configuration
│   ├── handlers/      # Command and message handlers
│   ├── services/      # Business logic services
│   ├── models/        # Database models
│   ├── locales/       # Translation files
│   ├── utils/         # Utility functions
│   └── data/          # Initial data (exercises)
├── tests/             # Test suite
├── docs/              # Documentation
├── docker/            # Docker configuration
└── run.py            # Entry point
```

## 🔧 Technical Stack

- **Framework**: aiogram 3.22.0 (Telegram Bot API)
- **Database**: SQLAlchemy 2.0 with aiosqlite
- **Language**: Python 3.9+
- **Architecture**: Async/await with FSM
- **Deployment**: Docker ready

## 📊 Project Statistics

- **Total Lines of Code**: ~8,000
- **Number of Files**: 88
- **Test Coverage**: ~60% (increasing)
- **Active Contributors**: 6
- **Exercises in Database**: 39

## 🐛 Known Issues

See [GitHub Issues](https://github.com/veacheslavv/telegram-gym-bot/issues) for current bugs and feature requests.

## 🤝 Contributing

We welcome contributions! Please see our [GitHub Workflow Guide](docs/GITHUB_WORKFLOW_GUIDE.md) for details.

### How to Contribute
1. Check [open issues](https://github.com/veacheslavv/telegram-gym-bot/issues)
2. Fork the repository
3. Create feature branch
4. Make your changes
5. Submit pull request

## 👥 Team

| Developer | Responsibility | Status |
|-----------|---------------|--------|
| Cristian | Architecture & Core Features | Active |
| Dev1 | Workout Tracking | ✅ Implemented |
| Dev2 | Exercise Database | ✅ Implemented |
| Dev3 | Progress Charts | 🚧 In Progress |
| Dev4 | Social Features | 📋 Planned |
| Dev5 | Rest Timers | ✅ Implemented |
| Dev6 | Nutrition Tracking | ✅ Implemented |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [aiogram](https://github.com/aiogram/aiogram)
- Inspired by fitness enthusiasts worldwide
- Special thanks to all contributors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/veacheslavv/telegram-gym-bot/issues)
- **Bot**: [@profiusgymbot](https://t.me/profiusgymbot)
- **Documentation**: [Project Docs](docs/)

---

**Last Updated**: January 14, 2025 | **Version**: 1.0.0 | **Status**: Production Ready 🚀