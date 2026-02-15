# Flathunter Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Flathunter uses a `.env` file for sensitive credentials that should never be committed to version control.

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required environment variables:**

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (if using Telegram notifier)
- `TELEGRAM_RECEIVER_IDS` - Comma-separated list of Telegram user IDs to notify

**Optional environment variables:**

- `SLACK_WEBHOOK_URL` - Slack webhook URL (if using Slack notifier)
- `LLM_API_KEY` - Anthropic API key for AI property scoring
- `2CAPTCHA_KEY` / `CAPMONSTER_KEY` - Captcha solving service keys (for ImmoScout24)
- `GOOGLE_MAPS_API_KEY` - Google Maps API key for distance calculations

See `.env.example` for the complete list of available variables.

### 3. Configure Search URLs

Edit `config.yaml` to add your property search URLs:

```yaml
urls:
  - https://www.immobilienscout24.de/Suche/...
  - https://www.rightmove.co.uk/property-to-rent/...
  - https://www.zoopla.co.uk/to-rent/...
```

**Note:** `config.yaml` can be safely committed to version control as it contains no sensitive data. All secrets are in `.env`.

### 4. Run Flathunter

```bash
# Single run (check once and exit)
python flathunt.py --config config.yaml

# Continuous mode (loop every 10 minutes)
# First, enable loop in config.yaml:
# loop:
#   active: yes
#   sleeping_time: 600
python flathunt.py --config config.yaml
```

## Environment Variables vs config.yaml

**Use `.env` for:**
- API keys and tokens
- Webhook URLs
- Passwords and sensitive credentials
- User IDs

**Use `config.yaml` for:**
- Search URLs
- Filter settings (price, size, rooms)
- Loop configuration
- Message format
- Feature flags (headless browser, verbose logging)

Environment variables **override** config.yaml values, so you can:
- Share `config.yaml` in version control
- Each developer/deployment uses their own `.env` file
- Change settings without modifying code

## Supported Notifiers

Configure in `config.yaml`:

```yaml
notifiers:
  - telegram  # Requires TELEGRAM_BOT_TOKEN in .env
  - slack     # Requires SLACK_WEBHOOK_URL in .env
  - file      # No credentials needed, saves to JSON file
```

## LLM Integration (Optional)

To enable AI-powered property scoring:

1. Get an Anthropic API key from https://console.anthropic.com
2. Add to `.env`:
   ```bash
   LLM_API_KEY=sk-ant-api03-...
   LLM_ENABLED=true
   ```
3. Uncomment the `llm` section in `config.yaml`

See `docs/LLM_INTEGRATION_GUIDE.md` for details.

## Troubleshooting

### SSL Certificate Errors (macOS)

If you see SSL certificate errors when running crawlers:

```bash
/Applications/Python*/Install\ Certificates.command
```

### No properties found

- Verify your search URLs work in a browser
- Enable verbose logging: `verbose: true` in config.yaml
- Check that crawlers are registered for your URLs
- Some sites require captcha solving (add API key to .env)

### Telegram not sending

- Verify `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Verify `TELEGRAM_RECEIVER_IDS` contains your user ID
- Get your user ID by messaging @userinfobot on Telegram

## Directory Structure

```
flathunter/
├── .env              # Your secrets (gitignored, not committed)
├── .env.example      # Template for .env (committed)
├── config.yaml       # Public config (committed)
├── flathunt.py       # Main entry point
├── flathunter/       # Source code
│   ├── config/       # Configuration system
│   ├── crawler/      # Website crawlers
│   ├── notifiers/    # Notification services
│   ├── llm/          # AI integration
│   └── ...
├── deployment/       # Docker, requirements, systemd
├── scripts/          # Development tools
└── docs/             # Documentation
```

## Next Steps

- Read `docs/LLM_INTEGRATION_GUIDE.md` for AI features
- Check `deployment/README.md` for production deployment
- See `README.md` for architecture overview
