# 🏋️ Telegram Gym Bot

A comprehensive fitness tracking Telegram bot with advanced analytics, multilingual support, and data export capabilities.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen)

## 🌟 Features

### Core Functionality
- **📝 Workout Tracking**: Log exercises with sets, reps, weight, and RPE
- **📚 Exercise Library**: 40+ pre-loaded exercises with fuzzy search
- **📊 Progress Analytics**: Volume progression, weak point analysis, and AI recommendations
- **🎯 Custom Routines**: Create and manage personalized workout programs
- **⏱ Rest Timers**: Configurable rest periods with memory management
- **🌍 Multilingual**: Full support for English and Russian
- **📤 Data Export**: Export to Excel, PDF, and CSV formats
- **📈 Visualizations**: Progress charts, heatmaps, and muscle distribution graphs
- **🏆 Personal Records**: Automatic PR tracking and notifications

### Technical Features
- **Async Architecture**: Built with aiogram 3.x for high performance
- **Database Support**: SQLAlchemy with SQLite/PostgreSQL
- **Memory Management**: Automatic cleanup and resource optimization
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Docker Support**: Containerized deployment with docker-compose
- **Test Coverage**: 85%+ coverage with unit and integration tests

## Quick Start

### Prerequisites
- Python 3.9+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/veacheslavv/telegram-gym-bot.git
cd telegram-gym-bot
```

2. **Set up virtual environment**
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your TELEGRAM_TOKEN
```

5. **Initialize database**
```bash
python -c "from main.feature.dev1_workout_tracking.db import init_db; init_db()"
```

6. **Run the bot**
```bash
python main/main.py
```

## Usage

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot and see welcome message | `/start` |
| `/help` | Show available commands | `/help` |
| `/log` | Log a workout | `/log BenchPress 3x10x50` |
| `/today` | View today's workouts | `/today` |
| `/timer` | Set a rest timer | `/timer` |

### Logging Workouts

Format: `/log [Exercise] [Sets]x[Reps]x[Weight]`

Examples:
- `/log BenchPress 3x10x50` - 3 sets of 10 reps with 50kg
- `/log Squats 5x5x100` - 5 sets of 5 reps with 100kg
- `/log PullUps 4x8x0` - 4 sets of 8 bodyweight pull-ups

## Project Structure

```
telegram-gym-bot/
├── main/
│   ├── main.py                 # Bot entry point
│   └── feature/                # Feature modules
│       ├── dev1_workout_tracking/
│       └── dev5_rest_timers/
├── src/                        # Source code
│   ├── models/                 # Data models
│   └── utils/                  # Utility functions
├── tests/                      # Test files
├── docs/                       # Documentation
│   ├── PROJECT_ANALYSIS.md    # Detailed project analysis
│   └── GITHUB_WORKFLOW_GUIDE.md # Team workflow guide
└── requirements.txt            # Python dependencies
```

## Development

### Setting Up Development Environment

1. **Install development dependencies**
```bash
pip install pytest black isort flake8 mypy
```

2. **Run tests**
```bash
pytest tests/
```

3. **Format code**
```bash
black src/ main/
isort src/ main/
```

4. **Check code quality**
```bash
flake8 src/ main/
mypy src/ main/
```

### Contributing

Please read our [GitHub Workflow Guide](docs/GITHUB_WORKFLOW_GUIDE.md) for details on our development process and how to submit pull requests.

#### Quick Contribution Guide

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Branch Strategy

- `main` - Production branch
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fixes

## Team

| Developer | Primary Responsibility |
|-----------|----------------------|
| Dev1 | Workout Tracking |
| Dev2 | Exercise Database |
| Dev3 | Progress Charts |
| Dev4 | Social Features |
| Dev5 | Rest Timers |
| Dev6 | Nutrition Tracking |

## Documentation

- [Project Analysis & Recommendations](docs/PROJECT_ANALYSIS.md) - Detailed analysis of current state and improvement roadmap
- [GitHub Workflow Guide](docs/GITHUB_WORKFLOW_GUIDE.md) - Team collaboration and development workflow
- [API Documentation](docs/API.md) - Coming soon

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=main

# Run specific test file
pytest tests/unit/test_workout.py
```

## Deployment

### Local Deployment
Follow the Quick Start guide above.

### Production Deployment

1. **Using Docker** (Recommended)
```bash
docker build -t gym-bot .
docker run -d --name gym-bot --env-file .env gym-bot
```

2. **Using systemd** (Linux)
```bash
sudo cp gym-bot.service /etc/systemd/system/
sudo systemctl enable gym-bot
sudo systemctl start gym-bot
```

### Environment Variables

See [.env.example](.env.example) for all available configuration options.

Key variables:
- `TELEGRAM_TOKEN` - Your bot token (required)
- `DATABASE_URL` - Database connection string
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level (INFO, DEBUG, ERROR)

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if TELEGRAM_TOKEN is set correctly
   - Verify bot is running: `ps aux | grep main.py`
   - Check logs for errors

2. **Database errors**
   - Ensure database is initialized: `python -c "from main.feature.dev1_workout_tracking.db import init_db; init_db()"`
   - Check database permissions

3. **Import errors**
   - Verify virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Support

- **Issues**: [GitHub Issues](https://github.com/veacheslavv/telegram-gym-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/veacheslavv/telegram-gym-bot/discussions)
- **Team Chat**: Slack #gym-bot-dev

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors
- Built with [aiogram](https://github.com/aiogram/aiogram)
- Inspired by fitness enthusiasts worldwide

---

**Stay fit, code strong! 💪🚀**