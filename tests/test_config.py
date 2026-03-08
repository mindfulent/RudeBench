"""Tests for config loading and validation."""

import pytest
from rudebench.config import load_config, validate_default, validate_models, validate_judge


class TestLoadConfig:
    """Test that load_config returns a valid merged config dict."""

    def test_loads_all_sections(self):
        cfg = load_config("config")
        assert "default" in cfg
        assert "models" in cfg
        assert "judge" in cfg

    def test_default_has_required_keys(self):
        cfg = load_config("config")
        d = cfg["default"]
        assert "bench_name" in d
        assert "data_file" in d
        assert "output_dir" in d
        assert "generation" in d

    def test_generation_has_required_keys(self):
        cfg = load_config("config")
        gen = cfg["default"]["generation"]
        assert "temperature" in gen
        assert "max_tokens" in gen
        assert "num_runs" in gen
        assert "greeting" in gen

    def test_generation_values(self):
        cfg = load_config("config")
        gen = cfg["default"]["generation"]
        assert gen["temperature"] == 0.7
        assert gen["max_tokens"] == 16384
        assert gen["num_runs"] == 1
        assert gen["greeting"] == "Hello"


class TestModelValidation:
    """Test that all 5 models load with correct fields."""

    def test_five_models_present(self):
        cfg = load_config("config")
        assert len(cfg["models"]["models"]) == 5

    def test_all_models_have_required_fields(self):
        cfg = load_config("config")
        for model in cfg["models"]["models"]:
            assert "id" in model
            assert "litellm_model" in model
            assert "parallel" in model
            assert "env_key" in model

    def test_model_ids(self):
        cfg = load_config("config")
        ids = {m["id"] for m in cfg["models"]["models"]}
        expected = {"claude-sonnet-4.6", "gpt-5-mini", "gemini-2.5-flash", "llama-4-scout", "grok-3-mini"}
        assert ids == expected

    def test_parallel_is_positive_int(self):
        cfg = load_config("config")
        for model in cfg["models"]["models"]:
            assert isinstance(model["parallel"], int)
            assert model["parallel"] > 0


class TestValidateDefault:
    """Test validate_default raises on missing keys."""

    def test_missing_top_level_key(self):
        with pytest.raises(ValueError, match="missing required keys"):
            validate_default({"generation": {"temperature": 0.7, "max_tokens": 2048, "num_runs": 10, "greeting": "Hello"}})

    def test_missing_generation_key(self):
        with pytest.raises(ValueError, match="generation section missing keys"):
            validate_default({
                "bench_name": "test",
                "data_file": "test.jsonl",
                "output_dir": "results",
                "generation": {"temperature": 0.7},
            })


class TestValidateModels:
    """Test validate_models raises on missing fields."""

    def test_missing_models_key(self):
        with pytest.raises(ValueError, match="missing 'models' key"):
            validate_models({})

    def test_missing_model_field(self):
        with pytest.raises(ValueError, match="missing keys"):
            validate_models({"models": [{"id": "test"}]})
