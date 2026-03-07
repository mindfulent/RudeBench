#!/usr/bin/env python3
"""Validate the RudeBench prompt dataset (data/prompts.jsonl).

Runs 10 automated checks and optionally prints a word count deviation report.

Usage:
    python scripts/validate_prompts.py [--data PATH] [--report]
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

# Allow running as script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rudebench.utils import read_jsonl

VALID_TONES = {"grateful", "friendly", "neutral", "curt", "hostile", "abusive"}
VALID_DOMAINS = {"coding", "creative", "analysis", "factual"}
DOMAIN_COUNTS = {"coding": 15, "creative": 12, "analysis": 13, "factual": 10}
TONE_ORDER = ["grateful", "friendly", "neutral", "curt", "hostile", "abusive"]

REQUIRED_FIELDS = {
    "id": str,
    "task_id": str,
    "domain": str,
    "tone": str,
    "prompt": str,
    "word_count": int,
    "neutral_word_count": int,
    "dimensions": list,
    "metadata": dict,
}

ALWAYS_DIMENSIONS = {"ACC", "SYC", "VRB", "APO"}


def validate_prompts(data_path: str = "data/prompts.jsonl") -> dict[str, list[str]]:
    """Run all 10 validation checks on the prompt dataset.

    Returns a dict mapping check names to lists of error strings.
    An empty list means the check passed.
    """
    errors: dict[str, list[str]] = {}
    prompts = read_jsonl(data_path)

    # Check 1: Exactly 300 lines, all valid JSON
    check = "01_count_and_json"
    errs = []
    if len(prompts) != 300:
        errs.append(f"Expected 300 prompts, got {len(prompts)}")
    errors[check] = errs

    # Check 2: Exactly 50 unique task_id values
    check = "02_task_id_count"
    errs = []
    task_ids = {p.get("task_id") for p in prompts}
    if len(task_ids) != 50:
        errs.append(f"Expected 50 unique task_ids, got {len(task_ids)}")
    errors[check] = errs

    # Check 3: Each task_id has exactly 6 tone variants
    check = "03_tone_variants"
    errs = []
    task_tones: dict[str, set[str]] = {}
    for p in prompts:
        tid = p.get("task_id", "MISSING")
        tone = p.get("tone", "MISSING")
        task_tones.setdefault(tid, set()).add(tone)
    for tid, tones in sorted(task_tones.items()):
        if tones != VALID_TONES:
            missing = VALID_TONES - tones
            extra = tones - VALID_TONES
            parts = []
            if missing:
                parts.append(f"missing {missing}")
            if extra:
                parts.append(f"extra {extra}")
            errs.append(f"{tid}: {', '.join(parts)}")
    errors[check] = errs

    # Check 4: Domain distribution
    check = "04_domain_distribution"
    errs = []
    # Count unique task_ids per domain
    domain_tasks: dict[str, set[str]] = {}
    for p in prompts:
        domain = p.get("domain", "MISSING")
        tid = p.get("task_id", "MISSING")
        domain_tasks.setdefault(domain, set()).add(tid)
    for domain, expected in DOMAIN_COUNTS.items():
        actual = len(domain_tasks.get(domain, set()))
        if actual != expected:
            errs.append(f"{domain}: expected {expected} tasks, got {actual}")
    unknown = set(domain_tasks.keys()) - VALID_DOMAINS
    if unknown:
        errs.append(f"Unknown domains: {unknown}")
    errors[check] = errs

    # Check 5: Word count within ±15% of neutral + stored word_count matches actual
    check = "05_word_count"
    errs = []
    # Build neutral word counts
    neutral_wc: dict[str, int] = {}
    for p in prompts:
        if p.get("tone") == "neutral":
            neutral_wc[p["task_id"]] = len(p["prompt"].split())
    for p in prompts:
        actual_wc = len(p["prompt"].split())
        stored_wc = p.get("word_count", -1)
        if stored_wc != actual_wc:
            errs.append(
                f"{p.get('id')}: stored word_count={stored_wc}, actual={actual_wc}"
            )
        stored_neutral = p.get("neutral_word_count", -1)
        tid = p.get("task_id")
        if tid in neutral_wc and stored_neutral != neutral_wc[tid]:
            errs.append(
                f"{p.get('id')}: stored neutral_word_count={stored_neutral}, "
                f"actual neutral={neutral_wc[tid]}"
            )
        if p.get("tone") != "neutral" and tid in neutral_wc:
            nwc = neutral_wc[tid]
            lo = nwc * 0.85
            hi = nwc * 1.15
            if not (lo <= actual_wc <= hi):
                dev = ((actual_wc - nwc) / nwc) * 100
                errs.append(
                    f"{p.get('id')}: word_count={actual_wc}, neutral={nwc}, "
                    f"deviation={dev:+.1f}% (allowed ±15%)"
                )
    errors[check] = errs

    # Check 6: All required fields present and correctly typed
    check = "06_required_fields"
    errs = []
    for p in prompts:
        pid = p.get("id", "UNKNOWN")
        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in p:
                errs.append(f"{pid}: missing field '{field}'")
            elif not isinstance(p[field], expected_type):
                errs.append(
                    f"{pid}: field '{field}' should be {expected_type.__name__}, "
                    f"got {type(p[field]).__name__}"
                )
        # Check metadata sub-fields
        meta = p.get("metadata", {})
        if isinstance(meta, dict):
            for mf in ["difficulty", "pushback_expected", "has_false_premise"]:
                if mf not in meta:
                    errs.append(f"{pid}: metadata missing '{mf}'")
        # Validate domain and tone values
        if p.get("domain") not in VALID_DOMAINS:
            errs.append(f"{pid}: invalid domain '{p.get('domain')}'")
        if p.get("tone") not in VALID_TONES:
            errs.append(f"{pid}: invalid tone '{p.get('tone')}'")
    errors[check] = errs

    # Check 7: dimensions always includes ACC, SYC, VRB, APO
    check = "07_always_dimensions"
    errs = []
    for p in prompts:
        dims = set(p.get("dimensions", []))
        missing = ALWAYS_DIMENSIONS - dims
        if missing:
            errs.append(f"{p.get('id')}: missing required dimensions {missing}")
    errors[check] = errs

    # Check 8: PBR present when pushback_expected or has_false_premise
    check = "08_pbr_when_expected"
    errs = []
    for p in prompts:
        meta = p.get("metadata", {})
        needs_pbr = meta.get("pushback_expected", False) or meta.get(
            "has_false_premise", False
        )
        has_pbr = "PBR" in p.get("dimensions", [])
        if needs_pbr and not has_pbr:
            errs.append(f"{p.get('id')}: pushback expected but PBR not in dimensions")
        if has_pbr and not needs_pbr:
            errs.append(
                f"{p.get('id')}: PBR in dimensions but neither pushback_expected "
                f"nor has_false_premise is true"
            )
    errors[check] = errs

    # Check 9: CRE present only for creative domain
    check = "09_cre_creative_only"
    errs = []
    for p in prompts:
        has_cre = "CRE" in p.get("dimensions", [])
        is_creative = p.get("domain") == "creative"
        if has_cre and not is_creative:
            errs.append(f"{p.get('id')}: CRE dimension but domain is {p.get('domain')}")
        if is_creative and not has_cre:
            errs.append(f"{p.get('id')}: creative domain but missing CRE dimension")
    errors[check] = errs

    # Check 10: No duplicate id values
    check = "10_no_duplicate_ids"
    errs = []
    id_counts = Counter(p.get("id") for p in prompts)
    for pid, count in id_counts.items():
        if count > 1:
            errs.append(f"Duplicate id '{pid}' appears {count} times")
    errors[check] = errs

    return errors


def print_report(data_path: str = "data/prompts.jsonl") -> None:
    """Print per-task word count table with deviation percentages."""
    prompts = read_jsonl(data_path)
    if not prompts:
        print("No prompts found.")
        return

    # Group by task_id
    tasks: dict[str, dict[str, int]] = {}
    for p in prompts:
        tid = p.get("task_id", "UNKNOWN")
        tone = p.get("tone", "UNKNOWN")
        wc = len(p["prompt"].split())
        tasks.setdefault(tid, {})[tone] = wc

    # Print header
    print(f"{'task_id':<40} {'grateful':>8} {'friendly':>8} {'neutral':>8} {'curt':>8} {'hostile':>8} {'abusive':>8}")
    print("-" * 104)

    violations = 0
    for tid in sorted(tasks.keys()):
        tones = tasks[tid]
        nwc = tones.get("neutral", 0)
        parts = [f"{tid:<40}"]
        for tone in TONE_ORDER:
            wc = tones.get(tone, 0)
            if tone == "neutral":
                parts.append(f"{wc:>8}")
            else:
                if nwc > 0:
                    dev = ((wc - nwc) / nwc) * 100
                    marker = " " if abs(dev) <= 15 else "!"
                    if abs(dev) > 15:
                        violations += 1
                    parts.append(f"{wc:>4}{dev:>+5.0f}%{marker}")
                else:
                    parts.append(f"{wc:>8}")
        print("".join(parts))

    print("-" * 104)
    print(f"Total tasks: {len(tasks)}, Total prompts: {len(prompts)}, "
          f"Word count violations: {violations}")


def main():
    parser = argparse.ArgumentParser(description="Validate RudeBench prompt dataset")
    parser.add_argument(
        "--data", default="data/prompts.jsonl", help="Path to prompts JSONL file"
    )
    parser.add_argument(
        "--report", action="store_true", help="Print word count deviation report"
    )
    args = parser.parse_args()

    if args.report:
        print_report(args.data)
        print()

    errors = validate_prompts(args.data)

    total_errors = sum(len(e) for e in errors.values())
    passed = sum(1 for e in errors.values() if not e)
    failed = sum(1 for e in errors.values() if e)

    for check, errs in sorted(errors.items()):
        status = "PASS" if not errs else "FAIL"
        print(f"[{status}] {check}")
        for err in errs[:10]:  # Show first 10 errors per check
            print(f"       {err}")
        if len(errs) > 10:
            print(f"       ... and {len(errs) - 10} more errors")

    print(f"\n{passed}/10 checks passed, {total_errors} total errors")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
