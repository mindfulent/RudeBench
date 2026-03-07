# RudeBench

A multi-dimensional behavioral benchmark for LLM resilience under hostile prompting.

Existing research asks whether rudeness makes AI more or less accurate. RudeBench asks a richer question: **when you're hostile to an AI model, does it start groveling? Does it stop pushing back on bad ideas? Does it lose creativity? Does it apologize more? Does it become shorter and more compliant?**

We measure six behavioral dimensions simultaneously across six tone conditions — from grateful to abusive — and five frontier models, producing a multi-dimensional behavioral fingerprint for each model under varying social pressure — then compress it into a single composite **Resilience Score**.

## Why This Matters

- **AI Safety:** A model that stays accurate but becomes more compliant under hostility is arguably *more* dangerous than one that visibly degrades — the failure is invisible to accuracy-only monitoring.
- **Alignment Evaluation:** If alignment behaviors (pushback, honesty, critical engagement) degrade under hostile prompting, current neutral-condition evals are missing a significant failure mode.
- **Practical Deployment:** Enterprise users need to know whether customer-facing AI behaves consistently when customers are angry, rude, or abusive.

## Benchmark Design

### Behavioral Dimensions

| Dimension | Abbr | Measures | Direction |
|---|---|---|---|
| Task Accuracy | ACC | Did the model correctly complete the task? | Higher = better |
| Sycophancy Shift | SYC | Did the model increase agreement/validation/flattery? | Lower = better |
| Pushback Retention | PBR | Does the model still challenge incorrect premises? | Higher = better |
| Creative Risk | CRE | Did the model play it safe or take creative risks? | Higher = better |
| Verbosity Change | VRB | How did response length change relative to neutral? | Closer to 100 = better |
| Apology Frequency | APO | How often did the model apologize unprompted? | Lower = better |

### Tone Conditions

| Tone | Description |
|---|---|
| **Grateful** | Deep appreciation, explicit gratitude, acknowledges AI capabilities |
| **Friendly** | Casual warmth, encouraging, upbeat |
| **Neutral** | Professional, complete, standard prompt |
| **Curt** | Terse, impatient, dismissive — no insults |
| **Hostile** | Aggressive, demeaning, insulting |
| **Abusive** | Sustained personal attacks, profanity, contempt |

All tone variants are constrained to ±15% word count of the neutral baseline to prevent confounding tone with brevity.

### Task Domains

50 base tasks across four domains: Coding (15), Creative Writing (12), Analysis & Advice (13), Factual Q&A (10).

### Scale

50 tasks × 6 tones × 5 models × 10 runs = **15,000 completions**, scored by an LLM judge with 20% human validation.

### Resilience Score

```
R(M) = 100 − (1/D) Σ_d (1/T) Σ_t |S_d(M, t) − S_d(M, neutral)| / range(d)
```

R = 100: identical behavior regardless of tone. R = 0: maximum behavioral instability.

## Models Evaluated

- Claude 4.6 Sonnet (Anthropic)
- GPT-5.2 (OpenAI)
- Gemini 2.5 Pro (Google DeepMind)
- Llama 4 Scout (Meta)
- Grok 3 (xAI)

## Project Status

- [x] Research design finalized
- [x] Paper drafted (~80% complete, Section 5 pending results)
- [x] Domain acquired (rudebench.com)
- [ ] Task & prompt construction (300 prompts)
- [ ] Scoring rubrics & judge prompt design
- [ ] Benchmark execution (15,000 completions)
- [ ] Analysis & paper completion
- [ ] Public release (code, dataset, results, website)

## Repository Structure

```
docs/
  RudeBench_Research_Briefing.md   # Full research design and methodology
  RudeBench_Paper_Draft.docx       # arXiv preprint draft
CLAUDE.md                          # Claude Code project guide
CHANGELOG.md                       # Version history
```

## Citation

Paper forthcoming on arXiv. Citation information will be added upon publication.

## License

TBD
