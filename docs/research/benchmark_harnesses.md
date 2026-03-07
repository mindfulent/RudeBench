# Benchmark Harness Framework Research

## Recommendation: Custom Python harness on LiteLLM (~200-400 lines)

### Why not existing frameworks?

| Framework | Verdict | Reason |
|-----------|---------|--------|
| lm-eval-harness | Overkill | Designed for scored academic evals with scorers/metrics pipeline. Fighting the framework to just "send and save." |
| Inspect AI | Strong but heavy | Best multi-provider support, clean Python API, but you write trivial solvers/scorers just to use it as a dispatcher. |
| HELM | Not practical | Heavyweight research platform. Custom scenarios require subclassing. Highest overhead. |
| Promptfoo | Closest off-the-shelf | JSONL output, resumption, rate limiting, repeat runs. But TypeScript/Node.js ecosystem. |
| DeepEval | Poor fit | Evaluation metrics framework (RAG, hallucination), not prompt dispatch. |

### What LiteLLM gives us for free

- Unified `acompletion()` for all 5 providers (OpenAI, Anthropic, Google, xAI, Together/Groq)
- Per-request cost in USD (`response._hidden_params["response_cost"]`)
- Automatic retries with exponential backoff (`num_retries=3`)
- Token counting across all providers
- Async support for high-throughput concurrent dispatch
- xAI Grok fully supported: `model="xai/grok-3-beta"`
- Together AI fully supported: `model="together_ai/..."`

### What we build ourselves (all straightforward)

1. **Prompt matrix generation** — Load 50 tasks × 4 tones from JSONL. Expand with 5 models × 10 runs = 10,000 jobs. Nested loop.
2. **Resumption** — Check if `(task_id, tone, model, run_number)` tuple exists in output JSONL. Skip if so. ~10 lines with set lookup.
3. **JSONL output** — Append one JSON line per completed request.
4. **Rate-limited async dispatch** — `asyncio.Semaphore` to cap concurrency per model. LiteLLM retries handle 429s.
5. **Progress tracking** — `tqdm` over the 10,000 jobs.

### Estimated effort
1-2 days for a solid, resumable harness vs. 1-2 weeks adapting a framework.
