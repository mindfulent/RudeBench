# API Pricing & Unified Client Research

## Model Pricing (March 2026)

### Current Lineup (Mid-Range Non-Reasoning)

| Model | Input/MTok | Output/MTok | Batch Input | Batch Output | Batch Discount |
|-------|-----------|-------------|-------------|--------------|----------------|
| Claude 4.6 Sonnet | $3.00 | $15.00 | $1.50 | $7.50 | 50% |
| GPT-5 mini | $0.40 | $1.60 | $0.20 | $0.80 | 50% |
| Gemini 2.5 Flash | $0.15 | $3.50 | $0.075 | $1.75 | 50% |
| Llama 4 Scout (Groq) | $0.11 | $0.34 | N/A | N/A | Already cheap |
| Grok 3 mini | $0.30 | $0.50 | $0.15 | $0.25 | 50% |

### Previous Lineup (Retired — Reasoning Models Caused Truncation)

| Model | Input/MTok | Output/MTok | Issue |
|-------|-----------|-------------|-------|
| GPT-5.2 | $1.75 | $14.00 | Thinking tokens consumed max_tokens budget |
| Gemini 2.5 Pro | $1.25 | $10.00 | 92% completions truncated by thinking tokens |
| Grok 3 | $3.00 | $15.00 | Expensive, no reasoning_effort control |

## Provider Notes

- **GPT-5 mini / Gemini 2.5 Flash:** Support `reasoning_effort="none"` to fully disable thinking tokens. No output budget consumed by reasoning.
- **Grok 3 mini:** Supports `reasoning_effort="low"` (minimum) — `"none"` is not available. May still use some thinking tokens, but 16384 max_tokens absorbs this.
- **Llama 4 Scout:** Use **Groq** (cheapest: $0.11/$0.34, fastest: 460+ tok/s). No reasoning tokens.
- **Claude 4.6 Sonnet:** Non-reasoning model, no thinking tokens.
- **All 4 proprietary providers** offer batch APIs with 50% discount and 24-hour processing.

## Total Cost Estimate

Assumptions: 3,000 calls/model (50 tasks × 6 tones × 10 runs), ~200 input tokens, ~1,000 output tokens average.

### Standard API
| Model | Total |
|-------|-------|
| Claude 4.6 Sonnet | $46.80 |
| GPT-5 mini | $5.00 |
| Gemini 2.5 Flash | $5.00 |
| Llama 4 Scout (Groq) | $1.08 |
| Grok 3 mini | $10.00 |
| **Subtotal** | **~$68** |

### Grand Total (with judge costs)
| Scenario | Completions | Judge | Buffer (15%) | Total |
|----------|-------------|-------|--------------|-------|
| **Standard API** | ~$68 | ~$102 | ~$26 | **~$196** |

Well within the $200-500 budget. The pivot from flagship reasoning models to mid-range non-reasoning models reduced completion costs by ~60%.

## Sunk Cost from Previous Lineup

| Model | Completions | Approximate Cost | Status |
|-------|-------------|-----------------|--------|
| GPT-5.2 | 1,406 | ~$20 | Archived (reasoning tokens, expensive) |
| Grok 3 | 732 | ~$15 | Archived (expensive, no reasoning control) |
| Claude Sonnet 4.6 | 197 | ~$5 | Archived (restarting fresh) |
| Llama 4 Scout | 300 | ~$0.08 | Archived (restarting fresh) |
| Gemini 2.5 Pro | 0 | ~$0 | Never completed (quota exhausted) |
| **Total sunk** | **2,635** | **~$40** | All archived in results/archive/ |

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
| reasoning_effort | Yes (pass-through) | Varies |

## Sources
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Groq Pricing](https://groq.com/pricing)
- [xAI Models and Pricing](https://docs.x.ai/developers/models)
- [LiteLLM Docs](https://docs.litellm.ai/docs/)
