"""File-based notifier for local testing"""
import json
from datetime import datetime
from pathlib import Path

from flathunter.core.abstract_notifier import Notifier
from flathunter.core.abstract_processor import Processor
from flathunter.core.config import YamlConfig


class SenderFile(Processor, Notifier):
    """Expose processor that saves notifications to a local file"""

    def __init__(self, config: YamlConfig):
        self.config = config
        file_config = self.config.get('file', {})
        self.output_file = file_config.get('output_file', 'flathunter_results.json')
        self.output_path = Path(self.output_file)

        # Create file if it doesn't exist
        if not self.output_path.exists():
            self.output_path.write_text('[]', encoding='utf-8')

    def process_expose(self, expose):
        """Save expose details to file"""
        # Load existing data
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

        # Add timestamp
        expose_with_timestamp = {
            'timestamp': datetime.now().isoformat(),
            **expose
        }

        # Append new expose
        data.append(expose_with_timestamp)

        # Save back to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print("NEW LISTING FOUND AND SAVED!")
        print("="*60)
        print(f"Title: {expose.get('title', 'N/A')}")
        print(f"Price: {expose.get('price', 'N/A')}")
        print(f"Rooms: {expose.get('rooms', 'N/A')}")
        print(f"Size: {expose.get('size', 'N/A')}")
        print(f"Address: {expose.get('address', 'N/A')}")

        # Display AI analysis if available
        if expose.get('ai_score') is not None:
            score = expose.get('ai_score')
            stars = '⭐' * int(round(score))
            print(f"\n🤖 AI SCORE: {score}/10 {stars}")

            if expose.get('ai_reasoning'):
                print(f"   Reasoning: {expose.get('ai_reasoning')}")

            if expose.get('ai_highlights'):
                print("   ✅ Highlights:")
                for highlight in expose.get('ai_highlights', []):
                    print(f"      • {highlight}")

            if expose.get('ai_warnings'):
                print("   ⚠️  Warnings:")
                for warning in expose.get('ai_warnings', []):
                    print(f"      • {warning}")

            if expose.get('ai_red_flags'):
                print("   🚩 Red Flags:")
                for flag in expose.get('ai_red_flags', []):
                    print(f"      • {flag}")

        print(f"\nURL: {expose.get('url', 'N/A')}")
        print(f"Saved to: {self.output_path.absolute()}")
        print(f"{'='*60}\n")

        return expose

    def notify(self, message: str):
        """Save a notification message to file"""
        try:
            with open(self.output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []

        data.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'notification',
            'message': message
        })

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nNotification: {message}")
        print(f"Saved to: {self.output_path.absolute()}\n")
