# 🏠 UK Flathunter v1.0.0 - First Stable Release

**Automate your UK rental property search with AI-powered intelligence.**

## 🎉 What's New

This is the first stable release of UK Flathunter, a modern fork optimized for UK property hunting with enterprise-grade architecture and optional AI capabilities.

### ✨ Key Features

#### 🌍 Multi-Country Property Search
- **UK**: Zoopla, Rightmove
- **Germany**: ImmoScout24, WG-Gesucht, Kleinanzeigen, Immowelt, VRM Immo
- **Italy**: Immobiliare.it, Subito, Idealista
- **Spain**: Idealista

#### 🤖 AI-Powered Analysis (Optional)
- Smart property scoring (0-10 ratings)
- Intelligent pros/cons analysis
- Red flag detection
- Personalized recommendations
- Cost-optimized with Claude Haiku 4.5 (~$0.001/property)

#### 🔔 Flexible Notifications
- Telegram (recommended)
- Slack
- Mattermost
- 80+ services via Apprise (Discord, Email, WhatsApp, etc.)
- File output for testing

#### 🎯 Smart Filtering
- Price, size, and room filters
- Title exclusion patterns
- Price per square meter limits
- Custom filter combinations

#### 🔒 Secure Configuration
- Environment variables via .env
- Safe version control (config.yaml has no secrets)
- Type-safe configuration validation

## 🚀 Quick Start

```bash
# Install
git clone https://github.com/OrestisIon/uk-flathunter.git
cd uk-flathunter
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your Telegram bot token

# Run
python flathunt.py --config config.yaml
```

See [SETUP.md](SETUP.md) for detailed instructions.

## 📚 Documentation

- **[README.md](README.md)** - Quick start guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Developer documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Full release notes

## 🏗️ Architecture Highlights

- **Factory Pattern**: Easy plugin registration
- **Repository Pattern**: Clean data persistence
- **Type Safety**: Full type hints with dataclasses
- **Protocol Interfaces**: Well-defined extension points
- **Modern Python**: 3.10+ with latest best practices

## 🐳 Deployment

- Docker (Compose and plain)
- Google Cloud (App Engine, Cloud Run)
- Linux systemd service
- Local development

## 🔧 Technical Details

### Dependencies
- Python 3.10+
- BeautifulSoup4, Selenium
- python-dotenv
- Anthropic SDK (optional, for AI features)

### Bot Detection Handling
- Headless Chrome integration
- Captcha solving (2Captcha, Capmonster, ImageTyperz)
- Cookie injection support
- Proxy rotation

## 📊 What's Inside

- **10 Crawlers** supporting 4 countries
- **5 Built-in notifiers** + Apprise
- **100% type-hinted** core modules
- **Comprehensive tests** with good coverage
- **Developer-friendly** architecture

## 🙏 Credits

Based on the original [Flathunters](https://github.com/flathunters/flathunter) project, enhanced with UK support, modern architecture, and AI capabilities.

## 🐛 Known Issues

- ImmoScout24 requires Capmonster for captcha solving
- macOS may need SSL certificate installation
- Some sites may rate-limit aggressive crawling

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**Happy house hunting!** 🏡

Found this useful? ⭐ Star the repo and share with friends searching for rentals!
