# Contributing to Flathunter

Thank you for your interest in contributing to Flathunter! This guide covers technical details for developers.

## Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Deployment](#deployment)
- [Code Style](#code-style)

## Development Setup

### Prerequisites

- Python 3.10+
- pipenv (recommended) or pip
- Google Chrome / Chromium (for crawlers that need browser automation)
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/flathunters/flathunter.git
   cd flathunter
   ```

2. **Install dependencies:**
   ```bash
   # Using pipenv (recommended)
   pipenv install --dev
   pipenv shell

   # Or using pip
   pip install -r requirements.txt
   pip install -e .  # Install in editable mode
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

4. **Create test configuration:**
   ```bash
   cp docs/examples/config.yaml.dist config.yaml
   # Edit config.yaml with test URLs
   ```

### Running Locally

```bash
# Single crawl run
python flathunt.py --config config.yaml

# Web interface
python main.py
# or
FLASK_APP=flathunter.web flask run

# With verbose logging
python flathunt.py --config config.yaml -v
```

### Platform-Specific Notes

**Linux (CentOS/RHEL):**
```bash
# If using SELinux
chcon -R -t bin_t /home/flathunter/.local/bin/pipenv
```

**macOS:**
```bash
# Fix SSL certificate issues
/Applications/Python*/Install\ Certificates.command
```

---

## Architecture Overview

Flathunter uses a modular, plugin-based architecture with modern Python design patterns.

### Core Design Principles

1. **Separation of Concerns** - Business logic, persistence, and external integrations are clearly separated
2. **Plugin Architecture** - Crawlers and notifiers can be registered dynamically
3. **Type Safety** - Domain models use dataclasses with type hints
4. **Dependency Inversion** - Components depend on abstract interfaces (Protocols)
5. **Backward Compatibility** - All refactoring maintains compatibility

### Directory Structure

```
flathunter/
├── app/                    # Application entry points
│   └── hunter.py          # Main application logic
├── config/                 # Configuration management
│   ├── settings.py         # Typed configuration dataclass
│   ├── crawler_factory.py  # Factory for crawler registration
│   └── notifier_factory.py # Factory for notifier registration
├── core/                   # Core abstractions and utilities
│   ├── abstract_crawler.py # Base crawler class
│   ├── abstract_notifier.py # Base notifier class
│   ├── abstract_processor.py # Base processor class
│   └── config.py           # Legacy config (uses factories)
├── crawler/                # Website-specific crawlers
│   ├── germany/            # ImmoScout24, WG-Gesucht, Kleinanzeigen, Immowelt, VrmImmo
│   ├── uk/                 # Zoopla, Rightmove
│   ├── italy/              # Immobiliare, Subito
│   └── spain/              # Idealista
├── domain/                 # Domain models
│   └── models.py           # Expose dataclass with type safety
├── llm/                    # LLM integration
│   ├── property_scorer.py  # AI-powered property scoring
│   └── enrichment.py       # Feature extraction
├── notifiers/              # Notification service integrations
│   ├── telegram.py
│   ├── slack.py
│   ├── mattermost.py
│   ├── apprise.py
│   └── file.py
├── persistence/            # Database and storage
│   └── idmaintainer.py     # SQLite database management
├── ports/                  # Interface definitions (Protocols)
│   ├── crawler.py          # CrawlerPort protocol
│   ├── notifier.py         # NotifierPort protocol
│   └── repository.py       # RepositoryPort protocol
├── processing/             # Processing pipeline
│   ├── processor.py        # Chain-of-responsibility pattern
│   └── default_processors.py
├── repositories/           # Repository pattern implementations
│   └── expose_repository.py # SQLite repository for exposes
└── web/                    # Flask web interface
```

### Key Components

#### 1. Domain Models (`flathunter/domain/`)

Type-safe domain objects representing core business entities:

```python
from flathunter.domain.models import Expose

expose = Expose(
    id=12345,
    url="https://example.com/property/12345",
    title="Beautiful 2-bedroom flat",
    price="1200€",
    crawler="immobilienscout",
    size="75qm",
    rooms="2",
    address="Berlin Mitte"
)

# Backward compatible with dicts
expose_dict = expose.to_dict()
expose_obj = Expose.from_dict(expose_dict)
```

#### 2. Ports (Interfaces) (`flathunter/ports/`)

Protocol classes define contracts for components:

```python
class CrawlerPort(Protocol):
    URL_PATTERN: re.Pattern
    def crawl(self, url: str, max_pages: Optional[int] = None) -> List[Dict]: ...
    def get_name(self) -> str: ...
```

#### 3. Factory Pattern (`flathunter/config/`)

Centralizes registration and creation of crawlers and notifiers:

```python
from flathunter.config import get_default_crawler_factory

factory = get_default_crawler_factory()
crawler = factory.get_crawler_for_url(url, config)
```

#### 4. Repository Pattern (`flathunter/repositories/`)

Abstracts persistence layer:

```python
from flathunter.repositories import SqliteExposeRepository

repo = SqliteExposeRepository('./data/flathunter.db')
if not repo.is_processed(expose['id']):
    repo.save_expose(expose)
    repo.mark_processed(expose['id'])
```

#### 5. Processing Pipeline (`flathunter/processing/`)

Chain-of-Responsibility pattern for processing exposes:

```python
chain = (ProcessorChain.builder(config)
    .apply_filter(filter_set)
    .crawl_expose_details()
    .resolve_addresses()
    .calculate_durations()
    .save_all_exposes(id_watch)
    .send_messages(receivers)
    .build())

processed = chain.process(raw_exposes)
```

### Data Flow

```
Config File → YamlConfig → CrawlerFactory → Crawler Pool
                  ↓
              Hunter App → ProcessorChain
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
              Repository            Notifiers
              (SQLite)         (Telegram/Slack)
```

---

## Adding New Features

### Adding a New Crawler

1. **Create crawler class** in appropriate directory (`flathunter/crawler/{country}/`):

```python
# flathunter/crawler/uk/newsite.py
import re
from flathunter.core.abstract_crawler import Crawler

class NewSite(Crawler):
    """Crawler for newsite.co.uk"""

    URL_PATTERN = re.compile(r'https://www\.newsite\.co\.uk')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def crawl(self, url, max_pages=None):
        """Crawl newsite listings"""
        soup = self.get_page(url)  # Handles Chrome/Selenium if needed
        return self.extract_data(soup)

    def extract_data(self, soup):
        """Parse HTML and extract expose data"""
        exposes = []
        for listing in soup.select('.property-card'):
            expose = {
                'id': self.extract_id(listing),
                'url': self.extract_url(listing),
                'title': listing.select_one('.title').text.strip(),
                'price': listing.select_one('.price').text.strip(),
                'size': self.extract_size(listing),
                'rooms': self.extract_rooms(listing),
                'address': listing.select_one('.address').text.strip(),
                'crawler': self.get_name()
            }
            exposes.append(expose)
        return exposes

    def get_name(self):
        return 'newsite'
```

2. **Register in factory** (`flathunter/config/crawler_factory.py`):

```python
def get_default_crawler_factory() -> CrawlerFactory:
    # ... existing imports ...
    from flathunter.crawler.uk.newsite import NewSite

    factory = CrawlerFactory()
    # ... existing registrations ...
    factory.register(re.compile(r'https://www\.newsite\.co\.uk'), NewSite)
    return factory
```

3. **Add tests** (`test/test_crawler_newsite.py`):

```python
import unittest
from flathunter.crawler.uk.newsite import NewSite

class NewSiteTest(unittest.TestCase):
    def test_crawler_extracts_data(self):
        config = {'headless_browser': True}
        crawler = NewSite(config)
        results = crawler.crawl('https://www.newsite.co.uk/...')
        self.assertGreater(len(results), 0)
```

### Adding a New Notifier

1. **Create notifier class** (`flathunter/notifiers/mynewnotifier.py`):

```python
from flathunter.core.abstract_notifier import Notifier

class SenderMyNewNotifier(Notifier):
    """Send notifications via MyNewService"""

    def __init__(self, config, receivers=None):
        self.webhook_url = config.mynewnotifier_webhook_url()
        self.enabled = self.webhook_url is not None

    def notify(self, message):
        """Send notification"""
        if not self.enabled:
            return

        import requests
        response = requests.post(
            self.webhook_url,
            json={'text': message}
        )
        response.raise_for_status()
```

2. **Register in factory** (`flathunter/config/notifier_factory.py`):

```python
def get_default_notifier_factory() -> NotifierFactory:
    # ... existing imports ...
    from flathunter.notifiers.mynewnotifier import SenderMyNewNotifier

    factory = NotifierFactory()
    # ... existing registrations ...
    factory.register('mynewnotifier', SenderMyNewNotifier)
    return factory
```

3. **Add config support** (`config.yaml`):

```yaml
notifiers:
  - mynewnotifier

mynewnotifier:
  webhook_url: # loaded from MYNEWNOTIFIER_WEBHOOK_URL env var
```

### Adding a Processor

Create a processor in `flathunter/processing/`:

```python
from flathunter.core.abstract_processor import Processor

class MyCustomProcessor(Processor):
    """Custom processing step"""

    def __init__(self, config):
        self.config = config

    def process_expose(self, expose):
        """Process single expose"""
        # Add custom fields, transform data, etc.
        expose['custom_field'] = self.calculate_something(expose)
        return expose
```

Add to processing chain in `flathunter/processing/processor.py`:

```python
def my_custom_step(self):
    """Add custom processing step"""
    self.processors.append(MyCustomProcessor(self.config))
    return self
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flathunter --cov-report=html

# Run specific test file
pytest test/test_crawler_zoopla.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "telegram"
```

### Test Structure

```
test/
├── test_crawler_*.py      # Crawler tests
├── test_notifier_*.py     # Notifier tests
├── test_processor_*.py    # Processor tests
└── fixtures/              # Test data (HTML responses, etc.)
```

### Writing Tests

```python
import unittest
from unittest.mock import Mock, patch

class MyFeatureTest(unittest.TestCase):

    def setUp(self):
        """Run before each test"""
        self.config = Mock()
        self.config.headless_browser = Mock(return_value=True)

    def test_something(self):
        """Test description"""
        # Arrange
        expected = "value"

        # Act
        result = my_function()

        # Assert
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_with_mocking(self, mock_get):
        """Test with external dependency mocked"""
        mock_get.return_value.text = "<html>...</html>"
        # ... test code ...
```

### Test Coverage Goals

- **Core modules**: 90%+ coverage
- **Crawlers**: 70%+ coverage (hard to test bot-protected sites)
- **Notifiers**: 80%+ coverage
- **Integration tests**: Critical paths covered

---

## Deployment

### Docker Deployment

#### With Docker Compose (Recommended)

```bash
# Build
docker compose -f deployment/docker-compose.yaml build

# Run
docker compose -f deployment/docker-compose.yaml up

# Run in background
docker compose -f deployment/docker-compose.yaml up -d

# View logs
docker compose -f deployment/docker-compose.yaml logs -f
```

#### With Plain Docker

```bash
# Build
docker build -t flathunter -f deployment/Dockerfile .

# Run with mounted config
docker run --mount type=bind,source=$PWD/config.yaml,target=/config.yaml \
  --mount type=bind,source=$PWD/.env,target=/.env \
  flathunter python flathunt.py -c /config.yaml
```

### Google Cloud Deployment

#### Prerequisites

```bash
# Install gcloud CLI
# See: https://cloud.google.com/sdk/docs

# Initialize
gcloud init
gcloud config set project YOUR_PROJECT_ID
```

#### Google App Engine

For simple deployments without captcha solving:

```bash
# Deploy app
gcloud app deploy deployment/app.yaml

# Deploy cron job (periodic crawling)
gcloud app deploy deployment/cron.yaml

# View logs
gcloud app logs tail -s default
```

**Requirements:**
- Cloud Build API enabled
- Cloud Firestore API enabled (Native mode)
- Firestore configured in project

#### Google Cloud Run

For deployments needing Chrome/captcha support:

```bash
# Build image with Cloud Build
gcloud builds submit --region=europe-west1

# Or build locally
docker build -t flathunter-job -f deployment/Dockerfile.gcloud.job .

# Create Cloud Run Job via console
# - Memory: 1GB
# - CPU: 1
# - Set environment variables from .env

# Trigger via Cloud Scheduler (HTTP POST to):
# https://[REGION]-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/[PROJECT_ID]/jobs/[JOB_NAME]:run
```

### Systemd Service (Linux)

For running on a dedicated server:

```bash
# Copy service file
sudo cp deployment/sample-flathunter.service /lib/systemd/system/flathunter.service

# Edit service file with your paths
sudo nano /lib/systemd/system/flathunter.service

# Enable and start
sudo systemctl enable flathunter --now

# View status
sudo systemctl status flathunter

# View logs
sudo journalctl -u flathunter -f
```

---

## Code Style

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use docstrings for classes and public methods

### Linting

```bash
# Run pylint
pylint flathunter/

# Run type checker
pyright flathunter/
# or
mypy flathunter/

# Auto-format with black (if configured)
black flathunter/
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ImmoScout`, `SenderTelegram`)
- **Functions/Methods**: `snake_case` (e.g., `extract_data`, `get_name`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `URL_PATTERN`, `DEFAULT_TIMEOUT`)
- **Private methods**: `_leading_underscore` (e.g., `_parse_price`)

### Commit Messages

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(crawler): add support for NewSite.com

Implements crawler for NewSite.com rental listings.
Includes bot detection bypass and pagination support.

Closes #123

---

fix(telegram): handle connection timeout gracefully

Previously crashed on network errors. Now retries 3 times
with exponential backoff before logging error.

Fixes #456
```

### Pull Request Process

1. **Fork and create branch** from `main`
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. **Make changes** with tests
   - Add tests for new functionality
   - Ensure existing tests pass
   - Update documentation

3. **Commit changes** with conventional commits

4. **Push and create PR**
   ```bash
   git push origin feat/my-new-feature
   ```

5. **PR Requirements:**
   - Description of changes
   - Tests passing
   - Code coverage maintained/improved
   - Documentation updated
   - No merge conflicts

6. **Code Review:**
   - Address reviewer feedback
   - Keep commits clean (squash if needed)

7. **Merge:**
   - Maintainer will merge after approval

---

## Bot Detection & Captchas

### Chrome WebDriver

Some sites require browser automation:

```python
from flathunter.crawling.chrome_wrapper import get_chrome_driver

# In your crawler
driver = get_chrome_driver(self.config)
driver.get(url)
html = driver.page_source
# ... parse html ...
driver.quit()
```

### Captcha Solving

For ImmoScout24 and similar sites:

1. **Configure captcha service** in `.env`:
   ```bash
   CAPMONSTER_KEY=your_api_key
   ```

2. **Enable in config.yaml**:
   ```yaml
   captcha:
     capmonster:
       api_key:  # loaded from CAPMONSTER_KEY
   ```

3. **Crawler uses automatically** if configured

### Proxy Support

Enable rotating proxies:

```yaml
use_proxy_list: true
```

Flathunter will fetch free proxies and rotate through them.

---

## LLM Integration

### Setup

See `docs/LLM_INTEGRATION_GUIDE.md` for detailed documentation.

**Quick start:**

```bash
# Install anthropic SDK
pip install anthropic

# Add API key to .env
LLM_API_KEY=sk-ant-api03-...
LLM_ENABLED=true
```

### Usage in Code

```python
from flathunter.llm.property_scorer import PropertyScorerProcessor

# Add to processing chain
chain = (ProcessorChain.builder(config)
    .apply_filter(filter_set)
    .crawl_expose_details()
    # Add LLM scoring
    .add_processor(PropertyScorerProcessor(config))
    .send_messages()
    .build())
```

### Cost Optimization

- Use `claude-haiku-4.5` for development (~$0.001/property)
- Use `claude-sonnet-4.5` for production if higher quality needed
- Batch processing reduces API overhead
- Async processing improves throughput

---

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'flathunter'**
```bash
pip install -e .
```

**SSL Certificate Errors (macOS)**
```bash
/Applications/Python*/Install\ Certificates.command
```

**Chrome driver errors**
```bash
# Ensure Chrome is installed
# Set headless mode in config
headless_browser: true
```

**Captcha not solving**
- Verify API key is correct
- Check account balance
- Enable verbose logging to see errors

**Bot detection blocking**
- Try ImmoScout24 cookie override
- Enable proxy support
- Reduce crawl frequency

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/flathunters/flathunter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flathunters/flathunter/discussions)
- **Email**: maintainers@flathunters.org (for security issues)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original flathunters team
- Contributors (see [CONTRIBUTORS.md](CONTRIBUTORS.md))
- Open source libraries used in this project
