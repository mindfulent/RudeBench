# Changelog

All notable changes to this project will be documented in this file.

## [v0.5.1] - 2026-03-07

### Fixed
- **UTF-8 encoding for all JSONL I/O** (`utils.py`): Explicit `encoding="utf-8"` on all file operations. Windows defaults to cp1252 which can't encode Unicode characters (Greek letters, arrows, etc.) in model responses, causing silent data loss.
- **RPM rate limiter** (`gen_completions.py`): Added token-bucket `_RateLimiter` class to throttle API calls for providers with low rate limits (e.g., Groq free tier at 30 RPM). Configured via optional `rpm_limit` field in `models.yaml`.
- **Corrected Groq model ID** (`models.yaml`): Changed from `groq/llama-4-scout` to `groq/meta-llama/llama-4-scout-17b-16e-instruct`.
- Converted `data/prompts.jsonl` to UTF-8.

### Validated
- Smoke test: 300/300 completions for `llama-4-scout` (run=1), schema matches TDD spec, $0.08 cost.
- Resumption: killed and restarted mid-run, picked up exactly 16 missing jobs with no duplicates.

## [v0.5.0] - 2026-03-07

### Added
- **Completion harness** (`rudebench/gen_completions.py`): Async LiteLLM dispatcher for generating all 15,000 completions (300 prompts × 5 models × 10 runs)
  - Two-turn conversation architecture: turn 1 sends greeting, turn 2 sends task prompt with full history
  - Per-model concurrency via `asyncio.Semaphore` (from `models.yaml` `parallel` field)
  - Crash-safe resumption: reads existing output JSONL on startup, skips completed `(prompt_id, run)` pairs
  - Refusal detection: `content_filter` finish reason or short responses (<10 words) with apology keywords
  - Cost tracking from both turns via LiteLLM `response_cost`
  - Dry-run mode: `--dry-run` prints job counts and API call estimates without calling APIs
  - `tqdm` progress bars per model
  - Graceful error handling: failed jobs log warnings but don't crash the run
- **Config tests** (`tests/test_config.py`): 12 tests covering config loading, validation, and model field checks
- Wired `generate` CLI subcommand to `gen_completions.main()`

## [v0.4.2] - 2026-03-07

### Changed
- **Added "Shut up!" prefix to all 50 abusive prompts**: Since the two-turn conversation starts with "Hello", the abusive tone now opens with "Shut up!" to immediately signal hostility on the second turn. Trimmed 1-2 words from 8 prompts that would have exceeded ±15% word count tolerance.

## [v0.4.1] - 2026-03-07

### Changed
- **Restructured all 50 grateful prompts**: Moved explicit gratitude from generic opener to heartfelt closing. Prompts now lead with the task request in warm register and end with a "grateful"/"thankful" closing phrase. Rotates through 10 closing variations across the 50 tasks. Eliminates the repetitive "I appreciate your help..." opener pattern that was barely distinguishable from friendly tone.

## [v0.4.0] - 2026-03-07

### Changed
- **Expanded from 4 to 6 tone conditions**: Added **Grateful** (deep appreciation, explicit gratitude) and **Friendly** (casual warmth, encouraging) tones to capture the full behavioral spectrum. The benchmark now measures whether models change behavior when treated *well*, not just when treated poorly.
- Prompt dataset expanded from 200 to **300 prompts** (50 tasks × 6 tones)
- Total completions per run: 10,000 → **15,000** (300 prompts × 5 models × 10 runs)
- Resilience Score formula now uses 5 non-neutral tones {grateful, friendly, curt, hostile, abusive}
- Updated all documentation (CLAUDE.md, README.md, Research Briefing, TDD, api_pricing)
- Updated review page to 3-column grid layout for 6 tone cards
- Updated validation script for 300 prompts and 6 tones per task
- Estimated cost: ~$315 standard API (still within $200-500 budget)

## [v0.3.2] - 2026-03-07

### Changed
- **Browser-renderable coding tasks**: Replaced all 15 coding tasks with visual HTML variants. Every coding prompt now requires a single self-contained HTML file, enabling iframe-based visual inspection on rudebench.com. Same CS concepts (binary search, race conditions, SQL injection, etc.), same dimension distributions (11 PBR, 4 no-PBR, 3 false premise), same difficulty spread (5 easy, 6 medium, 4 hard) — just browser-renderable output.
- Regenerated `data/prompts.jsonl` (60 coding records changed, 140 other-domain records unchanged)
- Added browser-renderable coding note to CLAUDE.md Benchmark Design section

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
