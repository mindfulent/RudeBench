# API Pricing & Unified Client Research

## Model Pricing (March 2026)

| Model | Input/MTok | Output/MTok | Batch Input | Batch Output | Batch Discount |
|-------|-----------|-------------|-------------|--------------|----------------|
| Claude 4.6 Sonnet | $3.00 | $15.00 | $1.50 | $7.50 | 50% |
| GPT-5.2 | $1.75 | $14.00 | $0.88 | $7.00 | 50% |
| Gemini 2.5 Pro | $1.25 | $10.00 | $0.625 | $5.00 | 50% |
| Llama 4 Scout (Groq) | $0.11 | $0.34 | N/A | N/A | Already cheap |
| Grok 3 | $3.00 | $15.00 | $1.50 | $7.50 | 50% |

## Provider Notes

- **Llama 4 Scout:** Use **Groq** (cheapest: $0.11/$0.34, fastest: 460+ tok/s). Fireworks as fallback.
- **Grok 3:** xAI API is OpenAI-compatible — use `openai` SDK with `base_url="https://api.x.ai/v1"`.
- **All 4 proprietary providers** offer batch APIs with 50% discount and 24-hour processing.
- **Gemini 2.5 Pro** is cheapest frontier model for both standard and batch.

## Total Cost Estimate

Assumptions: 3,000 calls/model (50 tasks × 6 tones × 10 runs), ~200 input tokens, ~1,000 output tokens average.

### Standard API
| Model | Total |
|-------|-------|
| Claude 4.6 Sonnet | $46.80 |
| GPT-5.2 | $43.05 |
| Gemini 2.5 Pro | $30.75 |
| Llama 4 Scout (Groq) | $1.08 |
| Grok 3 | $46.80 |
| **Subtotal** | **$168.48** |

### Batch API (recommended)
| Model | Total |
|-------|-------|
| Claude 4.6 Sonnet | $23.40 |
| GPT-5.2 | $21.53 |
| Gemini 2.5 Pro | $15.38 |
| Llama 4 Scout (Groq) | $1.08 |
| Grok 3 | $23.40 |
| **Subtotal** | **$84.79** |

### Grand Total (with judge costs)
| Scenario | Completions | Judge | Total |
|----------|-------------|-------|-------|
| Standard API | $168 | ~$38 | ~$206 |
| All Batch API | $85 | ~$27 | ~$112 |
| With 20% retry buffer | — | — | ~$135 (batch) / ~$247 (standard) |

**Budget of $200-500 is very realistic.** Even worst-case (full run twice at standard pricing) is ~$415.

## Unified API Client: LiteLLM (Library Mode)

**Recommendation:** Use LiteLLM in library mode for standard API calls. Call batch APIs directly for 50% savings.

| Feature | LiteLLM (Library) | OpenRouter |
|---------|-------------------|------------|
| All 5 models | Yes | Yes |
| Rate limiting/retries | Yes (configurable) | Yes (managed) |
| Cost tracking | Yes (per-request USD) | Yes (dashboard) |
| Batch API support | Call providers directly | No batch passthrough |
| Pricing | Direct (no markup) | Small markup |
| Complexity | Low (`pip install litellm`) | Lowest (just API calls) |

OpenRouter loses on batch API support (no passthrough = no 50% discount) and adds pricing markup.

## Batch API Strategy

Since benchmark doesn't need real-time responses, use batch APIs for all proprietary models:
- Anthropic, OpenAI, Google, xAI all offer 50% batch discount
- 24-hour processing windows
- Submit JSONL of requests, poll/webhook for completion
- Groq doesn't need batch (already $0.72 total)

## Sources
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Groq Pricing](https://groq.com/pricing)
- [xAI Models and Pricing](https://docs.x.ai/developers/models)
- [LiteLLM Docs](https://docs.litellm.ai/docs/)
