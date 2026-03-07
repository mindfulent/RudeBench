"""Pytest wrapper for RudeBench prompt validation.

Runs the 10-check validation once (module-scoped fixture) and exposes
each check as an individual test for granular failure reporting.
"""

import pytest

from scripts.validate_prompts import validate_prompts

DATA_PATH = "data/prompts.jsonl"


@pytest.fixture(scope="module")
def validation_results():
    """Run all validation checks once and cache results."""
    return validate_prompts(DATA_PATH)


def _assert_check(results: dict, check_name: str):
    errs = results.get(check_name, ["check not found"])
    assert not errs, f"{check_name} failed:\n" + "\n".join(errs)


def test_count_and_json(validation_results):
    _assert_check(validation_results, "01_count_and_json")


def test_task_id_count(validation_results):
    _assert_check(validation_results, "02_task_id_count")


def test_tone_variants(validation_results):
    _assert_check(validation_results, "03_tone_variants")


def test_domain_distribution(validation_results):
    _assert_check(validation_results, "04_domain_distribution")


def test_word_count(validation_results):
    _assert_check(validation_results, "05_word_count")


def test_required_fields(validation_results):
    _assert_check(validation_results, "06_required_fields")


def test_always_dimensions(validation_results):
    _assert_check(validation_results, "07_always_dimensions")


def test_pbr_when_expected(validation_results):
    _assert_check(validation_results, "08_pbr_when_expected")


def test_cre_creative_only(validation_results):
    _assert_check(validation_results, "09_cre_creative_only")


def test_no_duplicate_ids(validation_results):
    _assert_check(validation_results, "10_no_duplicate_ids")
