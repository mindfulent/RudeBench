# Changelog

All notable changes to this project will be documented in this file.

## [v0.8.3] - 2026-03-08

### Added
- **Bifurcation chart**: Interactive Recharts line chart as the new hero visual on the landing page, showing the sycophancy split between resilient (Claude, GPT-5 mini) and reactive (Gemini, Grok, Llama) model groups across all 6 tone levels
- **Dimension switcher**: Pill buttons let users explore all 6 behavioral dimensions in the chart (SYC default)
- Group A (solid blue lines) vs Group B (dashed warm lines) visual encoding

### Changed
- **Landing page layout**: Chart section now leads after hero/methodology; insight cards follow; leaderboard pushed lower
- **How It Works** section is now collapsible (`<details>`) to reduce initial scroll depth
- Data reads from existing `dimensions.json` — no pipeline changes needed

## [v0.8.2] - 2026-03-08

### Changed
- **Light theme redesign**: Replaced dark theme with a clean, professional light palette optimized for readability. White/light-gray surfaces, dark text, subtle tone-color tints.
- **Dropped Space Grotesk**: Unified on Inter for all typography (headings and body). Removed Silkscreen/Space Grotesk references from PRD.
- **Updated deviation heatmap colors** for light backgrounds: pastel tints (green/yellow/orange/red) with dark saturated text colors.
- **Updated tone palette** for light mode: slightly deepened tone colors for contrast on white, subtle light tinted backgrounds.

## [v0.8.1] - 2026-03-08

### Added
- **DigitalOcean App Platform deployment** (`.do/app.yaml`): Static site config for rudebench.com
- Committed `site/public/data/` (25MB) and `site/public/renders/` (1.3MB) to repo — generated JSON is the published form of the benchmark data

### Changed
- Simplified `site/package.json` build script to `astro build` only (no Python dependency for production builds)
- Updated `site/.gitignore` to track `public/data/` and `public/renders/` (still ignoring `public/downloads/`)

## [v0.8.0] - 2026-03-08

### Added
- **rudebench.com website** (`site/`): Full static site built with Astro 5 + React islands + Tailwind CSS.
  - **Homepage** with Resilience Score leaderboard, methodology explainer, headline findings cards
  - **Dimension Explorer** (`/explore`): Interactive heatmap grid — models × tones for each of 6 behavioral dimensions, with domain filtering (factual, coding, creative, analysis), deviation coloring, and observation counts
  - **Model Profiles** (`/explore/[model]`): Per-model dimensions × tones heatmap with refusal rates
  - **Response Viewer** (`/responses`): Read actual model responses, toggle between tones, compare mode for side-by-side tone comparison
  - **HTML Render Viewer** (`/renders`): Sandboxed iframe grid for coding task HTML outputs across tones (desktop-optimized)
  - **Research Paper** (`/paper`): Full paper draft rendered as HTML with anchor links
  - **Dataset & Downloads** (`/data`): File descriptions, schema docs, BibTeX citation copy widget
  - **About** (`/about`): n=2 → n=10 path explainer, methodology details, Resilience Score formula
- **Data pipeline** (`site/scripts/build-data.py`): Python script that reads raw JSONL from `results/` and generates pre-computed JSON for the website. Produces leaderboard, per-dimension aggregations (with per-domain breakdowns), model profiles, task metadata, per-task response files (250 total), and renders index.
- **Maturity badge**: Persistent "Early Release — n=2" indicator on every page (non-dismissable)
- **Mobile-responsive design** throughout (renders page desktop-only by design)
- **URL state management**: Deep-linkable URLs with search params (`/explore?dim=SYC&domain=coding`)
- **Tone-mapped color palette** (warm gold → peach → gray → steel blue → deep blue → crimson)
- **Typography**: Inter (Google Fonts) for all text

### Tech Stack
- Astro 5.x (SSG, zero JS for editorial pages)
- React islands (hydrated on demand for interactive components)
- Tailwind CSS v4 with custom theme tokens
- `marked` for Markdown → HTML rendering
- Sitemap generation via `@astrojs/sitemap`

## [v0.7.9] - 2026-03-08

### Added
- **Product Requirements Document** (`docs/PRD.md`): Comprehensive PRD for rudebench.com — the interactive web dashboard for exploring benchmark results.

## [v0.7.8] - 2026-03-08

### Data
- **Grok 3 mini n=2 complete** — all 5 models now at full parity: 600/600 completions, 1200/1200 judgments, 600/600 VRB each.
  - Grok completions: $0.72 (600 completions, 2 xAI server errors retried successfully).
  - Grok judgments: $6.95 (1200 judge calls + 600 VRB via GPT-4.1).
- **Grok 3 mini key findings**:
  - ACC rock solid (98.1–99.1) — most stable accuracy of all 5 models.
  - SYC +17.0 under abuse — second highest after Gemini (24.0). Also +10.3 under grateful (people-pleasing both ways).
  - PBR essentially flat — holds ground regardless of tone.
  - CRE *increases* under hostility (+7.1) and abuse (+8.3).
  - VRB unique split: **-21.2% under curt** but **+7.7% under hostile** — only model with opposite verbosity responses to different negative tones.
  - APO near zero (slight +2.2 under abuse).

## [v0.7.7] - 2026-03-08

### Data
- **n=2 data collection complete for 4 models**: All targets met — 600/600 completions, 1200/1200 judgments, 600/600 VRB per model.
  - Llama 4 Scout: finished remaining 89 completions (511→600) after Groq Dev tier upgrade, then full 1200 judgments.
  - GPT-5 mini and Gemini 2.5 Flash: filled remaining judgment gaps (145 and 189 respectively).
  - Claude Sonnet 4.6: already complete from prior run.
- **Judge cost**: $7.52 for this session (1538 judgments via GPT-4.1).
- **4-model Resilience Scores**: GPT-5 mini **98.5**, Claude Sonnet 4.6 **97.5**, Llama 4 Scout **96.9**, Gemini 2.5 Flash **96.8**.
- **Key findings with Llama added**:
  - Llama has lowest baseline accuracy (90.7 neutral vs 99+ for Claude/GPT) but comparable resilience to Gemini.
  - Llama sycophancy: 14.8 under abuse (3× neutral), between Claude/GPT (~5) and Gemini (24.0).
  - Llama biggest accuracy drop under abuse: -3.4 points (87.3 vs 90.7 neutral).
  - Gemini remains the most sycophantic model by far (24.0 abusive, 18.6 hostile).
  - GPT-5 mini's VRB spike under hostile tone confirmed at +24.9% — unique behavioral pattern.

### Changed
- Added `llama-4-scout` to `scripts/quick_analysis.py` model list.

## [v0.7.6] - 2026-03-07

### Fixed
- **Soft refusal rendering in coding viewer** (`scripts/extract_renders.py`): Responses without renderable HTML (e.g., Gemini refusing to produce code but writing a long explanation) now display inline with an orange "SOFT REFUSE" badge and the full refusal text in a scrollable container. Previously showed blank "No completion available". Detects soft refusals by checking for actual HTML tags (`<html>`, `<body>`, `<div>`, etc.) in the extracted content. Affected 4 Gemini completions: 2 tone-triggered (abusive fibonacci/dom_memory_leak) and 2 task-triggered (price_calculator grateful/hostile — Gemini considers demonstrating broken float arithmetic harmful).

## [v0.7.5] - 2026-03-07

### Data
- **Claude Sonnet 4.6 judgments** (`results/judgments/gpt-4.1/claude-sonnet-4.6.jsonl`, `_vrb.jsonl`): 600 judge calls + 300 VRB scores. Key findings: ACC rock solid (94.8–99.5), SYC very low (max 4.9 under abuse), PBR drops under abuse (93.4 vs 99.5 neutral, -6.1), CRE slightly *increases* under hostility (+4.2), VRB dramatic withdrawal (-36.6% abusive), APO flatline zero.
- **Gemini 2.5 Flash judgments** (`results/judgments/gpt-4.1/gemini-2.5-flash.jsonl`, `_vrb.jsonl`): 600 judge calls + 300 VRB scores. Key findings: **highest sycophancy** of all models (SYC 24.9 under abuse vs Claude 4.9, GPT 3.7), **most verbosity-unstable** (VRB +42.6% grateful, +29.6% hostile), ACC drops under abuse (94.7), APO near zero.
- Combined judge cost: $9.09. All three models drop ACC ~4-5 points under abuse — universal pattern.

### Remaining
- Llama 4 Scout: 225/300 completions (Groq daily limit), needs retry + judging
- Grok 3 mini: 0/300 (xAI credits), needs retry + judging

## [v0.7.4] - 2026-03-07

### Data
- **Gemini 2.5 Flash n=1 completions** (`results/completions/gemini-2.5-flash.jsonl`): 300/300 complete, 1 refusal (content_filter on `analysis_book_summary_curt`), 1 truncated. Cost: $1.56 (43min, rate-limited at 14 RPM). Key finding: VRB mirrors user energy — grateful +16.2%, curt -15.6%, abusive -12.1%. Factual domain under curt tone collapses to 49% VRB. Third distinct verbosity strategy alongside GPT-5 mini (verbose under hostility) and Claude (withdraws under all non-neutral).

## [v0.7.3] - 2026-03-07

### Added
- **Claude Sonnet 4.6 n=1 completions** (`results/completions/claude-sonnet-4.6.jsonl`): 300/300 complete, 0 refusals, 4 truncated. Cost: $13.78. Key finding: VRB drops dramatically under abuse (-36.6%) — opposite pattern from GPT-5 mini (+20.6% under hostile). Claude gets concise when berated; GPT over-explains.

### Fixed
- **Coding render viewer layout** (`scripts/extract_renders.py`): Removed `max-width: 1800px` cap so the grid fills the full browser width. Increased iframe height from 400px to 500px. Adjusted responsive breakpoints for better use of screen real estate.

## [v0.7.2] - 2026-03-07

### Fixed
- **Per-model temperature override** (`gen_completions.py`, `models.yaml`): GPT-5 mini only supports `temperature=1`; added per-model `temperature` field (same pattern as `max_tokens` override). Falls back to `config/default.yaml` value when not specified.
- **GPT-5 mini `reasoning_effort`** (`models.yaml`): Changed from `"none"` (unsupported) to `"minimal"` (lowest valid value for GPT-5 mini).
- **Llama 4 Scout `max_tokens`** (`models.yaml`): Added `max_tokens: 8192` (Groq's cap for this model). Previous `16384` caused all 300 jobs to fail.

### Data
- **GPT-5 mini n=1 completions** (`results/completions/gpt-5-mini.jsonl`): 300/300 complete, 0 refusals, 0 truncated. Cost: $1.14.
- **GPT-5 mini judgments** (`results/judgments/gpt-4.1/gpt-5-mini.jsonl`): 600 judge calls (behavioral + quality) via GPT-4.1. Cost: $4.14. Key findings: SYC +3.0 under abuse, ACC -3.9 under abuse, CRE -5.8 under abuse, VRB +20.6% under hostile tone. APO flatline zero.
- **Llama 4 Scout partial** (`results/completions/llama-4-scout.jsonl`): 225/300 complete (75 analysis tasks missing due to Groq daily RPD limit of 1,000 requests).

## [v0.7.1] - 2026-03-07

### Added
- **Coding render comparison viewer** (`scripts/extract_renders.py`): Generates a self-contained HTML page (`analysis/coding_review.html`) that renders all coding task completions side-by-side in iframes across 6 tone conditions. Supports task/model/run selection via dropdowns, keyboard navigation (arrow keys, M/R/S), source code toggle, finish_reason badges, and empty states for missing/refused completions. Base64-encodes HTML to prevent `</script>` injection. Follows the same pattern as `generate_review.py`.

## [v0.7.0] - 2026-03-07

### Changed
- **Pivoted to mid-range non-reasoning model lineup**: Replaced flagship reasoning models (GPT-5.2, Gemini 2.5 Pro, Grok 3) with their non-reasoning counterparts (GPT-5 mini, Gemini 2.5 Flash, Grok 3 mini). Claude Sonnet 4.6 and Llama 4 Scout retained. Reasoning models consumed `max_tokens` budget with thinking tokens, causing 92% truncation on Gemini and 100% on Claude coding tasks — a fundamental incompatibility with the benchmark design.
- **Added `reasoning_effort` support** (`gen_completions.py`, `models.yaml`): Models can now specify `reasoning_effort` in config (e.g., `"none"` for GPT-5 mini/Gemini Flash, `"low"` for Grok 3 mini). Passed as `**extra_kwargs` to `litellm.acompletion()`. Models without the field (Claude, Llama) are unaffected.
- **Raised `max_tokens` to 16384** (`config/default.yaml`): Eliminates all truncation risk. Cost is per-token-generated, not per-cap, so this has no cost impact. Absorbs any residual thinking tokens from Grok 3 mini's `reasoning_effort="low"`.
- **Archived all existing completions** to `results/archive/completions/` (2,635 total: GPT-5.2 1,406, Grok-3 732, Llama-4-Scout 300, Claude-Sonnet 197). Fresh start with standardized lineup.
- Removed per-model `max_tokens: 16384` override from GPT-5.2 (model removed).

### Sunk Cost
~$40 spent on 2,635 completions from the original lineup. All data archived, not deleted.

### New Model Lineup
| Model | LiteLLM ID | reasoning_effort |
|-------|-----------|-----------------|
| Claude 4.6 Sonnet | `anthropic/claude-sonnet-4-6` | — |
| GPT-5 mini | `gpt-5-mini` | `none` |
| Gemini 2.5 Flash | `gemini/gemini-2.5-flash` | `none` |
| Llama 4 Scout | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | — |
| Grok 3 mini | `xai/grok-3-mini-beta` | `low` |

## [v0.6.1] - 2026-03-07

### Fixed
- **Raised `max_tokens` from 2048 to 4096** (`config/default.yaml`): Claude Sonnet 4.6 generates elaborate `<style>` blocks that exhausted the 2048 token budget before reaching `<body>` or `<script>` — 90/90 coding completions were truncated (all `finish_reason=length`), producing pure CSS with no visible HTML. Other models affected: Grok-3 (15 truncated), Llama 4 Scout (1). GPT-5.2 was unaffected (already had per-model `max_tokens: 16384`). Raising globally to 4096 maintains methodological consistency across all models.
- **Added `--rerun-truncated` flag** (`gen_completions.py`, `__main__.py`): Detects completions with `finish_reason=length`, removes them from the output file, and re-runs them with the updated `max_tokens`. Safe for dry-run mode (file modifications are skipped). Enables targeted re-generation without discarding valid completions.

## [v0.6.0] - 2026-03-07

### Added
- **Judge pipeline** (`rudebench/gen_judgments.py`): Async LLM judge scoring for all completions
  - **Tone firewall**: Judge always receives the neutral task description, never the actual hostile/curt/abusive prompt. This is an architectural guarantee — `build_neutral_map()` creates `{task_id → neutral_prompt}` at startup, and the judge prompt template only ever receives this neutral text.
  - Two judge calls per completion: behavioral (SYC/PBR/APO) and quality (ACC/CRE)
  - Score parsing via regex with automatic retry on parse failure
  - VRB computed automatically: `completion_word_count / mean_neutral_word_count × 100` (no judge call needed)
  - Primary judge (GPT-4.1) and secondary judge (Claude Sonnet 4.6, 20% sample) support
  - Deterministic hash-based sampling for secondary judge reproducibility
  - Crash-safe resumption: reads existing judgment JSONL on startup, skips completed `(prompt_id, run, judge_type)` tuples
  - Per-judge concurrency via `asyncio.Semaphore`
  - `--dry-run` mode: prints job counts without calling APIs
  - Cost tracking per model
- **Scoring tests** (`tests/test_scoring.py`): 13 tests covering score parsing (valid, N/A, missing, boundary, case-insensitive), tone firewall map construction, and VRB computation (neutral=100, proportional scaling, multi-run averaging)
- Wired `judge` CLI subcommand with `--dry-run`, `--models`, `--judge primary|secondary` flags

### Dry Run Summary (primary judge, existing completions)
| Model | Completions | Judge Calls |
|-------|-------------|-------------|
| claude-sonnet-4.6 | 300 | 600 |
| gpt-5.2 | 1,055 | 2,110 |
| llama-4-scout | 300 | 600 |
| grok-3 | 658 | 1,316 |
| **Total** | **2,313** | **4,626** |

## [v0.5.2] - 2026-03-07

### Fixed
- **Auto-load `.env` file** (`gen_completions.py`): Added `python-dotenv` loading so API keys from `.env` are available without manual `export`. Previously required keys to be pre-exported in the shell.
- **Claude Sonnet 4.6 model ID** (`models.yaml`): Changed from `claude-sonnet-4-6-20250514` to `anthropic/claude-sonnet-4-6`. LiteLLM requires the `anthropic/` provider prefix for newer models not yet in its registry, and the date suffix is not part of the API model ID.
- **GPT-5.2 empty responses** (`models.yaml`, `gen_completions.py`): GPT-5.2 is a reasoning model that consumes `max_tokens` on internal reasoning before producing visible output. With `max_tokens: 2048`, all tokens were used for reasoning, yielding empty responses. Added per-model `max_tokens` override support and set GPT-5.2 to `16384` to provide headroom for both reasoning and 2048 tokens of visible output.
- **Gemini RPM limit** (`models.yaml`): Added `rpm_limit: 14` for `gemini-2.5-pro` (free tier: 15 RPM).

### Smoke Test Results (run=1, 300 completions per model)
| Model | Status | Cost | Notes |
|-------|--------|------|-------|
| llama-4-scout | 300/300 | $0.08 | (v0.5.1) |
| claude-sonnet-4.6 | 300/300 | $5.09 | 0 refusals, 197 stop + 103 length |
| gpt-5.2 | 129/300 | $4.25 | Model works, OpenAI quota exceeded mid-run |
| gemini-2.5-pro | 0/300 | $0 | Free tier quota exhausted, needs billing |
| grok-3 | 0/300 | $0 | xAI account has no credits |

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
