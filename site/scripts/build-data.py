#!/usr/bin/env python
"""Build pre-computed JSON data files for the RudeBench website.

Reads raw JSONL from results/ and data/, outputs JSON to site/public/data/.
Reuses aggregation logic from scripts/quick_analysis.py.

Usage: python site/scripts/build-data.py
"""

import json
import statistics
import shutil
import re
import base64
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # RudeBench/
RESULTS = ROOT / "results"
DATA = ROOT / "data"
CONFIG = ROOT / "config"
OUT = Path(__file__).resolve().parent.parent / "public" / "data"

MODELS = ["claude-sonnet-4.6", "gpt-5-mini", "gemini-2.5-flash", "llama-4-scout", "grok-3-mini"]
TONES = ["grateful", "friendly", "neutral", "curt", "hostile", "abusive"]
DIMENSIONS = ["ACC", "SYC", "PBR", "CRE", "VRB", "APO"]

MODEL_DISPLAY = {
    "claude-sonnet-4.6": "Claude Sonnet 4.6",
    "gpt-5-mini": "GPT-5 mini",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "llama-4-scout": "Llama 4 Scout",
    "grok-3-mini": "Grok 3 mini",
}

DIMENSION_DESCRIPTIONS = {
    "ACC": "Task Accuracy — correctness and completeness of the response",
    "SYC": "Sycophancy — uncritical validation and excessive agreement",
    "PBR": "Pushback Retention — willingness to challenge false premises",
    "CRE": "Creative Risk — inventiveness and originality in creative tasks",
    "VRB": "Verbosity Change — response length relative to neutral baseline",
    "APO": "Apology Frequency — unnecessary or excessive apologizing",
}


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_tone(prompt_id: str) -> str:
    for t in TONES:
        if prompt_id.endswith(f"_{t}"):
            return t
    return "unknown"


def extract_task_id(prompt_id: str) -> str:
    for t in TONES:
        if prompt_id.endswith(f"_{t}"):
            return prompt_id[: -(len(t) + 1)]
    return prompt_id


def load_prompts() -> dict[str, dict]:
    """Load prompts indexed by prompt_id."""
    prompts = {}
    path = DATA / "prompts.jsonl"
    for rec in read_jsonl(path):
        prompts[rec["id"]] = rec
    return prompts


def load_judgments(model: str) -> list[dict]:
    path = RESULTS / "judgments" / "gpt-4.1" / f"{model}.jsonl"
    if not path.exists():
        return []
    return read_jsonl(path)


def load_vrb(model: str) -> list[dict]:
    path = RESULTS / "judgments" / "gpt-4.1" / f"{model}_vrb.jsonl"
    if not path.exists():
        return []
    return read_jsonl(path)


def load_completions(model: str) -> list[dict]:
    path = RESULTS / "completions" / f"{model}.jsonl"
    if not path.exists():
        return []
    return read_jsonl(path)


def compute_resilience(dim_tone_means: dict[str, dict[str, float]]) -> float:
    """Compute Resilience Score from dimension × tone means.

    R(M) = 100 - (100/D) * sum_d( mean_t(|S_d(M,t) - S_d(M,neutral)|) / range(d) )
    """
    parts = []
    for dim, tone_means in dim_tone_means.items():
        neutral = tone_means.get("neutral")
        if neutral is None:
            continue
        dim_range = 200.0 if dim == "VRB" else 100.0
        deltas = []
        for t, m in tone_means.items():
            if t != "neutral":
                deltas.append(abs(m - neutral))
        if deltas:
            parts.append(statistics.mean(deltas) / dim_range)
    if not parts:
        return 0.0
    return 100 - (100 / len(parts)) * sum(parts)


def build_meta() -> dict:
    total_completions = 0
    total_judgments = 0
    for model in MODELS:
        total_completions += len(load_completions(model))
        total_judgments += len(load_judgments(model))
        total_judgments += len(load_vrb(model))

    return {
        "version": "0.8.0",
        "n_runs": 2,
        "total_completions": total_completions,
        "total_judgments": total_judgments,
        "models": MODELS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_model_data(model: str) -> dict:
    """Build per-model aggregated data."""
    judgments = load_judgments(model)
    vrb_data = load_vrb(model)
    completions = load_completions(model)

    # Group scores by dimension × tone
    dim_tone_scores = defaultdict(lambda: defaultdict(list))
    for j in judgments:
        tone = extract_tone(j["prompt_id"])
        for dim, score in j.get("scores", {}).items():
            if score is not None:
                dim_tone_scores[dim][tone].append(score)

    for v in vrb_data:
        tone = extract_tone(v["prompt_id"])
        score = v.get("score", v.get("vrb_score"))
        if score is not None:
            dim_tone_scores["VRB"][tone].append(score)

    # Compute means and deltas
    dimensions = {}
    dim_tone_means = {}
    for dim in DIMENSIONS:
        tone_data = {}
        tone_means = {}
        for tone in TONES:
            scores = dim_tone_scores[dim].get(tone, [])
            if scores:
                tone_means[tone] = statistics.mean(scores)
                tone_data[tone] = {
                    "mean": round(statistics.mean(scores), 2),
                    "observation_count": len(scores),
                }
            else:
                tone_data[tone] = {"mean": None, "observation_count": 0}

        neutral_mean = tone_means.get("neutral")
        deltas = {}
        if neutral_mean is not None:
            for t, m in tone_means.items():
                if t != "neutral":
                    deltas[t] = abs(m - neutral_mean)

        avg_delta = round(statistics.mean(deltas.values()), 2) if deltas else 0
        worst_tone = max(deltas, key=deltas.get) if deltas else "neutral"

        dimensions[dim] = {
            "tones": tone_data,
            "neutral_mean": round(neutral_mean, 2) if neutral_mean is not None else None,
            "avg_delta": avg_delta,
            "worst_tone": worst_tone,
        }
        dim_tone_means[dim] = tone_means

    # Refusal counts
    refusal_counts = {}
    for tone in TONES:
        tone_completions = [c for c in completions if extract_tone(c["prompt_id"]) == tone]
        refusal_counts[tone] = {
            "refused": sum(1 for c in tone_completions if c.get("refused", False)),
            "total": len(tone_completions),
        }

    resilience = compute_resilience(dim_tone_means)

    return {
        "model": model,
        "display_name": MODEL_DISPLAY.get(model, model),
        "resilience_score": round(resilience, 1),
        "dimensions": dimensions,
        "refusal_counts": refusal_counts,
    }


def build_leaderboard(model_data: dict[str, dict]) -> list[dict]:
    """Build ranked leaderboard with tier banding."""
    entries = []
    for model in MODELS:
        md = model_data[model]
        dim_summaries = {}
        for dim in DIMENSIONS:
            d = md["dimensions"][dim]
            dim_summaries[dim] = {
                "neutral_mean": d["neutral_mean"],
                "avg_delta": d["avg_delta"],
                "worst_tone": d["worst_tone"],
                "observation_count": sum(
                    d["tones"][t]["observation_count"] for t in TONES
                ),
            }

        total_completions = sum(
            md["refusal_counts"][t]["total"] for t in TONES
        )
        total_refused = sum(
            md["refusal_counts"][t]["refused"] for t in TONES
        )

        entries.append({
            "model": model,
            "display_name": MODEL_DISPLAY.get(model, model),
            "resilience_score": md["resilience_score"],
            "rank": 0,
            "tier": 0,
            "dimensions": dim_summaries,
            "refusal_rate": round(total_refused / total_completions * 100, 1)
            if total_completions > 0 else 0,
        })

    # Sort by resilience score descending
    entries.sort(key=lambda e: e["resilience_score"], reverse=True)

    # Assign ranks and tiers (within 0.5 pts = same tier)
    tier = 1
    for i, entry in enumerate(entries):
        entry["rank"] = i + 1
        if i == 0:
            entry["tier"] = tier
        else:
            prev = entries[i - 1]
            if prev["resilience_score"] - entry["resilience_score"] > 0.5:
                tier += 1
            entry["tier"] = tier

    return entries


def build_dimensions(model_data: dict[str, dict], prompts: dict) -> list[dict]:
    """Build per-dimension aggregated data for the explorer, including per-domain breakdowns."""
    # Count applicable tasks per dimension
    task_dims = defaultdict(set)
    for p in prompts.values():
        task_id = p.get("task_id", extract_task_id(p["id"]))
        for dim in p.get("dimensions", []):
            task_dims[dim].add(task_id)

    total_tasks = len(set(p.get("task_id", extract_task_id(p["id"])) for p in prompts.values()))

    # Build prompt_id -> domain lookup
    prompt_domain = {}
    for p in prompts.values():
        prompt_domain[p["id"]] = p.get("domain", "unknown")

    # Build per-domain dimension data from raw judgments/VRB
    # Structure: domain_dim_scores[model][dim][domain][tone] = [scores]
    domain_dim_scores = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for model in MODELS:
        for j in load_judgments(model):
            tone = extract_tone(j["prompt_id"])
            domain = prompt_domain.get(j["prompt_id"], "unknown")
            for dim, score in j.get("scores", {}).items():
                if score is not None:
                    domain_dim_scores[model][dim][domain][tone].append(score)

        for v in load_vrb(model):
            tone = extract_tone(v["prompt_id"])
            domain = prompt_domain.get(v["prompt_id"], "unknown")
            score = v.get("score", v.get("vrb_score"))
            if score is not None:
                domain_dim_scores[model]["VRB"][domain][tone].append(score)

    dimensions = []
    for dim in DIMENSIONS:
        dim_range = [0, 200] if dim == "VRB" else [0, 100]
        models_data = {}
        for model in MODELS:
            md = model_data[model]
            d = md["dimensions"].get(dim)
            if d:
                # Build per-domain breakdown
                by_domain = {}
                for domain in ["factual", "coding", "creative", "analysis"]:
                    tone_data = {}
                    for tone in TONES:
                        scores = domain_dim_scores[model][dim][domain].get(tone, [])
                        if scores:
                            tone_data[tone] = {
                                "mean": round(statistics.mean(scores), 2),
                                "observation_count": len(scores),
                            }
                        else:
                            tone_data[tone] = {"mean": None, "observation_count": 0}

                    neutral_scores = domain_dim_scores[model][dim][domain].get("neutral", [])
                    neutral_mean = round(statistics.mean(neutral_scores), 2) if neutral_scores else None

                    # Only include domain if there's data
                    if any(td["mean"] is not None for td in tone_data.values()):
                        by_domain[domain] = {
                            "tones": tone_data,
                            "neutral_mean": neutral_mean,
                        }

                models_data[model] = {
                    "tones": d["tones"],
                    "neutral_mean": d["neutral_mean"],
                    "by_domain": by_domain,
                }

        dimensions.append({
            "dimension": dim,
            "description": DIMENSION_DESCRIPTIONS.get(dim, ""),
            "range": dim_range,
            "applicable_tasks": len(task_dims.get(dim, set())),
            "total_tasks": total_tasks,
            "models": models_data,
        })

    return dimensions


def build_tasks(prompts: dict) -> list[dict]:
    """Build task metadata index."""
    tasks = {}
    for p in prompts.values():
        task_id = p.get("task_id", extract_task_id(p["id"]))
        if task_id not in tasks:
            tasks[task_id] = {
                "id": task_id,
                "task_id": task_id,
                "domain": p.get("domain", "unknown"),
                "dimensions": p.get("dimensions", []),
                "difficulty": p.get("metadata", {}).get("difficulty", "unknown"),
                "has_false_premise": p.get("metadata", {}).get("has_false_premise", False),
                "pushback_expected": p.get("metadata", {}).get("pushback_expected", False),
            }
    return sorted(tasks.values(), key=lambda t: (t["domain"], t["id"]))


def build_responses(model: str, prompts: dict):
    """Build per-model per-task response JSON files."""
    completions = load_completions(model)
    judgments = load_judgments(model)
    vrb_data = load_vrb(model)

    # Index judgments by prompt_id + run
    judgment_index = {}
    for j in judgments:
        key = (j["prompt_id"], j.get("run", 1))
        judgment_index[key] = j

    vrb_index = {}
    for v in vrb_data:
        key = (v["prompt_id"], v.get("run", 1))
        vrb_index[key] = v

    # Group completions by task_id
    task_completions = defaultdict(list)
    for c in completions:
        task_id = extract_task_id(c["prompt_id"])
        task_completions[task_id].append(c)

    out_dir = OUT / "responses" / model
    out_dir.mkdir(parents=True, exist_ok=True)

    for task_id, comps in task_completions.items():
        # Group by tone
        tone_groups = defaultdict(list)
        for c in comps:
            tone = extract_tone(c["prompt_id"])
            tone_groups[tone].append(c)

        task_data = []
        for tone in TONES:
            tone_comps = tone_groups.get(tone, [])
            prompt_text = ""
            prompt_id = f"{task_id}_{tone}"
            if prompt_id in prompts:
                prompt_text = prompts[prompt_id].get("prompt", "")

            responses = []
            for c in sorted(tone_comps, key=lambda x: x.get("run", 1)):
                run = c.get("run", 1)
                j_key = (c["prompt_id"], run)
                j = judgment_index.get(j_key, {})
                v = vrb_index.get(j_key, {})

                scores = {}
                for dim_name, score_val in j.get("scores", {}).items():
                    scores[dim_name] = {
                        "score": score_val,
                        "evidence": j.get("evidence", {}).get(dim_name, ""),
                        "reasoning": j.get("reasoning", {}).get(dim_name, ""),
                    }

                responses.append({
                    "run": run,
                    "text": c.get("response", ""),
                    "word_count": c.get("word_count", 0),
                    "finish_reason": c.get("finish_reason", "unknown"),
                    "refused": c.get("refused", False),
                    "scores": scores,
                    "vrb_score": v.get("score", v.get("vrb_score")),
                })

            task_data.append({
                "prompt_id": prompt_id,
                "tone": tone,
                "prompt_text": prompt_text,
                "responses": responses,
            })

        out_path = out_dir / f"{task_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False)


def extract_html(response: str) -> str:
    """Extract HTML from a model response (same logic as extract_renders.py)."""
    fence_match = re.search(r"```(?:html)?\s*\n(.*?)```", response, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1).strip()
        if "<" in candidate:
            return candidate

    doctype_match = re.search(
        r"(<!DOCTYPE\s+html[^>]*>.*)", response, re.DOTALL | re.IGNORECASE
    )
    if doctype_match:
        candidate = doctype_match.group(1).strip()
        close_match = re.search(r"</html\s*>", candidate, re.IGNORECASE)
        if close_match:
            return candidate[: close_match.end()].strip()
        return candidate

    html_match = re.search(r"(<html[\s>].*)", response, re.DOTALL | re.IGNORECASE)
    if html_match:
        candidate = html_match.group(1).strip()
        close_match = re.search(r"</html\s*>", candidate, re.IGNORECASE)
        if close_match:
            return candidate[: close_match.end()].strip()
        return candidate

    return response


def build_renders_index():
    """Build renders index and copy render files to public/renders/."""
    renders_src = ROOT / "analysis" / "renders"
    renders_dst = OUT.parent / "renders"
    renders_dst.mkdir(parents=True, exist_ok=True)

    entries = []
    if renders_src.exists():
        for html_file in sorted(renders_src.glob("*.html")):
            # Parse filename: coding_task_slug_tone_model.html
            stem = html_file.stem
            # Copy file
            shutil.copy2(html_file, renders_dst / html_file.name)
            entries.append({"filename": html_file.name, "stem": stem})

    # Also generate renders from completions for models not in analysis/renders/
    tasks = set()
    models = set()
    structured_entries = []

    for entry in entries:
        stem = entry["stem"]
        # Extract model (last segment), tone (second to last from known tones)
        parts = stem.split("_")
        model_short = parts[-1]
        # Find tone in parts
        tone_found = None
        tone_idx = -1
        for i, p in enumerate(parts):
            if p in TONES:
                tone_found = p
                tone_idx = i
                break
        if tone_found and tone_idx > 0:
            task_id = "_".join(parts[:tone_idx])
            tasks.add(task_id)
            models.add(model_short)
            structured_entries.append({
                "task_id": task_id,
                "model": model_short,
                "tone": tone_found,
                "filename": entry["filename"],
            })

    index = {
        "tasks": sorted(tasks),
        "models": sorted(models),
        "entries": structured_entries,
    }

    out_path = OUT / "renders-index.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return len(structured_entries)


def build_domain_dimensions(prompts: dict) -> dict:
    """Build domain → dimensions mapping for domain filtering."""
    domain_dims = defaultdict(lambda: defaultdict(set))
    for p in prompts.values():
        domain = p.get("domain", "unknown")
        task_id = p.get("task_id", extract_task_id(p["id"]))
        for dim in p.get("dimensions", []):
            domain_dims[domain][dim].add(task_id)

    result = {}
    for domain, dims in domain_dims.items():
        result[domain] = {dim: len(tasks) for dim, tasks in dims.items()}
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    print("Loading prompts...")
    prompts = load_prompts()
    print(f"  {len(prompts)} prompts loaded")

    print("Building model data...")
    model_data = {}
    for model in MODELS:
        md = build_model_data(model)
        model_data[model] = md
        print(f"  {model}: R={md['resilience_score']}")

    print("Writing meta.json...")
    meta = build_meta()
    with open(OUT / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  {meta['total_completions']} completions, {meta['total_judgments']} judgments")

    print("Writing leaderboard.json...")
    leaderboard = build_leaderboard(model_data)
    with open(OUT / "leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

    print("Writing dimensions.json...")
    dimensions = build_dimensions(model_data, prompts)
    with open(OUT / "dimensions.json", "w", encoding="utf-8") as f:
        json.dump(dimensions, f, ensure_ascii=False, indent=2)

    print("Writing model profiles...")
    models_dir = OUT / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        with open(models_dir / f"{model}.json", "w", encoding="utf-8") as f:
            json.dump(model_data[model], f, ensure_ascii=False, indent=2)

    print("Writing tasks.json...")
    tasks = build_tasks(prompts)
    with open(OUT / "tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"  {len(tasks)} tasks")

    print("Writing response files...")
    resp_count = 0
    for model in MODELS:
        build_responses(model, prompts)
        model_dir = OUT / "responses" / model
        resp_count += len(list(model_dir.glob("*.json")))
    print(f"  {resp_count} response files")

    print("Building renders index...")
    render_count = build_renders_index()
    print(f"  {render_count} render entries")

    print("\nDone! Output written to site/public/data/")


if __name__ == "__main__":
    main()
