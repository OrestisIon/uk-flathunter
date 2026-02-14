# Configuration Examples

This directory contains example configuration files and templates.

## Files

- **config.yaml.dist** - Distribution template for config.yaml with all options documented

## Usage

### Quick Start

Copy the example config and customize it:

```bash
cp docs/examples/config.yaml.dist config.yaml
# Edit config.yaml with your search URLs and notification settings
```

### Or Use the Wizard

For an interactive setup experience:

```bash
python scripts/config_wizard.py
```

## Configuration Documentation

See the main [README.md](../../README.md#configuration) for detailed configuration instructions.

### Key Sections

1. **urls** - Your property search URLs from ImmoScout24, Zoopla, etc.
2. **notifiers** - Choose from: telegram, slack, mattermost, apprise, file
3. **filters** - Price, size, rooms, excluded titles
4. **captcha** - API keys for captcha solving services (for ImmoScout24)
5. **google_maps_api** - Distance calculation (optional, requires API key)

### Example Minimal Config

```yaml
urls:
  - https://www.zoopla.co.uk/to-rent/...

notifiers:
  - telegram

telegram:
  bot_token: YOUR_BOT_TOKEN
  receiver_ids:
    - YOUR_CHAT_ID
```
