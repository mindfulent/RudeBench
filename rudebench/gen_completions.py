"""Step 1: Async LiteLLM dispatch for generating completions."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

import litellm
from tqdm import tqdm

from rudebench.config import load_config
from rudebench.utils import append_jsonl, read_jsonl, write_jsonl

logger = logging.getLogger(__name__)

# Suppress litellm's verbose logging
litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

REFUSAL_KEYWORDS = {"sorry", "cannot", "apologize", "unable", "won't", "can't"}


class _RateLimiter:
    """Simple token-bucket rate limiter for API calls per minute."""

    def __init__(self, rpm: int):
        self._interval = 60.0 / rpm  # seconds between allowed calls
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            wait = self._last + self._interval - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last = time.monotonic()


def _detect_refusal(text: str, finish_reason: str) -> bool:
    """Detect if a response is a refusal (turn-2 only)."""
    if finish_reason == "content_filter":
        return True
    if not text:
        return True
    words = text.split()
    if len(words) < 10:
        lower = text.lower()
        if any(kw in lower for kw in REFUSAL_KEYWORDS):
            return True
    return False


def _get_cost(response) -> float:
    """Extract cost from a LiteLLM response, falling back to 0."""
    try:
        return response._hidden_params.get("response_cost", 0) or 0
    except Exception:
        return 0


async def _run_job(
    sem: asyncio.Semaphore,
    rate_limiter: _RateLimiter | None,
    model: dict,
    prompt: dict,
    run: int,
    greeting: str,
    gen_cfg: dict,
    output_path: Path,
    pbar: tqdm,
) -> float:
    """Execute a single two-turn completion job. Returns cost_usd."""
    async with sem:
        try:
            t0 = time.time()

            # Per-model overrides
            max_tokens = model.get("max_tokens", gen_cfg["max_tokens"])
            temperature = model.get("temperature", gen_cfg["temperature"])

            # Extra kwargs (e.g., reasoning_effort for models that support it)
            extra_kwargs = {}
            if "reasoning_effort" in model:
                extra_kwargs["reasoning_effort"] = model["reasoning_effort"]

            # Turn 1: greeting
            if rate_limiter:
                await rate_limiter.acquire()
            r1 = await litellm.acompletion(
                model=model["litellm_model"],
                messages=[{"role": "user", "content": greeting}],
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=3,
                **extra_kwargs,
            )
            greeting_response = r1.choices[0].message.content or ""
            greeting_tokens = r1.usage.total_tokens if r1.usage else 0

            # Turn 2: task prompt with conversation history
            if rate_limiter:
                await rate_limiter.acquire()
            r2 = await litellm.acompletion(
                model=model["litellm_model"],
                messages=[
                    {"role": "user", "content": greeting},
                    {"role": "assistant", "content": greeting_response},
                    {"role": "user", "content": prompt["prompt"]},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                num_retries=3,
                **extra_kwargs,
            )

            latency_ms = int((time.time() - t0) * 1000)
            response_text = r2.choices[0].message.content or ""
            finish_reason = r2.choices[0].finish_reason or "unknown"

            # Cost from both turns
            cost1 = _get_cost(r1)
            cost2 = _get_cost(r2)

            # Refusal detection (turn 2 only)
            refused = _detect_refusal(response_text, finish_reason)

            record = {
                "prompt_id": prompt["id"],
                "task_id": prompt["task_id"],
                "model_id": model["id"],
                "run": run,
                "greeting_response": greeting_response,
                "greeting_tokens": greeting_tokens,
                "response": response_text,
                "word_count": len(response_text.split()),
                "input_tokens": r2.usage.prompt_tokens if r2.usage else 0,
                "output_tokens": r2.usage.completion_tokens if r2.usage else 0,
                "cost_usd": round(cost1 + cost2, 6),
                "latency_ms": latency_ms,
                "finish_reason": finish_reason,
                "refused": refused,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            append_jsonl(output_path, record)
            pbar.update(1)
            return record["cost_usd"]

        except Exception as e:
            logger.warning("Job failed: model=%s prompt=%s run=%d error=%s", model["id"], prompt["id"], run, e)
            pbar.update(1)
            return 0.0


async def main(config_dir: str = "config", models_filter: str | None = None, dry_run: bool = False, rerun_truncated: bool = False):
    """Generate completions for all models and prompts."""
    cfg = load_config(config_dir)
    default = cfg["default"]
    gen_cfg = default["generation"]
    greeting = gen_cfg["greeting"]
    num_runs = gen_cfg["num_runs"]
    output_dir = Path(default["output_dir"]) / "completions"
    data_file = default["data_file"]

    prompts = read_jsonl(data_file)
    if not prompts:
        print(f"No prompts found in {data_file}")
        return

    # Filter models
    all_models = cfg["models"]["models"]
    if models_filter:
        filter_ids = {m.strip() for m in models_filter.split(",")}
        models = [m for m in all_models if m["id"] in filter_ids]
        unknown = filter_ids - {m["id"] for m in models}
        if unknown:
            print(f"Warning: unknown model IDs ignored: {unknown}")
    else:
        models = all_models

    if not models:
        print("No models to run.")
        return

    total_cost = 0.0
    total_jobs = 0
    total_skipped = 0

    for model in models:
        output_path = output_dir / f"{model['id']}.jsonl"

        # Load existing completions for resumption
        existing = read_jsonl(output_path)

        # If rerunning truncated, remove completions with finish_reason="length"
        num_truncated = 0
        if rerun_truncated:
            truncated = [r for r in existing if r.get("finish_reason") == "length"]
            if truncated:
                num_truncated = len(truncated)
                kept = [r for r in existing if r.get("finish_reason") != "length"]
                if not dry_run:
                    write_jsonl(output_path, kept)
                existing = kept

        done_set = {(r["prompt_id"], r["run"]) for r in existing}

        # Build job list
        jobs = []
        for prompt in prompts:
            for run in range(1, num_runs + 1):
                if (prompt["id"], run) not in done_set:
                    jobs.append((prompt, run))

        skipped = len(prompts) * num_runs - len(jobs)
        total_skipped += skipped

        if dry_run:
            print(f"\n[DRY RUN] {model['id']}:")
            if num_truncated:
                print(f"  Truncated to re-run: {num_truncated}")
            print(f"  Total prompts:  {len(prompts)}")
            print(f"  Runs per prompt: {num_runs}")
            print(f"  Already done:   {skipped}")
            print(f"  Jobs remaining: {len(jobs)}")
            print(f"  API calls:      {len(jobs) * 2} (two-turn)")
            total_jobs += len(jobs)
            continue

        if not jobs:
            print(f"\n{model['id']}: all {skipped} completions already done, skipping.")
            continue

        if num_truncated:
            print(f"\n{model['id']}: {len(jobs)} jobs ({skipped} already done, {num_truncated} truncated removed)")
        else:
            print(f"\n{model['id']}: {len(jobs)} jobs ({skipped} already done)")

        sem = asyncio.Semaphore(model["parallel"])
        rpm = model.get("rpm_limit")
        rate_limiter = _RateLimiter(rpm) if rpm else None
        if rpm:
            print(f"  Rate limited: {rpm} RPM")
        pbar = tqdm(total=len(jobs), desc=model["id"], unit="job")

        tasks = [
            _run_job(sem, rate_limiter, model, prompt, run, greeting, gen_cfg, output_path, pbar)
            for prompt, run in jobs
        ]
        costs = await asyncio.gather(*tasks)
        pbar.close()

        model_cost = sum(costs)
        total_cost += model_cost
        total_jobs += len(jobs)
        print(f"  Cost: ${model_cost:.4f}")

    if dry_run:
        print(f"\n[DRY RUN] Total: {total_jobs} jobs, {total_jobs * 2} API calls across {len(models)} models")
        if total_skipped:
            print(f"  ({total_skipped} completions already done)")
    else:
        print(f"\nDone. {total_jobs} completions generated. Total cost: ${total_cost:.4f}")
