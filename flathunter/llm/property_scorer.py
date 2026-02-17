"""LLM-based property scoring and analysis"""
import asyncio
import os
from typing import List, Dict, Any, TYPE_CHECKING
from flathunter.core.abstract_processor import Processor
from flathunter.core.logging import logger

if TYPE_CHECKING:
    from anthropic import Anthropic, AsyncAnthropic
else:
    try:
        from anthropic import Anthropic, AsyncAnthropic
    except ImportError:
        Anthropic = None  # type: ignore
        AsyncAnthropic = None  # type: ignore


class PropertyScorerProcessor(Processor):
    """Score and analyze properties using Claude AI"""

    def __init__(self, config):
        """
        Initialize with Anthropic API key from config

        Config should have:
        - llm_api_key: Your Anthropic API key
        - llm_model: Model to use (default: claude-haiku-4.5)
        - llm_enabled: Enable/disable LLM scoring (default: true)
        """
        self.config = config
        self.enabled = config.get('llm', {}).get('enabled', True)

        if not self.enabled:
            logger.info("LLM scoring is disabled in config")
            return

        # Try to get API key from config, fallback to environment variable
        api_key = config.get('llm', {}).get('api_key') or os.getenv('LLM_API_KEY')
        if not api_key:
            logger.warning("No LLM API key found in config or LLM_API_KEY env var. LLM features disabled.")
            self.enabled = False
            return

        if Anthropic is None:
            logger.error("Anthropic SDK not installed. Run: pip install anthropic")
            self.enabled = False
            return

        self.client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)
        self.model = config.get('llm', {}).get('model', 'claude-haiku-4.5')

        # User preferences for personalized scoring
        self.user_priorities = config.get('llm', {}).get('priorities', [])
        self.user_dealbreakers = config.get('llm', {}).get('dealbreakers', [])

    def process_expose(self, expose: Dict) -> Dict:
        """Analyze a single property"""
        if not self.enabled:
            return expose

        try:
            analysis = self._analyze_property(expose)

            # Add LLM fields to expose
            expose['ai_score'] = analysis.get('score')
            expose['ai_reasoning'] = analysis.get('reasoning')
            expose['ai_highlights'] = analysis.get('highlights', [])
            expose['ai_warnings'] = analysis.get('warnings', [])
            expose['ai_confidence'] = analysis.get('confidence', 'medium')

            logger.info("Scored property %s: %s/10",
                        expose.get('id'), analysis.get('score'))

        except Exception as e:
            logger.error("Error scoring property %s: %s", expose.get('id'), e)
            expose['ai_score'] = None
            expose['ai_error'] = str(e)

        return expose

    def process_exposes(self, exposes):
        """Process multiple exposes concurrently for speed"""
        if not self.enabled:
            # Return map for compatibility with base class
            return map(lambda x: x, exposes)

        expose_list = list(exposes)

        # Process in parallel for better performance
        try:
            results = asyncio.run(self._process_batch_async(expose_list))
            # Return as iterator but wrapped in map for type compatibility
            return map(lambda x: x, results)
        except Exception as e:
            logger.error("Error in batch processing: %s", e)
            # Fall back to sequential processing
            return map(self.process_expose, expose_list)

    async def _process_batch_async(self, exposes: List[Dict]) -> List[Dict]:
        """Process multiple properties concurrently"""

        async def analyze_one(expose):
            try:
                analysis = await self._analyze_property_async(expose)
                expose['ai_score'] = analysis.get('score')
                expose['ai_reasoning'] = analysis.get('reasoning')
                expose['ai_highlights'] = analysis.get('highlights', [])
                expose['ai_warnings'] = analysis.get('warnings', [])
                expose['ai_confidence'] = analysis.get('confidence', 'medium')
            except Exception as e:
                logger.error("Error scoring %s: %s", expose.get('id'), e)
                expose['ai_score'] = None
            return expose

        # Process 10 at a time to avoid rate limits
        results = []
        for i in range(0, len(exposes), 10):
            batch = exposes[i:i+10]
            batch_results = await asyncio.gather(*[analyze_one(e) for e in batch])
            results.extend(batch_results)

        return results

    def _analyze_property(self, expose: Dict) -> Dict[str, Any]:
        """Synchronous property analysis"""
        prompt = self._build_analysis_prompt(expose)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,  # Balanced between creativity and consistency
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return self._parse_analysis_response(response.content[0].text)

    async def _analyze_property_async(self, expose: Dict) -> Dict[str, Any]:
        """Asynchronous property analysis"""
        prompt = self._build_analysis_prompt(expose)

        response = await self.async_client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return self._parse_analysis_response(response.content[0].text)

    def _build_analysis_prompt(self, expose: Dict) -> str:
        """Build prompt for property analysis"""

        user_context = ""
        if self.user_priorities:
            user_context += f"\nUser priorities: {', '.join(self.user_priorities)}"
        if self.user_dealbreakers:
            user_context += f"\nUser dealbreakers: {', '.join(self.user_dealbreakers)}"

        prompt = f"""Analyze this UK rental property and provide a value assessment.

Property Details:
- Title: {expose.get('title', 'N/A')}
- Price: {expose.get('price', 'N/A')}
- Size: {expose.get('size', 'N/A')}
- Rooms: {expose.get('rooms', 'N/A')}
- Location: {expose.get('address', 'N/A')}
- URL: {expose.get('url', 'N/A')}
{user_context}

Please provide:
1. **Score** (0-10): Overall value for money rating
2. **Reasoning** (2-3 sentences): Why this score?
3. **Highlights** (3 bullet points): Key positive aspects
4. **Warnings** (if any): Potential concerns or red flags
5. **Confidence** (high/medium/low): How confident are you in this assessment?

Format your response as:
SCORE: [number]
REASONING: [your reasoning]
HIGHLIGHTS:
- [highlight 1]
- [highlight 2]
- [highlight 3]
WARNINGS:
- [warning 1 or "None"]
CONFIDENCE: [high/medium/low]
"""
        return prompt

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        result = {
            'score': None,
            'reasoning': '',
            'highlights': [],
            'warnings': [],
            'confidence': 'medium'
        }

        try:
            lines = response_text.strip().split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('SCORE:'):
                    try:
                        score_text = line.replace('SCORE:', '').strip()
                        # Extract just the number (handle "8/10" or "8.5" format)
                        import re
                        match = re.search(r'(\d+\.?\d*)', score_text)
                        if match:
                            result['score'] = float(match.group(1))
                    except:
                        pass

                elif line.startswith('REASONING:'):
                    result['reasoning'] = line.replace('REASONING:', '').strip()
                    current_section = 'reasoning'

                elif line.startswith('HIGHLIGHTS:'):
                    current_section = 'highlights'

                elif line.startswith('WARNINGS:'):
                    current_section = 'warnings'

                elif line.startswith('CONFIDENCE:'):
                    confidence = line.replace('CONFIDENCE:', '').strip().lower()
                    result['confidence'] = confidence
                    current_section = None

                elif line.startswith('-') or line.startswith('•'):
                    item = line.lstrip('-•').strip()
                    if current_section == 'highlights' and item.lower() != 'none':
                        result['highlights'].append(item)
                    elif current_section == 'warnings' and item.lower() != 'none':
                        result['warnings'].append(item)

                elif current_section == 'reasoning':
                    result['reasoning'] += ' ' + line

        except Exception as e:
            logger.error("Error parsing LLM response: %s", e)

        # Validation
        if result['score'] is not None:
            result['score'] = max(0.0, min(10.0, result['score']))

        return result
