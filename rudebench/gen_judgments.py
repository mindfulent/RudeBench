"""Step 2: LLM judge scoring with tone firewall."""

import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import litellm
from tqdm import tqdm

from rudebench.config import load_config
from rudebench.utils import append_jsonl, read_jsonl

logger = logging.getLogger(__name__)

litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# Regex to parse judge scores from structured output
SCORE_RE = re.compile(r"(\w+)_SCORE:\s*(\d+|N/A)", re.IGNORECASE)
EVIDENCE_RE = re.compile(r"(\w+)_EVIDENCE:\s*(.+?)(?=\n\w+_|$)", re.DOTALL | re.IGNORECASE)
REASONING_RE = re.compile(r"(\w+)_REASONING:\s*(.+?)(?=\n\w+_|$)", re.DOTALL | re.IGNORECASE)


def parse_judge_output(text: str, dimensions: list[str]) -> tuple[dict, dict]:
    """Parse structured judge output into scores and justifications dicts.

    Returns (scores, justifications) where scores map dimension -> int|None
    and justifications map dimension -> str.
    """
    scores = {}
    justifications = {}

    score_matches = {m.group(1).upper(): m.group(2) for m in SCORE_RE.finditer(text)}
    evidence_matches = {m.group(1).upper(): m.group(2).strip() for m in EVIDENCE_RE.finditer(text)}
    reasoning_matches = {m.group(1).upper(): m.group(2).strip() for m in REASONING_RE.finditer(text)}

    for dim in dimensions:
        raw = score_matches.get(dim)
        if raw is None or raw.upper() == "N/A":
            scores[dim] = None
        else:
            try:
                scores[dim] = int(raw)
            except ValueError:
                scores[dim] = None

        parts = []
        if dim in evidence_matches:
            parts.append(evidence_matches[dim])
        if dim in reasoning_matches:
            parts.append(reasoning_matches[dim])
        justifications[dim] = " | ".join(parts) if parts else ""

    return scores, justifications


def build_neutral_map(prompts: list[dict]) -> dict[str, str]:
    """Build {task_id -> neutral_prompt_text} lookup for tone firewall."""
    neutral_map = {}
    for p in prompts:
        if p["tone"] == "neutral":
            neutral_map[p["task_id"]] = p["prompt"]
    return neutral_map


def build_reference_map(prompts: list[dict]) -> dict[str, str]:
    """Build {task_id -> reference_answer} lookup."""
    ref_map = {}
    for p in prompts:
        if p["tone"] == "neutral":
            ref_map[p["task_id"]] = p.get("metadata", {}).get("reference_answer", "")
    return ref_map


def build_dimensions_map(prompts: list[dict]) -> dict[str, list[str]]:
    """Build {task_id -> dimensions} lookup."""
    dim_map = {}
    for p in prompts:
        if p["tone"] == "neutral":
            dim_map[p["task_id"]] = p.get("dimensions", [])
    return dim_map


def compute_vrb(completions: list[dict], prompts: list[dict]) -> list[dict]:
    """Compute VRB scores for all completions.

    VRB = (completion_word_count / mean_neutral_word_count) * 100
    For neutral completions, VRB = 100 by definition.
    """
    # Group neutral completion word counts by (task_id, model_id)
    neutral_wc: dict[tuple[str, str], list[int]] = {}
    for c in completions:
        prompt = next((p for p in prompts if p["id"] == c["prompt_id"]), None)
        if prompt and prompt["tone"] == "neutral":
            key = (c["task_id"], c["model_id"])
            neutral_wc.setdefault(key, []).append(c["word_count"])

    # Compute mean neutral word count per (task_id, model_id)
    mean_neutral: dict[tuple[str, str], float] = {}
    for key, counts in neutral_wc.items():
        mean_neutral[key] = sum(counts) / len(counts)

    vrb_records = []
    for c in completions:
        prompt = next((p for p in prompts if p["id"] == c["prompt_id"]), None)
        if not prompt:
            continue

        key = (c["task_id"], c["model_id"])
        if prompt["tone"] == "neutral":
            vrb = 100.0
        elif key in mean_neutral and mean_neutral[key] > 0:
            vrb = (c["word_count"] / mean_neutral[key]) * 100
        else:
            vrb = 100.0  # fallback if no neutral data

        vrb_records.append({
            "prompt_id": c["prompt_id"],
            "task_id": c["task_id"],
            "model_id": c["model_id"],
            "run": c["run"],
            "vrb_score": round(vrb, 1),
        })

    return vrb_records


def _get_cost(response) -> float:
    """Extract cost from a LiteLLM response."""
    try:
        return response._hidden_params.get("response_cost", 0) or 0
    except Exception:
        return 0


def _sample_completions(completions: list[dict], sample_rate: float, seed: str) -> list[dict]:
    """Deterministically sample a fraction of completions for secondary judge."""
    sampled = []
    for c in completions:
        # Deterministic hash-based sampling
        h = hashlib.md5(f"{seed}:{c['prompt_id']}:{c['run']}".encode()).hexdigest()
        if int(h[:8], 16) / 0xFFFFFFFF <= sample_rate:
            sampled.append(c)
    return sampled


async def _judge_one(
    sem: asyncio.Semaphore,
    judge_cfg: dict,
    prompt_template: str,
    neutral_desc: str,
    reference: str,
    response_text: str,
    completion: dict,
    judge_type: str,
    dimensions: list[str],
    output_path: Path,
    pbar: tqdm,
) -> float:
    """Run a single judge call. Returns cost_usd."""
    async with sem:
        try:
            judge_prompt = prompt_template.format(
                neutral_task_description=neutral_desc,
                reference_answer=reference or "No reference answer provided.",
                response=response_text,
            )

            r = await litellm.acompletion(
                model=judge_cfg["litellm_model"],
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.0,
                max_tokens=1024,
                num_retries=3,
            )

            judge_response = r.choices[0].message.content or ""
            cost = _get_cost(r)

            scores, justifications = parse_judge_output(judge_response, dimensions)

            # Check if parsing failed (all scores None)
            all_none = all(v is None for v in scores.values())
            if all_none and dimensions:
                # Retry once with explicit format instruction
                retry_msg = (
                    "Your previous response could not be parsed. "
                    "Please respond EXACTLY in the required format with lines like:\n"
                    "DIM_EVIDENCE: ...\nDIM_REASONING: ...\nDIM_SCORE: [0-100 or N/A]\n\n"
                    + judge_prompt
                )
                r2 = await litellm.acompletion(
                    model=judge_cfg["litellm_model"],
                    messages=[{"role": "user", "content": retry_msg}],
                    temperature=0.0,
                    max_tokens=1024,
                    num_retries=3,
                )
                judge_response = r2.choices[0].message.content or ""
                cost += _get_cost(r2)
                scores, justifications = parse_judge_output(judge_response, dimensions)

            record = {
                "prompt_id": completion["prompt_id"],
                "task_id": completion["task_id"],
                "model_id": completion["model_id"],
                "run": completion["run"],
                "judge_model": judge_cfg["litellm_model"],
                "judge_type": judge_type,
                "scores": scores,
                "justifications": justifications,
                "raw_judge_response": judge_response,
                "cost_usd": round(cost, 6),
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            append_jsonl(output_path, record)
            pbar.update(1)
            return cost

        except Exception as e:
            logger.warning(
                "Judge failed: model=%s prompt=%s run=%d type=%s error=%s",
                completion["model_id"], completion["prompt_id"], completion["run"], judge_type, e,
            )
            pbar.update(1)
            return 0.0


async def main(
    config_dir: str = "config",
    models_filter: str | None = None,
    judge_type: str = "primary",
    dry_run: bool = False,
):
    """Run LLM judge on all completions."""
    cfg = load_config(config_dir)
    default = cfg["default"]
    judge_cfg = cfg["judge"]
    output_dir = Path(default["output_dir"])
    completions_dir = output_dir / "completions"
    data_file = default["data_file"]

    # Select judge
    if judge_type == "secondary":
        if "secondary_judge" not in judge_cfg:
            print("No secondary judge configured in judge.yaml")
            return
        active_judge = judge_cfg["secondary_judge"]
        sample_rate = active_judge.get("sample_rate", 0.20)
    else:
        active_judge = judge_cfg["primary_judge"]
        sample_rate = 1.0

    judge_model_id = active_judge["litellm_model"]
    # Use a clean directory name from the model ID
    judge_dir_name = judge_model_id.replace("/", "_")
    judgments_dir = output_dir / "judgments" / judge_dir_name

    # Load prompts and build tone firewall maps
    prompts = read_jsonl(data_file)
    if not prompts:
        print(f"No prompts found in {data_file}")
        return

    neutral_map = build_neutral_map(prompts)
    reference_map = build_reference_map(prompts)
    dimensions_map = build_dimensions_map(prompts)

    # Prompt-to-task lookup
    prompt_to_task = {p["id"]: p["task_id"] for p in prompts}

    # Rubric templates
    behavioral_template = judge_cfg["rubrics"]["behavioral"]["prompt_template"]
    quality_template = judge_cfg["rubrics"]["quality"]["prompt_template"]
    behavioral_dims = judge_cfg["rubrics"]["behavioral"]["dimensions"]
    quality_dims = judge_cfg["rubrics"]["quality"]["dimensions"]

    # Filter models
    all_models = cfg["models"]["models"]
    if models_filter:
        filter_ids = {m.strip() for m in models_filter.split(",")}
        models = [m for m in all_models if m["id"] in filter_ids]
    else:
        models = all_models

    total_cost = 0.0
    total_jobs = 0
    total_skipped = 0

    for model in models:
        comp_path = completions_dir / f"{model['id']}.jsonl"
        completions = read_jsonl(comp_path)
        if not completions:
            print(f"\n{model['id']}: no completions found, skipping.")
            continue

        # Sample for secondary judge
        if sample_rate < 1.0:
            completions = _sample_completions(completions, sample_rate, seed=judge_model_id)

        # Load existing judgments for resumption
        judgment_path = judgments_dir / f"{model['id']}.jsonl"
        existing = read_jsonl(judgment_path)
        done_set = {(r["prompt_id"], r["run"], r["judge_type"]) for r in existing}

        # Build job list: each completion needs behavioral + quality judge calls
        jobs = []
        for comp in completions:
            task_id = comp["task_id"]
            task_dims = dimensions_map.get(task_id, [])

            # Behavioral dimensions for this task
            b_dims = [d for d in behavioral_dims if d in task_dims]
            if b_dims and (comp["prompt_id"], comp["run"], "behavioral") not in done_set:
                jobs.append((comp, "behavioral", behavioral_template, b_dims))

            # Quality dimensions for this task
            q_dims = [d for d in quality_dims if d in task_dims]
            if q_dims and (comp["prompt_id"], comp["run"], "quality") not in done_set:
                jobs.append((comp, "quality", quality_template, q_dims))

        skipped = len(completions) * 2 - len(jobs)
        total_skipped += skipped

        if dry_run:
            print(f"\n[DRY RUN] {model['id']} (judge: {judge_model_id}):")
            print(f"  Completions:    {len(completions)}")
            if sample_rate < 1.0:
                print(f"  Sample rate:    {sample_rate:.0%}")
            print(f"  Already judged: {skipped}")
            print(f"  Jobs remaining: {len(jobs)}")
            print(f"  API calls:      {len(jobs)}")
            total_jobs += len(jobs)
            continue

        if not jobs:
            print(f"\n{model['id']}: all {skipped} judgments already done, skipping.")
            continue

        print(f"\n{model['id']}: {len(jobs)} judge jobs ({skipped} already done)")

        sem = asyncio.Semaphore(active_judge.get("parallel", 8))
        pbar = tqdm(total=len(jobs), desc=f"{model['id']} judge", unit="call")

        tasks = []
        for comp, jtype, template, dims in jobs:
            task_id = comp["task_id"]
            neutral_desc = neutral_map.get(task_id, "")
            reference = reference_map.get(task_id, "")

            tasks.append(_judge_one(
                sem=sem,
                judge_cfg=active_judge,
                prompt_template=template,
                neutral_desc=neutral_desc,
                reference=reference,
                response_text=comp["response"],
                completion=comp,
                judge_type=jtype,
                dimensions=dims,
                output_path=judgment_path,
                pbar=pbar,
            ))

        costs = await asyncio.gather(*tasks)
        pbar.close()

        model_cost = sum(costs)
        total_cost += model_cost
        total_jobs += len(jobs)
        print(f"  Cost: ${model_cost:.4f}")

    # Compute VRB for all models (no API calls)
    if not dry_run:
        print("\nComputing VRB scores...")
        for model in models:
            comp_path = completions_dir / f"{model['id']}.jsonl"
            completions = read_jsonl(comp_path)
            if not completions:
                continue
            vrb_records = compute_vrb(completions, prompts)
            vrb_path = judgments_dir / f"{model['id']}_vrb.jsonl"
            # Overwrite VRB file each time (it's computed, not incremental)
            from rudebench.utils import write_jsonl
            write_jsonl(vrb_path, vrb_records)
            print(f"  {model['id']}: {len(vrb_records)} VRB scores computed")

    if dry_run:
        print(f"\n[DRY RUN] Total: {total_jobs} judge calls across {len(models)} models")
        if total_skipped:
            print(f"  ({total_skipped} judgments already done)")
    else:
        print(f"\nDone. {total_jobs} judgments generated. Total cost: ${total_cost:.4f}")
