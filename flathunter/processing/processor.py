"""Utility classes for building chains for processors"""
from functools import reduce
from typing import List

from flathunter.processing.default_processors import AddressResolver
from flathunter.processing.default_processors import Filter
from flathunter.processing.default_processors import LambdaProcessor
from flathunter.processing.default_processors import CrawlExposeDetails
from flathunter.notifiers import SenderMattermost, SenderTelegram, SenderApprise, SenderSlack, SenderFile
from flathunter.processing.gmaps_duration_processor import GMapsDurationProcessor
from flathunter.persistence.idmaintainer import SaveAllExposesProcessor
from flathunter.core.abstract_processor import Processor
from flathunter.llm.property_scorer import PropertyScorerProcessor

class ProcessorChainBuilder:
    """Builder pattern for building chains of processors"""
    processors: List[Processor]

    def __init__(self, config):
        self.processors = []
        self.config = config

    def send_messages(self, receivers=None):
        """Add processor that sends messages for exposes using factory pattern"""
        try:
            from flathunter.config import get_default_notifier_factory
            notifier_factory = get_default_notifier_factory()
            enabled_names = self.config.notifiers()

            # Create notifiers using factory
            for notifier in notifier_factory.create_enabled(enabled_names, self.config):
                # Special handling for Telegram receiver override
                if isinstance(notifier, SenderTelegram) and receivers is not None:
                    notifier = SenderTelegram(self.config, receivers=receivers)
                self.processors.append(notifier)
        except ImportError:
            # Fallback to old hard-coded approach if factory not available
            notifiers = self.config.notifiers()
            if 'telegram' in notifiers:
                self.processors.append(SenderTelegram(self.config, receivers=receivers))
            if 'mattermost' in notifiers:
                self.processors.append(SenderMattermost(self.config))
            if 'apprise' in notifiers:
                self.processors.append(SenderApprise(self.config))
            if 'slack' in notifiers:
                self.processors.append(SenderSlack(self.config))
            if 'file' in notifiers:
                self.processors.append(SenderFile(self.config))
        return self

    def resolve_addresses(self):
        """Add processor that resolves addresses from expose pages"""
        self.processors.append(AddressResolver(self.config))
        return self

    def calculate_durations(self):
        """Add processor to calculate durations, if enabled"""
        durations_enabled = "google_maps_api" in self.config \
                            and self.config["google_maps_api"]["enable"]
        if durations_enabled:
            self.processors.append(GMapsDurationProcessor(self.config))
        return self

    def crawl_expose_details(self):
        """Add processor to crawl expose details"""
        self.processors.append(CrawlExposeDetails(self.config))
        return self

    def map(self, func):
        """Add processor that applies a lambda to exposes"""
        self.processors.append(LambdaProcessor(self.config, func))
        return self

    def apply_filter(self, filter_set):
        """Add processor that applies a filter to expose sequence"""
        self.processors.append(Filter(self.config, filter_set))
        return self

    def save_all_exposes(self, id_watch):
        """Add processor that saves all exposes to disk"""
        self.processors.append(SaveAllExposesProcessor(self.config, id_watch))
        return self

    def score_properties(self):
        """Add LLM-based property scoring processor, if enabled"""
        llm_enabled = "llm" in self.config and self.config["llm"].get("enabled", False)
        if llm_enabled:
            self.processors.append(PropertyScorerProcessor(self.config))
        return self

    def build(self):
        """Build the processor chain"""
        return ProcessorChain(self.processors)

class ProcessorChain:
    """Class to hold a chain of processors"""
    processors: List[Processor]

    def __init__(self, processors):
        self.processors = processors

    def process(self, exposes):
        """Process the sequences of exposes with the processor chain"""
        return reduce((lambda exposes, processor: processor.process_exposes(exposes)),
                      self.processors, exposes)

    @staticmethod
    def builder(config):
        """Return a new processor chain builder"""
        return ProcessorChainBuilder(config)
