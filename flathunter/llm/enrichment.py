"""Property enrichment using LLM for feature extraction"""
from typing import Dict, Any
from anthropic import Anthropic
from flathunter.core.abstract_processor import Processor
from flathunter.core.logging import logger


class PropertyEnrichmentProcessor(Processor):
    """Extract structured features from unstructured property descriptions"""

    def __init__(self, config):
        """Initialize with Anthropic API key"""
        self.config = config
        self.enabled = config.get('llm', {}).get('enabled', True)

        if not self.enabled:
            return

        api_key = config.get('llm', {}).get('api_key')
        if not api_key:
            self.enabled = False
            return

        self.client = Anthropic(api_key=api_key)
        self.model = config.get('llm', {}).get('model', 'claude-haiku-4.5')

    def process_expose(self, expose: Dict) -> Dict:
        """Enrich property with extracted features"""
        if not self.enabled:
            return expose

        try:
            # Extract key features from title/description
            features = self._extract_features(expose)
            expose['extracted_features'] = features

            # Detect red flags
            red_flags = self._detect_red_flags(expose, features)
            if red_flags:
                expose['ai_red_flags'] = red_flags

            logger.debug(f"Enriched property {expose.get('id')} with {len(features)} features")

        except Exception as e:
            logger.error(f"Error enriching property {expose.get('id')}: {e}")

        return expose

    def _extract_features(self, expose: Dict) -> Dict[str, Any]:
        """Extract structured features from description"""

        prompt = f"""Extract key features from this property listing:

Title: {expose.get('title', '')}

Extract the following if mentioned:
- Furnished status (furnished/unfurnished/part-furnished)
- Parking (yes/no/type)
- Garden/outdoor space (yes/no/type)
- Pet friendly (yes/no)
- Floor level (ground/1st/2nd/etc)
- Available from (date)
- Lease term (months)
- Bills included (yes/no)
- EPC rating (A-G)

Return ONLY a simple list of features found, one per line.
If information not mentioned, don't include it.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.0,  # Deterministic
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response into features dict
            features = {}
            for line in response.content[0].text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    features[key.strip().lower().replace(' ', '_')] = value.strip()

            return features

        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}

    def _detect_red_flags(self, expose: Dict, features: Dict) -> list:
        """Detect potential warning signs"""

        red_flags = []

        # Price-based red flags
        try:
            price_str = expose.get('price', '')
            if 'week' in price_str.lower():
                red_flags.append("Price listed per week (unusual for UK long-term rentals)")
        except:
            pass

        # Feature-based red flags
        if features.get('floor_level') == 'ground' and \
           features.get('garden') == 'no':
            red_flags.append("Ground floor without garden access")

        if features.get('epc_rating', '').upper() in ['F', 'G']:
            red_flags.append("Poor energy efficiency rating (high bills likely)")

        # Title-based red flags
        title_lower = expose.get('title', '').lower()
        warning_words = ['no dss', 'no benefits', 'professionals only', 'short term']
        for word in warning_words:
            if word in title_lower:
                red_flags.append(f"Restrictive requirement: {word}")

        return red_flags
