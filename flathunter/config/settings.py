"""Typed configuration settings"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    # python-dotenv not installed, will just use system env vars
    pass

@dataclass
class Settings:
    """Immutable configuration settings"""
    # Required
    target_urls: List[str]

    # Database
    database_location: str = "./data"

    # Loop configuration
    loop_is_active: bool = True
    loop_period_seconds: int = 300
    random_jitter_enabled: bool = False
    loop_pause_from: str = "22:00"
    loop_pause_till: str = "07:00"

    # Notifiers
    notifiers: List[str] = field(default_factory=list)

    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_receiver_ids: List[int] = field(default_factory=list)
    telegram_notify_with_images: bool = True

    # Other notifiers
    slack_webhook_url: Optional[str] = None
    mattermost_webhook_url: Optional[str] = None
    apprise_config: Dict[str, Any] = field(default_factory=dict)
    file_output_path: Optional[str] = None

    # Filters
    filter_excluded_titles: List[str] = field(default_factory=list)
    filter_min_price: Optional[int] = None
    filter_max_price: Optional[int] = None
    filter_min_size: Optional[int] = None
    filter_max_size: Optional[int] = None
    filter_min_rooms: Optional[int] = None
    filter_max_rooms: Optional[int] = None
    filter_max_price_per_square: Optional[int] = None

    # Captcha
    captcha_2captcha_key: Optional[str] = None
    captcha_imagetyperz_token: Optional[str] = None
    captcha_capmonster_key: Optional[str] = None
    headless_browser: bool = False

    # Google Maps
    google_maps_api_enable: bool = False
    google_maps_api_key: Optional[str] = None
    google_maps_api_url: Optional[str] = None

    # Verbose logging
    verbose: bool = False

    # LLM Configuration
    llm_enabled: bool = False
    llm_api_key: Optional[str] = None
    llm_model: str = "claude-haiku-4.5"
    llm_priorities: List[str] = field(default_factory=list)
    llm_dealbreakers: List[str] = field(default_factory=list)

    # ImmoScout24 Cookie
    immoscout_cookie: Optional[str] = None

    # Message format
    message_format: str = """{title}
Zimmer: {rooms}
Größe: {size}
Preis: {price}

{url}"""

    title_format: str = "{crawler}: {title}"

    @classmethod
    def from_yaml(cls, filepath: str) -> 'Settings':
        """Load from YAML file with environment variable overrides"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Extract and flatten nested config
        settings_dict = cls._flatten_config(config_data)

        # Override with environment variables
        settings_dict = cls._apply_env_overrides(settings_dict)

        return cls(**settings_dict)

    @staticmethod
    def _flatten_config(config: Dict) -> Dict:
        """Convert nested YAML to flat settings dict"""
        result = {}

        # Required: URLs
        result['target_urls'] = config.get('urls', [])

        # Database
        result['database_location'] = config.get('database_location', './data')

        # Loop configuration
        loop = config.get('loop', {})
        result['loop_is_active'] = loop.get('active', True)
        result['loop_period_seconds'] = loop.get('sleeping_time', 300)
        result['random_jitter_enabled'] = loop.get('random_jitter', False)
        result['loop_pause_from'] = config.get('loop_pause_from', '22:00')
        result['loop_pause_till'] = config.get('loop_pause_till', '07:00')

        # Notifiers
        result['notifiers'] = config.get('notifiers', [])

        # Telegram
        telegram = config.get('telegram', {})
        result['telegram_bot_token'] = telegram.get('bot_token')
        result['telegram_receiver_ids'] = telegram.get('receiver_ids', [])
        result['telegram_notify_with_images'] = telegram.get('notify_with_images', True)

        # Other notifiers
        slack = config.get('slack', {})
        result['slack_webhook_url'] = slack.get('webhook_url')

        mattermost = config.get('mattermost', {})
        result['mattermost_webhook_url'] = mattermost.get('webhook_url')

        result['apprise_config'] = config.get('apprise', {})

        file_config = config.get('file', {})
        result['file_output_path'] = file_config.get('output_file')

        # Filters
        filters = config.get('filters', {})
        result['filter_excluded_titles'] = filters.get('excluded_titles', [])
        result['filter_min_price'] = filters.get('min_price')
        result['filter_max_price'] = filters.get('max_price')
        result['filter_min_size'] = filters.get('min_size')
        result['filter_max_size'] = filters.get('max_size')
        result['filter_min_rooms'] = filters.get('min_rooms')
        result['filter_max_rooms'] = filters.get('max_rooms')
        result['filter_max_price_per_square'] = filters.get('max_price_per_square')

        # Captcha
        captcha = config.get('captcha', {})
        if '2captcha' in captcha:
            result['captcha_2captcha_key'] = captcha['2captcha'].get('api_key')
        if 'imagetyperz' in captcha:
            result['captcha_imagetyperz_token'] = captcha['imagetyperz'].get('token')
        if 'capmonster' in captcha:
            result['captcha_capmonster_key'] = captcha['capmonster'].get('api_key')
        result['headless_browser'] = config.get('headless_browser', False)

        # Google Maps
        gmaps = config.get('google_maps_api', {})
        result['google_maps_api_enable'] = gmaps.get('enable', False)
        result['google_maps_api_key'] = gmaps.get('key')
        result['google_maps_api_url'] = gmaps.get('url')

        # Verbose logging
        result['verbose'] = config.get('verbose', False)

        # LLM Configuration
        llm = config.get('llm', {})
        result['llm_enabled'] = llm.get('enabled', False)
        result['llm_api_key'] = llm.get('api_key')
        result['llm_model'] = llm.get('model', 'claude-haiku-4.5')
        result['llm_priorities'] = llm.get('priorities', [])
        result['llm_dealbreakers'] = llm.get('dealbreakers', [])

        # ImmoScout24 Cookie
        result['immoscout_cookie'] = config.get('immoscout_cookie')

        # Message format
        result['message_format'] = config.get('message', result['message_format'])
        result['title_format'] = config.get('title', result['title_format'])

        return result

    @staticmethod
    def _apply_env_overrides(settings: Dict) -> Dict:
        """Apply environment variable overrides"""
        # Check for env vars like TARGET_URLS, TELEGRAM_BOT_TOKEN, etc.
        if os.getenv('TARGET_URLS'):
            settings['target_urls'] = os.getenv('TARGET_URLS').split(';')

        if os.getenv('DATABASE_LOCATION'):
            settings['database_location'] = os.getenv('DATABASE_LOCATION')

        if os.getenv('TELEGRAM_BOT_TOKEN'):
            settings['telegram_bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')

        if os.getenv('TELEGRAM_RECEIVER_IDS'):
            settings['telegram_receiver_ids'] = [
                int(x.strip()) for x in os.getenv('TELEGRAM_RECEIVER_IDS').split(',')
            ]

        if os.getenv('SLACK_WEBHOOK_URL'):
            settings['slack_webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')

        if os.getenv('MATTERMOST_WEBHOOK_URL'):
            settings['mattermost_webhook_url'] = os.getenv('MATTERMOST_WEBHOOK_URL')

        if os.getenv('2CAPTCHA_KEY'):
            settings['captcha_2captcha_key'] = os.getenv('2CAPTCHA_KEY')

        if os.getenv('IMAGETYPERZ_TOKEN'):
            settings['captcha_imagetyperz_token'] = os.getenv('IMAGETYPERZ_TOKEN')

        if os.getenv('CAPMONSTER_KEY'):
            settings['captcha_capmonster_key'] = os.getenv('CAPMONSTER_KEY')

        if os.getenv('HEADLESS_BROWSER'):
            settings['headless_browser'] = os.getenv('HEADLESS_BROWSER').lower() in ('true', '1', 'yes')

        if os.getenv('VERBOSE_LOG'):
            settings['verbose'] = os.getenv('VERBOSE_LOG').lower() in ('true', '1', 'yes')

        if os.getenv('LOOP_PERIOD_SECONDS'):
            settings['loop_period_seconds'] = int(os.getenv('LOOP_PERIOD_SECONDS'))

        if os.getenv('RANDOM_JITTER_ENABLED'):
            settings['random_jitter_enabled'] = os.getenv('RANDOM_JITTER_ENABLED').lower() in ('true', '1', 'yes')

        # LLM Configuration
        if os.getenv('LLM_API_KEY'):
            settings['llm_api_key'] = os.getenv('LLM_API_KEY')

        if os.getenv('LLM_MODEL'):
            settings['llm_model'] = os.getenv('LLM_MODEL')

        if os.getenv('LLM_ENABLED'):
            settings['llm_enabled'] = os.getenv('LLM_ENABLED').lower() in ('true', '1', 'yes')

        # ImmoScout24 Cookie
        if os.getenv('IMMOSCOUT_COOKIE'):
            settings['immoscout_cookie'] = os.getenv('IMMOSCOUT_COOKIE')

        # Google Maps API Key
        if os.getenv('GOOGLE_MAPS_API_KEY'):
            settings['google_maps_api_key'] = os.getenv('GOOGLE_MAPS_API_KEY')

        return settings
