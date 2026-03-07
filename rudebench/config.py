"""YAML config loading and validation."""

from pathlib import Path

import yaml


REQUIRED_DEFAULT_KEYS = {"bench_name", "data_file", "output_dir", "generation"}
REQUIRED_GENERATION_KEYS = {"temperature", "max_tokens", "num_runs"}
REQUIRED_MODEL_KEYS = {"id", "litellm_model", "parallel", "env_key"}
REQUIRED_JUDGE_KEYS = {"primary_judge", "tone_firewall", "rubrics"}


def load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path) as f:
        return yaml.safe_load(f)


def validate_default(cfg: dict) -> None:
    """Validate default.yaml has all required fields."""
    missing = REQUIRED_DEFAULT_KEYS - set(cfg.keys())
    if missing:
        raise ValueError(f"default.yaml missing required keys: {missing}")
    gen = cfg["generation"]
    missing_gen = REQUIRED_GENERATION_KEYS - set(gen.keys())
    if missing_gen:
        raise ValueError(f"default.yaml generation section missing keys: {missing_gen}")


def validate_models(cfg: dict) -> None:
    """Validate models.yaml has all required fields."""
    if "models" not in cfg:
        raise ValueError("models.yaml missing 'models' key")
    for i, model in enumerate(cfg["models"]):
        missing = REQUIRED_MODEL_KEYS - set(model.keys())
        if missing:
            raise ValueError(f"models.yaml model [{i}] missing keys: {missing}")


def validate_judge(cfg: dict) -> None:
    """Validate judge.yaml has all required fields."""
    missing = REQUIRED_JUDGE_KEYS - set(cfg.keys())
    if missing:
        raise ValueError(f"judge.yaml missing required keys: {missing}")


def load_config(config_dir: str = "config") -> dict:
    """Load and validate all config files from a directory.

    Returns a merged dict with keys: default, models, judge.
    """
    config_path = Path(config_dir)

    default_cfg = load_yaml(config_path / "default.yaml")
    validate_default(default_cfg)

    models_cfg = load_yaml(config_path / "models.yaml")
    validate_models(models_cfg)

    judge_cfg = load_yaml(config_path / "judge.yaml")
    validate_judge(judge_cfg)

    return {
        "default": default_cfg,
        "models": models_cfg,
        "judge": judge_cfg,
    }
