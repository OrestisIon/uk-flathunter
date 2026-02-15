# UK Flathunter 🏠🤖

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat)](https://github.com/RichardLitt/standard-readme)
[![Lint Code Base](https://github.com/OrestisIon/uk-flathunter/actions/workflows/linter.yml/badge.svg)](https://github.com/OrestisIon/uk-flathunter/actions/workflows/linter.yml)
[![Tests](https://github.com/OrestisIon/uk-flathunter/actions/workflows/tests.yml/badge.svg)](https://github.com/OrestisIon/uk-flathunter/actions/workflows/tests.yml)

**A bot to automate your rental property search across multiple listing sites.**

Stop manually checking the same property sites every day. Flathunter monitors rental listings for you and sends instant notifications when new properties matching your criteria become available.

## ✨ Features

- 🌍 **Multi-country support**: UK (Zoopla, Rightmove), Germany (ImmoScout24, WG-Gesucht, etc.), Italy, Spain
- 🔔 **Instant notifications**: Telegram, Slack, Mattermost, or 80+ services via Apprise
- 🤖 **AI-powered scoring** (optional): Get intelligent property recommendations using Claude AI
- 🎯 **Smart filtering**: Price, size, rooms, location, and custom exclusions
- 🕒 **Continuous monitoring**: Automatic scanning at your preferred interval
- 🐳 **Easy deployment**: Docker, Google Cloud, or systemd service

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/OrestisIon/uk-flathunter.git
cd uk-flathunter

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy environment template and add your credentials
cp .env.example .env
nano .env  # Add your Telegram bot token, etc.

# Edit search URLs and preferences
nano config.yaml
```

**Minimum config needed:**
- Add your property search URLs from Rightmove, Zoopla, etc.
- Set up a Telegram bot (see [Setup Guide](SETUP.md#telegram))
- Add your Telegram user ID to receive notifications

### 3. Run

```bash
# Single scan
python flathunt.py --config config.yaml

# Continuous monitoring (enable loop in config.yaml first)
python flathunt.py --config config.yaml
```

That's it! You'll receive notifications when new properties appear. 🎉

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup instructions and configuration guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Developer docs, architecture, and how to contribute
- **[docs/LLM_INTEGRATION_GUIDE.md](docs/LLM_INTEGRATION_GUIDE.md)** - AI-powered property scoring setup

## 🌐 Supported Sites

### United Kingdom
- [Zoopla](https://www.zoopla.co.uk)
- [Rightmove](https://www.rightmove.co.uk)

### Germany
- [ImmoScout24](https://www.immobilienscout24.de)
- [WG-Gesucht](https://www.wg-gesucht.de)
- [Kleinanzeigen](https://www.kleinanzeigen.de)
- [Immowelt](https://www.immowelt.de)
- [VRM Immo](https://www.vrm-immo.de)

### Italy
- [Immobiliare.it](https://www.immobiliare.it)
- [Subito](https://www.subito.it)
- [Idealista Italy](https://www.idealista.it)

### Spain
- [Idealista Spain/Portugal](https://www.idealista.com)

## 🔧 Configuration Example

Create searches on your favorite property site, then copy the URL into `config.yaml`:

```yaml
urls:
  # UK example - Rightmove search for WC1, max £2500/month
  - https://www.rightmove.co.uk/property-to-rent/find.html?searchLocation=WC1...

  # Germany example - ImmoScout24 search in Berlin
  - https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten...

# Get notifications via Telegram
notifiers:
  - telegram

# Filter unwanted listings
filters:
  max_price: 2500
  min_size: 50
  excluded_titles:
    - "commercial"
    - "office space"
```

See [SETUP.md](SETUP.md) for complete configuration options.

## 🤖 AI Features (Optional)

Enable AI-powered property analysis to get:
- **Value scores** (0-10) for each property
- **Intelligent reasoning** about pros and cons
- **Red flag detection** (poor condition, hidden fees, etc.)
- **Personalized recommendations** based on your priorities

Just add an Anthropic API key to your `.env` file. See [LLM Integration Guide](docs/LLM_INTEGRATION_GUIDE.md).

## 📱 Notification Services

Configure your preferred notification method in `config.yaml`:

- **Telegram** (recommended) - Free, instant, works worldwide
- **Slack** - Great for team searches
- **Mattermost** - Self-hosted alternative
- **Apprise** - Supports 80+ services (Discord, WhatsApp, Email, etc.)
- **File** - Local JSON output for testing

## 🐳 Deployment Options

### Docker (Recommended)

```bash
# With Docker Compose
docker compose -f deployment/docker-compose.yaml up

# Or with plain Docker
docker build -t flathunter -f deployment/Dockerfile .
docker run --mount type=bind,source=$PWD/config.yaml,target=/config.yaml \
  flathunter python flathunt.py -c /config.yaml
```

### Linux Server (systemd)

```bash
# Copy and configure service file
sudo cp deployment/sample-flathunter.service /lib/systemd/system/flathunter.service
sudo nano /lib/systemd/system/flathunter.service

# Enable and start
sudo systemctl enable flathunter --now
```

### Google Cloud

Deploy to Google App Engine or Cloud Run for free-tier hosting. See [CONTRIBUTING.md](CONTRIBUTING.md#google-cloud-deployment).

## 🛠️ Development

Want to add support for a new property site or contribute to the project?

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Check out the developer docs
open CONTRIBUTING.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Architecture overview
- How to add new crawlers
- Testing guidelines
- Deployment guides

## ⚠️ Bot Detection & Captchas

Some sites (especially ImmoScout24) use bot detection. Flathunter handles this by:

- **Headless Chrome**: Simulates real browser behavior
- **Captcha solving**: Integration with 2Captcha, Capmonster, ImageTyperz
- **Cookie injection**: Bypass detection with valid browser cookies
- **Proxy support**: Rotate IPs to avoid rate limiting

See [SETUP.md](SETUP.md#bot-detection) for configuration.

## 📊 How It Works

1. **Configure** your search criteria and notification preferences
2. **Flathunter crawls** property sites at your chosen interval
3. **New listings** are filtered based on your criteria
4. **Notifications sent** instantly via Telegram/Slack/etc.
5. **Already-seen properties** are tracked to avoid duplicates

```
Config → Crawlers → Filters → AI Scoring (optional) → Notifications
```

## 🤝 Contributing

We welcome contributions! Whether you want to:

- Add support for a new property site
- Improve bot detection handling
- Fix bugs or add features
- Improve documentation

Check out [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original [flathunters](https://github.com/flathunters/flathunter) project and community
- All [contributors](https://github.com/flathunters/flathunter/graphs/contributors)

## ⭐ Support

If Flathunter helps you find your perfect home, please:
- ⭐ Star this repository
- 🐛 Report bugs via [Issues](https://github.com/OrestisIon/uk-flathunter/issues)
- 💬 Share your experience in [Discussions](https://github.com/OrestisIon/uk-flathunter/discussions)

---

**Happy house hunting!** 🏡
