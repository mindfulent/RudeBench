# Benchmark Repository Structure Research

## Repos Analyzed

| Repo | Type | Prompt Format | Results Format | Config |
|------|------|---------------|----------------|--------|
| ELEPHANT | Paper companion | CSV | Notebooks + CSV | None (env vars) |
| BullshitBench | Small benchmark | JSON | JSONL + CSV | JSON at root |
| lm-eval-harness | Framework | YAML + Jinja2 | JSON (runtime) | YAML per task + CLI |
| MT-Bench | Judge benchmark | JSONL | JSONL per model | CLI args only |
| Arena-Hard | Judge benchmark | JSONL | JSONL per model | YAML in `config/` |
| Inspect AI | Framework | Python + YAML | Log format | Python + YAML + CLI |

## Universal Conventions

- **JSONL for prompts and results** (MT-Bench, Arena-Hard, BullshitBench)
- **One results file per model** (`{model-id}.jsonl`)
- **3-step pipeline:** `gen_completions` → `gen_judgments` → `show_results` (MT-Bench, Arena-Hard)
- **`data/` directory** for questions + generated outputs
- **YAML config** in `config/` directory (Arena-Hard pattern)
- **Results organized by judge model:** `judgments/{judge}/{model}.jsonl`
- **Notebooks for paper analysis** (ELEPHANT)
- **Summary CSV committed, raw JSONL gitignored**

## Recommended RudeBench Structure

```
RudeBench/
├── README.md
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── config/
│   ├── default.yaml              # Run settings (temperature, max_tokens, num_runs)
│   ├── models.yaml               # Model list + provider/parallelism settings
│   └── judge.yaml                # Judge model, prompt templates, rubrics
│
├── data/
│   └── prompts.jsonl             # 200 prompts (50 tasks × 4 tones)
│
├── rudebench/                    # Python package
│   ├── __init__.py
│   ├── gen_completions.py        # Step 1: Call model APIs
│   ├── gen_judgments.py           # Step 2: Run LLM judge
│   ├── show_results.py           # Step 3: Aggregate + display
│   └── utils.py                  # API clients, retry logic, I/O helpers
│
├── results/                      # Generated outputs (mostly gitignored)
│   ├── completions/              # Raw model outputs
│   │   └── {model-id}.jsonl
│   ├── judgments/                 # Judge scores
│   │   └── {judge-model}/
│   │       └── {model-id}.jsonl
│   ├── leaderboard.csv           # Summary (committed)
│   └── summary.json              # Aggregate stats (committed)
│
├── analysis/
│   ├── main_results.ipynb        # Paper Table 1, Figure 1
│   ├── tone_breakdown.ipynb      # Per-tone analysis
│   └── inter_judge_agreement.ipynb
│
├── paper/
│   ├── figures/                  # Generated PNGs/SVGs
│   └── tables/                   # Generated LaTeX tables
│
├── scripts/
│   ├── run_all.sh                # Full pipeline
│   └── export_leaderboard.py     # Format for publication
│
├── tests/
│   └── test_scoring.py
│
└── docs/
    ├── RudeBench_Research_Briefing.md
    ├── RudeBench_Paper_Draft.docx
    └── research/                 # Pre-TDD research notes
```

## Prompt Schema (JSONL)

```json
{
  "id": "coding_fibonacci_hostile",
  "task_id": "coding_fibonacci",
  "domain": "coding",
  "tone": "hostile",
  "prompt": "This stupid Fibonacci function is broken...",
  "word_count": 41,
  "dimensions": ["ACC", "SYC", "PBR", "VRB", "APO"],
  "metadata": {
    "difficulty": "easy",
    "has_false_premise": false,
    "pushback_expected": false
  }
}
```

## Config Schemas

### `config/default.yaml`
```yaml
bench_name: rudebench-v1.0
data_file: data/prompts.jsonl
generation:
  temperature: 0.7
  max_tokens: 2048
  num_runs: 10
output_dir: results
```

### `config/models.yaml`
```yaml
models:
  - id: claude-sonnet-4.6
    provider: anthropic
    model: claude-sonnet-4-6-20250514
    parallel: 16
  - id: gpt-5.2
    provider: openai
    model: gpt-5.2
    parallel: 32
  - id: gemini-2.5-pro
    provider: google
    model: gemini-2.5-pro
    parallel: 16
  - id: llama-4-scout
    provider: groq
    model: llama-4-scout
    parallel: 32
  - id: grok-3
    provider: xai
    model: grok-3
    parallel: 16
```

## .gitignore Recommendations

```
.env
results/completions/
results/judgments/
# Keep committed:
# results/leaderboard.csv
# results/summary.json
```

## Sources

- [ELEPHANT](https://github.com/myracheng/elephant)
- [BullshitBench](https://github.com/petergpt/bullshit-benchmark)
- [Arena-Hard-Auto](https://github.com/lmarena/arena-hard-auto)
- [MT-Bench / FastChat](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge)
- [lm-eval-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai)
