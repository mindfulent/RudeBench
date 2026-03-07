# Changelog

All notable changes to this project will be documented in this file.

## [v0.3.1] - 2026-03-07

### Changed
- **Two-turn conversation architecture**: Each completion now uses a two-turn flow — turn 1 sends a fixed greeting ("Hello"), turn 2 sends the task prompt with full conversation history. Only the turn-2 response is judged. This creates more ecologically valid scenarios where the model has already committed to a helpful persona before encountering hostile tone.
- Added `greeting` field to `config/default.yaml` generation section (single source of truth)
- Added `greeting` to required generation config keys in `rudebench/config.py`
- Updated completion schema in TDD with `greeting_response` and `greeting_tokens` fields
- Updated Phase 2 harness design in TDD to show two-step API flow
- Updated cost budget (~$112 → ~$115, trivial increase for greeting turns)
- Added two-turn architecture to CLAUDE.md benchmark design section
- Updated Research Briefing evaluation protocol and Phase 3 description
- Added clarifying comments to `config/judge.yaml` noting turn-2-only evaluation

## [v0.3.0] - 2026-03-07

### Added
- **Prompt dataset**: 200 validated prompts in `data/prompts.jsonl` (50 tasks × 4 tones)
  - 15 coding tasks, 12 creative writing, 13 analysis & advice, 10 factual Q&A
  - 30 tasks with pushback expected (PBR dimension), 12 with creative risk (CRE)
  - All non-neutral variants within ±15% word count of neutral baseline
- Validation script (`scripts/validate_prompts.py`) with 10 automated checks and `--report` flag for word count deviation table
- Prompt build script (`scripts/build_prompts.py`) for reproducible dataset generation
- Pytest wrapper (`tests/test_prompts.py`) with per-check test functions for granular failure reporting
- Wired `validate` subcommand in CLI (`python -m rudebench validate`)

## [v0.2.0] - 2026-03-07

### Added
- Installable Python package scaffold (`pyproject.toml`, `rudebench/` package)
- CLI entry point with subcommands: `validate`, `generate`, `judge`, `results`
- Config files: `config/default.yaml`, `config/models.yaml`, `config/judge.yaml` (from TDD Section 3.4)
- Config loader with validation (`rudebench/config.py`)
- JSONL I/O utilities: `read_jsonl`, `write_jsonl`, `append_jsonl` (`rudebench/utils.py`)
- Module stubs: `gen_completions.py`, `gen_judgments.py`, `show_results.py`
- `.env.example` with API key placeholders for all 5 providers
- `.gitignore` for Python, results, secrets
- Directory structure: `data/`, `results/`, `analysis/`, `paper/figures/`, `scripts/`, `tests/`

## [v0.1.4] - 2026-03-07

### Added
- Technical Design Document (`docs/TDD.md`) — complete implementation blueprint:
  - Tech stack: Python 3.10+, LiteLLM async, PyYAML, pandas, scipy, matplotlib, pytest
  - Full repository layout with .gitignore strategy
  - Data schemas: prompts JSONL, completions JSONL, judgments JSONL, YAML configs (default, models, judge)
  - 6 implementation phases (v0.2.0–v0.7.0) with acceptance criteria per phase
  - Judge design: tone firewall architecture, 5-level rubric anchors, validation experiment protocol, full prompt templates
  - Cost budget breakdown: ~$207 standard API, ~$106 with batch APIs
  - Testing strategy per phase

## [v0.1.3] - 2026-03-07

### Added
- Pre-TDD research documents in `docs/research/`:
  - `benchmark_harnesses.md` — Framework comparison (lm-eval-harness, Inspect AI, HELM, LiteLLM, Promptfoo, DeepEval). Recommendation: custom harness on LiteLLM.
  - `llm_judge.md` — Judge model selection, bias mitigation, "tone firewall" technique, prompt design, cost estimates.
  - `api_pricing.md` — Pricing for all 5 models, batch API discounts (50%), unified client comparison, total cost estimates ($75-165).
  - `repo_structure.md` — Analysis of 6 published benchmark repos, recommended directory structure and schemas.

## [v0.1.2] - 2026-03-07

### Changed
- Moved research briefing and paper draft into `docs/` folder
- Updated file path references in CLAUDE.md and README.md

## [v0.1.1] - 2026-03-07

### Added
- Research briefing document with complete benchmark design and methodology
- Paper draft (~80% complete, Section 5 pending benchmark results)
- Project setup: README.md, CLAUDE.md, CHANGELOG.md
- Git repository initialized and pushed to GitHub
