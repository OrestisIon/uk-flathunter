# LLM Integration Guide for Flathunter

## Overview

This guide explains how to integrate AI-powered property analysis into Flathunter using Claude AI.

## Features

### 🎯 Intelligent Property Scoring
- **Value-for-Money Analysis**: Score properties 0-10 based on price, location, size, and features
- **Personalized Recommendations**: Takes your preferences and dealbreakers into account
- **Confidence Rating**: Know how reliable the AI assessment is

### 📝 Property Enrichment
- **Feature Extraction**: Automatically extract structured data from unstructured descriptions
- **Red Flag Detection**: Identify potential concerns (poor EPC rating, restrictive requirements, etc.)
- **Smart Filtering**: Go beyond basic filters with AI understanding

### 💰 Cost
- **~$10-15/month** for analyzing 100 properties/day
- Uses Claude Haiku 4.5 by default (fast & cheap)
- Concurrent processing for speed (10 properties in ~5 seconds)

---

## Quick Start

### 1. Get an Anthropic API Key

1. Visit https://console.anthropic.com/
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### 2. Update Configuration

Copy the example config:
```bash
cp docs/examples/config_with_llm.yaml config.yaml
```

Edit `config.yaml` and add your API key:
```yaml
llm:
  enabled: true
  api_key: sk-ant-api03-YOUR-KEY-HERE  # Replace with your key
  model: claude-haiku-4.5

  priorities:
    - "quiet neighborhood"
    - "good natural light"
    - "near parks"

  dealbreakers:
    - "ground floor without garden"
    - "basement flat"
```

### 3. Install Anthropic SDK

```bash
pipenv install anthropic
# or
pip install anthropic
```

### 4. Test with File Notifier

Start with file output to test AI analysis:
```yaml
notifiers:
  - file

file:
  output_file: flathunter_results_with_ai.json
```

### 5. Run Flathunter

```bash
python flathunt.py --config config.yaml
```

You'll see AI-analyzed properties in your terminal and saved to the JSON file:

```
============================================================
NEW LISTING FOUND AND SAVED!
============================================================
Title: Beautiful 2-bed flat in WC1X
Price: £1,800 pcm
Rooms: 2
Size: 75 sqm
Address: WC1X 0AA, London

🤖 AI SCORE: 8.5/10 ⭐⭐⭐⭐⭐⭐⭐⭐
   Reasoning: Excellent value - price is 12% below market average
              for the area. Good size and well-located near transport.
   ✅ Highlights:
      • 5 minute walk to King's Cross station
      • Recently renovated based on listing photos
      • Price per sqm is competitive for central London
   ⚠️  Warnings:
      • Short lease (only 3 years remaining)

URL: https://www.zoopla.co.uk/...
Saved to: /path/to/flathunter_results_with_ai.json
============================================================
```

---

## Integration into Processing Pipeline

### Method 1: Simple Integration (Recommended for MVP)

Add to your processing pipeline in `flathunt.py` or custom script:

```python
from flathunter.processing.processor import ProcessorChain
from flathunter.llm import PropertyScorerProcessor, PropertyEnrichmentProcessor

# Build pipeline with LLM processors
processor_chain = (
    ProcessorChain.builder(config)
    .apply_filter(filter_set)
    .crawl_expose_details()
    .resolve_addresses()
    .calculate_durations()

    # Add LLM processors
    .processors.append(PropertyEnrichmentProcessor(config))  # Extract features
    .processors.append(PropertyScorerProcessor(config))      # Score properties

    .save_all_exposes(id_watch)
    .send_messages()
    .build()
)

# Process properties through pipeline
results = processor_chain.process(exposes)
```

### Method 2: Add to ProcessorChainBuilder

For a cleaner integration, extend `ProcessorChainBuilder`:

```python
# In flathunter/processing/processor.py

from flathunter.llm import PropertyScorerProcessor, PropertyEnrichmentProcessor

class ProcessorChainBuilder:
    # ... existing methods ...

    def enrich_with_llm(self):
        """Add LLM enrichment processor"""
        from flathunter.llm import PropertyEnrichmentProcessor
        self.processors.append(PropertyEnrichmentProcessor(self.config))
        return self

    def score_properties(self):
        """Add LLM scoring processor"""
        from flathunter.llm import PropertyScorerProcessor
        self.processors.append(PropertyScorerProcessor(self.config))
        return self
```

Then use it:
```python
processor_chain = (
    ProcessorChain.builder(config)
    .apply_filter(filter_set)
    .enrich_with_llm()      # NEW
    .score_properties()      # NEW
    .send_messages()
    .build()
)
```

---

## Advanced Configuration

### Model Selection

Choose based on your needs:

```yaml
llm:
  # Fast & cheap - good for most use cases
  model: claude-haiku-4.5
  # Cost: ~$0.10/month for 3,000 properties

  # Balanced - better quality analysis
  # model: claude-sonnet-4.5
  # Cost: ~$12/month for 3,000 properties

  # Most capable - highest quality
  # model: claude-opus-4.6
  # Cost: ~$50/month for 3,000 properties
```

### User Preferences

Personalize AI recommendations:

```yaml
llm:
  priorities:
    - "quiet neighborhood"
    - "good natural light"
    - "near parks or green spaces"
    - "easy cycling distance to work"
    - "family-friendly area"

  dealbreakers:
    - "ground floor without garden"
    - "basement flat"
    - "north-facing only"
    - "no natural light"
    - "busy main road"
```

### Feature Toggles

Enable/disable specific features:

```yaml
llm:
  features:
    - scoring              # Score properties 0-10
    - enrichment           # Extract features
    - red_flag_detection   # Detect warnings
    # - negotiation_assistance  # Future feature
```

### Confidence Thresholds

Only show high-confidence AI analysis:

```yaml
llm:
  min_confidence: 0.7  # Only show if confidence >= 70%

  # Possible values: high, medium, low
  # Confidence levels are automatically calculated by AI
```

---

## Cost Optimization

### 1. Use Batch API (50% Discount)

For non-urgent analysis, use Anthropic's batch API:

```python
# In property_scorer.py
# Set batch_mode: true in config

llm:
  batch_mode: true  # 50% discount, but 5-60 min latency
```

### 2. Tier Your Analysis

Process cheap analysis first, deep analysis for top properties:

```python
# config.yaml
llm:
  tiered_analysis:
    level_1:  # All properties
      model: claude-haiku-4.5
      features: [enrichment, red_flag_detection]

    level_2:  # Top 20% by basic filters
      model: claude-sonnet-4.5
      features: [scoring, detailed_analysis]
```

### 3. Caching (30-90% Savings)

Enable prompt caching for repeated context:

```python
# Automatically enabled for market data and instructions
# No configuration needed - handled by PropertyScorerProcessor
```

### 4. Set Token Limits

Prevent runaway costs:

```yaml
llm:
  max_tokens_per_request: 500  # Limit response length
  max_properties_per_day: 100  # Safety limit
```

---

## Monitoring & Debugging

### Check AI Usage

```python
# In your script
from flathunter.llm import PropertyScorerProcessor

scorer = PropertyScorerProcessor(config)
print(f"LLM enabled: {scorer.enabled}")
print(f"Model: {scorer.model}")
```

### View Detailed Logs

```yaml
verbose: true  # Enable in config.yaml
```

Then check logs:
```bash
python flathunt.py --config config.yaml

# You'll see:
# [INFO] Scored property 12345: 8.5/10
# [DEBUG] Enriched property 12345 with 7 features
# [WARNING] Low confidence (0.5) for property 67890
```

### Validate AI Scores

Add validation to check AI isn't hallucinating:

```python
def validate_score(expose):
    score = expose.get('ai_score')

    # Sanity checks
    if score and (score < 0 or score > 10):
        logger.warning(f"Invalid score: {score}")
        return False

    # Cross-reference with price per sqm
    pps = calculate_price_per_sqm(expose)
    if pps > 60 and score > 8:
        logger.warning(f"High score despite expensive PPS")

    return True
```

---

## Example Output

### JSON File Output

```json
{
  "timestamp": "2026-02-14T21:30:00",
  "id": "12345",
  "title": "Beautiful 2-bed flat in WC1X",
  "price": "£1,800 pcm",
  "rooms": "2",
  "size": "75 sqm",
  "address": "WC1X 0AA, London",
  "url": "https://www.zoopla.co.uk/...",

  "ai_score": 8.5,
  "ai_reasoning": "Excellent value - price is 12% below market average...",
  "ai_highlights": [
    "5 minute walk to King's Cross station",
    "Recently renovated based on listing photos",
    "Price per sqm is competitive for central London"
  ],
  "ai_warnings": [
    "Short lease (only 3 years remaining)"
  ],
  "ai_confidence": "high",
  "ai_red_flags": [],

  "extracted_features": {
    "furnished": "unfurnished",
    "parking": "no",
    "garden": "no",
    "floor_level": "2nd",
    "epc_rating": "C"
  }
}
```

### Telegram Output (with LLM)

```
🏠 Beautiful 2-bed flat in WC1X
AI Score: ⭐⭐⭐⭐⭐⭐⭐⭐ 8.5/10

💰 £1,800 pcm | 🛏️ 2 beds | 📏 75 sqm
📍 WC1X 0AA, London

✅ Why this is a good deal:
• 5 minute walk to King's Cross station
• Recently renovated
• Price 12% below market average

⚠️ Things to check:
• Short lease (3 years)

🔗 View listing
🤖 AI analysis | 🎯 High confidence
```

---

## Troubleshooting

### "LLM features disabled"

**Cause:** Missing or invalid API key

**Solution:**
1. Check `config.yaml` has valid `llm.api_key`
2. Verify key starts with `sk-ant-`
3. Test key at https://console.anthropic.com/

### "Rate limit exceeded"

**Cause:** Too many API requests too quickly

**Solution:**
1. Reduce concurrent requests (default: 10)
2. Add delay between batches
3. Use batch API mode

```yaml
llm:
  concurrent_requests: 5  # Reduce from 10
  batch_delay_seconds: 2  # Add delay
```

### "Scores seem inconsistent"

**Cause:** High temperature or lack of context

**Solution:**
1. Use temperature=0.0 for deterministic scoring (already default)
2. Ensure properties have sufficient data (address, size, etc.)
3. Add more context to user preferences

### High costs

**Cause:** Using expensive model or too many tokens

**Solution:**
1. Switch to Haiku: `model: claude-haiku-4.5`
2. Enable batch mode for 50% discount
3. Set `max_tokens_per_request: 300`
4. Use tiered analysis (Haiku for all, Sonnet for top 20%)

---

## Future Enhancements

### Phase 2: RAG Integration (Coming Soon)

Build knowledge base of historical properties:

```yaml
llm:
  rag:
    enabled: true
    vector_db: chromadb  # or pinecone, qdrant
    index_historical_data: true
```

### Phase 3: Image Analysis

Analyze property photos:

```yaml
llm:
  features:
    - image_analysis  # Detect renovations, quality, etc.
```

### Phase 4: Conversational Interface

Chat with your property assistant:

```bash
> "Show me properties near parks"
> "What's the best value property this week?"
> "Why did you score property #12345 so high?"
```

---

## Support

- **API Issues:** https://console.anthropic.com/
- **Flathunter Issues:** https://github.com/OrestisIon/uk-flathunter/issues
- **Cost Calculator:** https://llmpricingcalculator.com/

---

## Summary

✅ **Easy Integration** - Drop into existing pipeline
✅ **Low Cost** - ~$10-15/month for 100 properties/day
✅ **Fast** - Concurrent processing, ~5 seconds for 10 properties
✅ **Customizable** - Configure model, preferences, features
✅ **Production Ready** - Error handling, validation, logging

**Start testing with file notifier, then enable Telegram once you're happy with results!**
