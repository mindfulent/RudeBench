# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RudeBench is a multi-dimensional behavioral benchmark measuring how LLMs change behavior (not just accuracy) under hostile prompting. It evaluates 5 frontier models across 6 behavioral dimensions, 4 tone conditions, and 4 task domains, producing a composite Resilience Score per model.

**Status:** Concept validated, paper ~80% drafted, benchmark not yet executed. No code exists yet.

**Domain:** rudebench.com (acquired)
**Budget:** $200–500 for initial benchmark run (~10,000 API completions + judge evaluations)

## Key Files

- `RudeBench_Research_Briefing.md` — Complete research design, methodology, and phase plan (the authoritative reference)
- `RudeBench_Paper_Draft.docx` — arXiv preprint draft; Section 5 (Results) is placeholder, everything else is complete

## Benchmark Design (Do Not Change Without Good Reason)

These decisions are deliberate and methodologically justified:

- **4 tone levels:** Neutral, Curt, Hostile, Abusive (no "Very Polite" — signal is on the hostile end)
- **±15% word count constraint** across tone variants — prevents confounding tone with brevity. This is the single most important methodological control.
- **6 behavioral dimensions:** ACC (accuracy), SYC (sycophancy), PBR (pushback retention), CRE (creative risk), VRB (verbosity change), APO (apology frequency)
- **50 base tasks × 4 tones × 5 models × 10 runs = 10,000 completions**
- **Temperature 0.7** for all runs (captures stochastic variation)
- **Max tokens 2048**, default system prompts only (no custom system prompts)
- **LLM-as-judge** with 20% human validation sample

### Task Domains

| Domain | Count | Purpose |
|---|---|---|
| Coding | 15 | Objective correctness, pushback on bad requirements, solution creativity |
| Creative Writing | 12 | Creativity/risk-taking, formulaic response detection |
| Analysis & Advice | 13 | Sycophancy and pushback measurement, highest deployment relevance |
| Factual Q&A | 10 | Accuracy baseline, control for tone-vs-difficulty confound |

### Resilience Score Formula

```
R(M) = 100 − (1/D) Σ_d (1/T) Σ_t |S_d(M, t) − S_d(M, neutral)| / range(d)
```

R = 100 means identical behavior regardless of tone. R = 0 means maximum behavioral instability.

## Models to Evaluate

| Model | SDK |
|---|---|
| Claude 4.6 Sonnet | `anthropic` |
| GPT-5.2 | `openai` |
| Gemini 2.5 Pro | `google-genai` |
| Llama 4 Scout | `together` or `fireworks` |
| Grok 3 | `xai` |

## Implementation Phases

1. **Task & Prompt Construction** — Design 50 tasks, write 200 tone variants (4 per task), tag applicable dimensions, validate ±15% word count
2. **Scoring Rubric & Judge Design** — LLM judge prompts per dimension, judge tone-sensitivity validation (run identical responses with different prompt contexts), human annotation rubric
3. **Benchmark Execution** — Python API harness reading JSONL prompts, rate limiting/retries/cost tracking, structured JSONL output
4. **Analysis & Paper** — Per-model/dimension/tone scores with CIs, significance tests, complete Section 5 of paper
5. **Release** — GitHub repo (code + dataset + results), update rudebench.com with real data, arXiv submission

## Critical Constraints

- **Judge validation is mandatory:** Before scoring results, verify the judge model scores identical responses identically regardless of what tone produced them. If tone-sensitive, redesign the judge prompt or switch judge models.
- **Model refusals are data, not errors.** Track refusal rates per tone level. Do not exclude them.
- **Not all dimensions apply to all tasks.** PBR applies to ~30/50 tasks (where pushback is appropriate). CRE applies to 12/50 (creative writing). ACC/SYC/VRB/APO apply to all.
- **Cost monitoring:** Track spend per model during execution. Can reduce to 5 runs/prompt or drop a model if budget is tight.

## Planned Technical Architecture

The API harness should:
- Read prompts from a JSONL file
- Run each prompt through each model's API (10 runs per prompt per model)
- Handle rate limiting, retries, and cost tracking
- Save raw completions in structured JSONL
- Support resumption (don't re-run completed prompt/model/run combinations)

Scoring outputs should include: per-dimension scores (0–100), judge justifications, and aggregate statistics (means, CIs, significance tests).

## Deliverables

- Benchmark code (Python)
- Prompt dataset (200 prompts, JSONL)
- Scoring rubrics and judge prompts
- Raw results (JSONL + Parquet)
- Analysis notebooks
- rudebench.com with real data
- arXiv preprint
