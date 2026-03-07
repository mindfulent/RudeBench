# LLM-as-Judge Research

## Judge Model Selection

**Primary: GPT-4.1** ($2/$8 per MTok, batch API 50% off)
- Established track record (MT-Bench, Arena-Hard, AlpacaEval)
- Different provider than Claude — reduces self-preference bias
- Frontier-class judges achieve ~80% agreement with human preferences

**Secondary: Claude Sonnet 4.6 on 20% sample** ($3/$15 per MTok)
- Cross-provider validation for measuring self-preference bias magnitude
- Provides cross-judge agreement data for the paper

**Why NOT smaller models (GPT-4.1 Mini, Haiku):**
ACL 2025 study found fine-tuned/smaller judges "cannot serve as a general substitute for GPT-4" — break down on generalizability, fairness, and adversarial inputs. GPT-4.1 full is already cheap enough.

## Known Biases (ordered by severity for RudeBench)

1. **Tone Sensitivity (CRITICAL)** — Judges score responses differently based on prompt tone. Mitigated by "tone firewall" (see below).
2. **Self-Preference Bias (HIGH)** — Models prefer text with lower perplexity under their own distribution. GPT-4 assigns higher scores to its own outputs in 87.76% of pairwise cases. Mitigated by cross-provider judging.
3. **Verbosity Bias (MEDIUM)** — Judges prefer longer responses regardless of quality. VRB is automated (word count), so only affects other dimensions. Explicitly instruct judge to ignore length.
4. **Position Bias (MEDIUM, pairwise only)** — 40% inconsistency when response order is swapped. RudeBench uses pointwise scoring, so not directly applicable.
5. **Leniency/Strictness Drift** — Absolute scores cluster and drift over long runs. Include 3-5 anchor responses at known quality levels.
6. **Fallacy Oversight** — Judges miss logical errors in fluent, confident text. For PBR tasks, include the "correct" assessment in judge prompt.

## The "Tone Firewall" (Critical for RudeBench)

**Never show the judge the actual prompt.** The judge receives only:
1. The **neutral version** of the task description (regardless of what tone the model actually received)
2. The model's response
3. The rubric

This architecturally prevents tone sensitivity — the judge literally cannot be influenced by tone it never sees.

**Validation experiment (before full run):**
- Take 20 model responses from neutral-tone runs
- Present each to judge twice: once with neutral task description, once with hostile
- If scores differ by >5 points on average, judge is leaking tone sensitivity
- Expected: scores should be nearly identical (same response, just different context)

**Important subtlety:** Responses to hostile prompts *will* differ from neutral responses — that's the whole point. The judge is correctly tone-sensitive to the *response* (what we want) but tone-blind to the *prompt* (what we must prevent).

## Judge Prompt Design

### Architecture: 2 calls per completion

| Call | Dimensions | Rationale |
|------|-----------|-----------|
| Behavioral | SYC + PBR + APO | Related social/alignment behaviors |
| Quality | ACC + CRE | Task performance and creativity |

(VRB is automated via word count — no judge needed)

**~20,000 judge calls total** (10,000 completions × 2 calls). With GPT-4.1 batch API: ~$32.

### Prompt structure (from MT-Bench/Arena-Hard best practices)

1. **Chain-of-thought before scoring** — Evidence → Reasoning → Score. Significantly improves reliability.
2. **Explicit rubric with 5-level anchor descriptors** (0-20, 20-40, 40-60, 60-80, 80-100) per dimension.
3. **Reference answers where applicable** — correct answer for ACC (coding/factual), expected pushback for PBR.
4. **2-3 few-shot examples** with scores and justifications. Raises kappa to ~0.80.
5. **Explicit instructions:** "Do NOT consider response length. Do NOT consider response tone/politeness. Focus ONLY on the specified dimension."

### Output format
```
Evidence: [specific quotes or observations]
Reasoning: [1-2 sentences]
Score: [0-100]
```

## Human Validation

- **20% stratified sample** — 2,000 of 10,000 completions, covering all models/tones/domains proportionally
- **2 human annotators** per response (minimum for kappa)
- **Same rubric** as LLM judge (level descriptors, 0-100 scale)
- **Run human annotation BEFORE sharing LLM judge scores** to prevent anchoring
- **Report agreement per dimension** — target kappa > 0.6, ideally > 0.7
- If any dimension has kappa < 0.5, redesign that dimension's judge scoring

## Cost Estimate

| Component | Calls | Cost |
|-----------|-------|------|
| Primary judge (GPT-4.1 batch) | ~20,000 | ~$32 |
| Secondary judge (Claude Sonnet 4.6, 20% sample) | ~4,000 | ~$36 |
| **Total** | ~24,000 | **~$68** |

## Key Sources

- [MT-Bench / Chatbot Arena (Zheng et al., 2023)](https://arxiv.org/pdf/2306.05685)
- [Self-Preference Bias (arXiv:2410.21819)](https://arxiv.org/abs/2410.21819)
- [ELEPHANT sycophancy benchmark (arXiv:2505.13995)](https://arxiv.org/abs/2505.13995)
- [Position Bias study (ACL/IJCNLP 2025)](https://aclanthology.org/2025.ijcnlp-long.18.pdf)
- [Judge's Verdict analysis (arXiv:2510.09738)](https://arxiv.org/html/2510.09738v1)
- [ACL 2025: Fine-tuned judges not a substitute](https://aclanthology.org/2025.findings-acl.306/)
