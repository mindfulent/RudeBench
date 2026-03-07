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

Assumptions: 2,000 calls/model, ~200 input tokens, ~1,000 output tokens average.

### Standard API
| Model | Total |
|-------|-------|
| Claude 4.6 Sonnet | $31.20 |
| GPT-5.2 | $28.70 |
| Gemini 2.5 Pro | $20.50 |
| Llama 4 Scout (Groq) | $0.72 |
| Grok 3 | $31.20 |
| **Subtotal** | **$112.32** |

### Batch API (recommended)
| Model | Total |
|-------|-------|
| Claude 4.6 Sonnet | $15.60 |
| GPT-5.2 | $14.35 |
| Gemini 2.5 Pro | $10.25 |
| Llama 4 Scout (Groq) | $0.72 |
| Grok 3 | $15.60 |
| **Subtotal** | **$56.52** |

### Grand Total (with judge costs)
| Scenario | Completions | Judge | Total |
|----------|-------------|-------|-------|
| Standard API | $112 | ~$25 | ~$137 |
| All Batch API | $57 | ~$18 | ~$75 |
| With 20% retry buffer | — | — | ~$90 (batch) / ~$165 (standard) |

**Budget of $200-500 is very realistic.** Even worst-case (full run twice at standard pricing) is ~$275.

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
