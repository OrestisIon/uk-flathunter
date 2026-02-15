# Changelog

All notable changes to UK Flathunter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-15

### 🎉 Initial Release

First stable release of UK Flathunter - a fork optimized for UK property hunting with modern architecture and AI capabilities.

### ✨ Features

#### Multi-Country Support
- **UK Sites**: Zoopla, Rightmove
- **Germany Sites**: ImmoScout24, WG-Gesucht, Kleinanzeigen, Immowelt, VRM Immo
- **Italy Sites**: Immobiliare.it, Subito, Idealista
- **Spain Sites**: Idealista

#### Modern Architecture
- **Factory Pattern**: Plugin-based crawler and notifier registration
- **Repository Pattern**: Clean separation of persistence layer
- **Domain Models**: Type-safe dataclasses with IDE support
- **Protocol Interfaces**: Well-defined contracts for extensions
- **Type Safety**: Full type hints throughout codebase

#### Notification Services
- Telegram bot integration
- Slack webhooks
- Mattermost webhooks
- Apprise (80+ services: Discord, Email, WhatsApp, etc.)
- File output for testing/debugging

#### Smart Filtering
- Price range filtering
- Size (square meters) filtering
- Number of rooms filtering
- Title exclusion (regex support)
- Price per square meter limits
- Custom filter combinations

#### AI-Powered Features (Optional)
- **Property Scoring**: AI rates properties 0-10 for value
- **Intelligent Analysis**: Reasoning about pros/cons
- **Red Flag Detection**: Identifies potential issues
- **Personalized Recommendations**: Based on user priorities
- **Concurrent Processing**: Batch analysis for efficiency
- **Cost Optimized**: Uses Claude Haiku 4.5 by default (~$0.001/property)

#### Bot Detection Handling
- Headless Chrome/Selenium integration
- Captcha solving (2Captcha, Capmonster, ImageTyperz)
- Cookie injection for bot detection bypass
- Proxy rotation support
- User-agent spoofing

#### Configuration
- **Environment Variables**: Secure credential management via .env
- **YAML Config**: Clean, version-controllable configuration
- **Type-Safe Settings**: Validated configuration with defaults
- **Environment Overrides**: Easy deployment configuration

#### Deployment Options
- Docker support (Compose and plain Docker)
- Google Cloud Platform (App Engine, Cloud Run)
- Systemd service for Linux servers
- Local development mode

### 📚 Documentation

- **README.md**: User-friendly quick start guide
- **SETUP.md**: Detailed setup and configuration instructions
- **CONTRIBUTING.md**: Comprehensive developer documentation
- **LLM_INTEGRATION_GUIDE.md**: AI features setup and usage
- **Examples**: Sample configurations for common use cases

### 🔧 Technical Improvements

#### Code Quality
- Type hints throughout codebase
- Protocol-based interfaces for extensibility
- Comprehensive test suite
- Linting with pylint and pyright
- Code coverage tracking

#### Performance
- Async LLM processing (10 properties concurrently)
- Thread-safe database connections
- Lazy crawler initialization
- Efficient batch processing pipeline

#### Developer Experience
- Clear separation of concerns
- Easy to add new crawlers (just register in factory)
- Easy to add new notifiers (just register in factory)
- Well-documented architecture
- Examples for common extensions

### 🔒 Security

- Credentials stored in gitignored .env file
- config.yaml safe for version control
- No hardcoded secrets in codebase
- Secure credential loading with python-dotenv
- Environment variable validation

### 📦 Dependencies

- Python 3.10+
- BeautifulSoup4 for HTML parsing
- Selenium for browser automation
- python-dotenv for environment management
- Anthropic SDK for AI features (optional)
- Various notifier-specific libraries

### 🐛 Known Issues

- ImmoScout24 bot detection can be challenging (requires Capmonster)
- Some sites may rate-limit aggressive crawling
- macOS may require SSL certificate installation
- First-time Chrome driver download can be slow

### 🚀 Migration from Original Flathunter

This fork maintains backward compatibility with original Flathunter configurations:

1. **Config File**: Existing config.yaml files work with minimal changes
2. **Database**: Uses same SQLite schema (processed_ids.db compatible)
3. **Notifiers**: All original notifiers supported
4. **Crawlers**: All original German/Italian/Spanish crawlers included

**New features to adopt:**
- Move sensitive credentials to .env file (see SETUP.md)
- Optional: Enable LLM features for AI-powered scoring
- Optional: Use new factory-based crawler registration

### 📊 Statistics

- **10 Crawlers**: Supporting 4 countries
- **5 Notifiers**: Plus 80+ via Apprise
- **239 Lines**: User-friendly README (70% reduction from fork source)
- **Type Safe**: 100% type-hinted core modules
- **Well Tested**: Comprehensive test coverage

### 🙏 Credits

Based on the original [Flathunters](https://github.com/flathunters/flathunter) project.

Enhanced with:
- UK site support (Zoopla, Rightmove)
- Modern architecture patterns
- AI integration
- Improved documentation
- Security enhancements

---

## Release Notes Format

**Added**: New features
**Changed**: Changes in existing functionality
**Deprecated**: Soon-to-be removed features
**Removed**: Removed features
**Fixed**: Bug fixes
**Security**: Vulnerability fixes

---

[1.0.0]: https://github.com/OrestisIon/uk-flathunter/releases/tag/v1.0.0
