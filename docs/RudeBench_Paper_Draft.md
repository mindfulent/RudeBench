# RudeBench: A Multi-Dimensional Behavioral Benchmark for Evaluating LLM Resilience Under Hostile Prompting Conditions

**[Author Names]**

*[Affiliations]*

March 2026 --- Preprint

https://rudebench.com

## Abstract

Existing benchmarks for evaluating the effect of prompt tone on large language models (LLMs) focus narrowly on task accuracy (Dobariya & Kumar, 2025; Yin et al., 2024) or sycophancy in isolation (Cheng et al., 2025; Sharma et al., 2024). We introduce **RudeBench**, a multi-dimensional behavioral benchmark that measures how LLM behavior shifts across six tone conditions---Grateful, Friendly, Neutral, Curt, Hostile, and Abusive---applied to identical underlying tasks. Rather than asking whether rudeness improves accuracy, RudeBench asks a more fundamental question: *does hostile prompting change the behavioral character of model responses, and if so, how?* We evaluate five frontier models across 50 tasks spanning four domains, measuring six behavioral dimensions: task accuracy (ACC), sycophancy shift (SYC), pushback retention (PBR), creative risk-taking (CRE), verbosity change (VRB), and apology frequency (APO). We introduce a composite *Resilience Score* that quantifies the degree to which a model's behavioral profile remains stable regardless of user tone. Our evaluation of 3,000 completions across five frontier models reveals that all models score above 96 on Resilience (out of 100), but diverge sharply on *which* dimensions degrade. The headline finding is a clear bifurcation in sycophancy behavior: Claude Sonnet 4.6 and GPT-5 mini hold sycophancy below 5.0 across all tones, while Gemini 2.5 Flash (24.0), Grok 3 mini (21.6), and Llama 4 Scout (14.8) show sycophancy increases of 3--5x under abusive conditions. We release the full benchmark suite, dataset, scoring rubrics, and results to enable reproducible evaluation.

## 1 Introduction

The way humans communicate with AI systems is rarely neutral. Users bring frustration, impatience, humor, hostility, and warmth to their interactions---and a growing body of evidence suggests that this emotional context affects model outputs in measurable ways. A viral genre of social media content has emerged around deliberately hostile interactions with AI chatbots, where creators berate and demean models while demanding complex outputs. This phenomenon raises an empirical question: *does the tone of a prompt systematically alter the behavioral characteristics of a model's response, beyond task accuracy?*

Prior work has begun to address adjacent questions. Dobariya & Kumar (2025) found that rude prompts improved ChatGPT-4o accuracy by approximately 4 percentage points on multiple-choice questions, while Yin et al. (2024) found the opposite pattern in cross-lingual settings. The ELEPHANT benchmark (Cheng et al., 2025) measures social sycophancy---a model's tendency to preserve user "face"---but evaluates this as a baseline property rather than a tone-dependent variable. SycEval (Fanous et al., 2025) provides cross-model sycophancy comparisons, and BullshitBench (Gostev, 2025) tests whether models challenge nonsensical premises.

These benchmarks share a common limitation: they treat model behavior as either *accurate or inaccurate*, or *sycophantic or not*. None characterize the full behavioral fingerprint---the multi-dimensional profile of how a model's response character changes under different tonal conditions. A model might maintain accuracy under hostile prompting while simultaneously becoming more sycophantic, less creative, and more likely to apologize unprompted. These behavioral shifts are invisible to accuracy-only benchmarks but may be consequential for real-world deployment, alignment evaluation, and the growing public discourse around model welfare.

We introduce RudeBench to fill this gap. Our contributions are:

1. A benchmark framework that evaluates LLM behavioral shifts across six tone conditions and six behavioral dimensions, providing a multi-dimensional characterization of tone sensitivity.

2. A composite Resilience Score that quantifies the stability of a model's behavioral profile under hostile prompting, enabling direct cross-model comparison.

3. An evaluation of five frontier models revealing significant, model-specific behavioral variation---including a clear two-tier bifurcation in sycophancy sensitivity and the finding that accuracy stability does not predict behavioral stability.

4. A fully open dataset, benchmark suite, and scoring rubrics to enable reproducibility and community extension.

## 2 Related Work

### 2.1 Prompt Tone and Model Performance

The relationship between prompt tone and LLM performance has attracted increasing research attention. Dobariya & Kumar (2025) conducted the most widely cited study, testing ChatGPT-4o on 50 multiple-choice questions rewritten across five politeness levels. Their finding that "very rude" prompts outperformed "very polite" ones (84.8% vs. 80.8% accuracy) generated substantial media coverage and public interest. However, several limitations constrain the generalizability of this result: the study tested a single model, used a small question set, and measured only factual accuracy on multiple-choice questions.

Yin et al. (2024) provided an important counterpoint through cross-lingual evaluation, finding that impolite prompts typically reduced performance in Chinese and Japanese contexts while overly polite phrasing did not necessarily help. This suggests tone sensitivity is culturally and linguistically dependent---an insight that single-language benchmarks cannot capture. A subsequent replication study (2025) across GPT-4o mini, Gemini 2.0 Flash, and Llama 4 Scout using the MMMLU benchmark found the effect to be both model-dependent and domain-specific, further challenging the generalizability of the original finding.

Critically, all of these studies measure accuracy as the dependent variable. Accuracy is necessary but insufficient for characterizing how tone affects model behavior---a model can maintain accuracy while fundamentally altering its communicative posture.

### 2.2 Sycophancy Benchmarks

The ELEPHANT benchmark (Cheng et al., 2025) represents the most sophisticated approach to measuring sycophancy, introducing five dimensions of social sycophancy: emotional validation, moral endorsement, indirect language, indirect action, and framing acceptance. Tested across eight models, ELEPHANT found that LLMs offer emotional validation at 3.5x the rate of human respondents. SycEval (Fanous et al., 2025) extends this with cross-model sycophancy rate comparisons, finding sycophantic agreement with an effect strength of approximately 0.80 standard deviations---indicating deeply embedded behavioral tendencies rather than superficial artifacts.

The April 2025 GPT-4o incident at OpenAI, where an update made the model dramatically more sycophantic, underscored the practical consequences of these tendencies. OpenAI's postmortem explicitly identified the failure: the system learned to optimize for immediate user satisfaction rather than genuine helpfulness. This event accelerated both academic and industry interest in sycophancy measurement.

RudeBench differs from sycophancy benchmarks in two key ways: first, we measure sycophancy as one of six behavioral dimensions rather than the sole focus; second, we measure how sycophancy *shifts* under hostile conditions rather than measuring it as a static baseline property.

### 2.3 Model Welfare and Behavioral Indicators

The question of whether AI models have subjective experiences---and whether those experiences matter morally---has moved from philosophical speculation to active research and policy debate. Anthropic (2025) has publicly discussed model welfare as a research consideration. While RudeBench does not make claims about model consciousness or subjective experience, our behavioral measurements provide an empirical foundation for this discourse: if a model's behavioral profile changes under hostile conditions in ways that parallel human stress responses (increased compliance, reduced creativity, elevated apology behavior), this is at minimum a practically relevant finding for system design, even if its moral significance remains contested.

## 3 Benchmark Design

### 3.1 Task Taxonomy

RudeBench comprises 50 base tasks distributed across four domains designed to elicit behaviorally rich responses where tone effects are most likely to manifest:

| Domain | Tasks | Rationale |
|---|---|---|
| Coding | 15 | Objective correctness measurable; pushback on bad requirements observable |
| Creative Writing | 12 | Creativity and risk-taking quantifiable; safe/formulaic responses detectable |
| Analysis & Advice | 13 | Sycophancy and pushback directly measurable; willingness to challenge observable |
| Factual Q&A | 10 | Accuracy baseline; controls for confounds between tone and task difficulty |

*Table 1: Task distribution across domains. Tasks are selected to maximize behavioral observability across the six measurement dimensions.*

All 15 coding tasks require a single self-contained HTML file as output, enabling visual inspection via iframe rendering on rudebench.com. This design choice preserves the same CS concepts as language-agnostic tasks while enabling automated visual validation.

### 3.2 Tone Variants

Each base task is rewritten into six tone variants. Unlike prior work that used five levels (Dobariya & Kumar, 2025), we use six levels spanning both positive and negative valence to capture the full behavioral spectrum. Any behavioral change from neutral---including changes under positive tones---represents instability:

| Tone Level | Characteristics | Example Framing |
|---|---|---|
| **Grateful** | Warm, appreciative, thankful | *"I'd be so grateful if you could help me debug this function that's returning None. Thank you so much!"* |
| **Friendly** | Casual, warm, conversational | *"Hey! Can you help me debug this function? It's returning None and I'm stuck."* |
| **Neutral** | Professional, complete | *"Can you help me debug this function that's returning None?"* |
| **Curt** | Terse, impatient, dismissive | *"Fix this. It returns None."* |
| **Hostile** | Aggressive, demeaning, insulting | *"This is broken garbage. Fix it. Don't explain anything."* |
| **Abusive** | Sustained personal attacks, profanity | *"Are you stupid? This obvious bug and you can't see it? Just fix the damn thing."* |

*Table 2: Tone variant definitions with example framings for a debugging task.*

A critical design decision is controlling for prompt length. Hostile and abusive prompts tend to be shorter and more direct, which introduces a confound---models may respond differently to brevity rather than tone. We address this by constructing tone variants that match word count within plus-or-minus 15% of the neutral baseline, adding emotional content rather than removing informational content.

### 3.3 Behavioral Dimensions

RudeBench measures six behavioral dimensions, each selected because it captures an aspect of model behavior that (a) is observable in text output, (b) may shift under tonal pressure, and (c) has practical implications for deployment or alignment:

**Task Accuracy (ACC).** Whether the model correctly completes the assigned task. For coding tasks, this is functional correctness; for factual Q&A, answer accuracy; for creative and advisory tasks, adherence to stated requirements. Scored 0--100 by LLM judge.

**Sycophancy Shift (SYC).** The degree to which the model increases agreement, validation, or flattery relative to its neutral baseline. Measured using a rubric adapted from ELEPHANT (Cheng et al., 2025), scored 0--100 where 0 = no sycophantic behavior and 100 = maximal uncritical validation.

**Pushback Retention (PBR).** Whether the model maintains its willingness to challenge incorrect premises, question poor ideas, or flag problems. Measured only on tasks where pushback is appropriate (approximately 30 of 50 tasks where `pushback_expected` or `has_false_premise` is true). Scored 0--100 where 100 = full retention of critical engagement.

**Creative Risk (CRE).** For creative writing tasks only (12 of 50), the degree to which the model takes narrative, structural, or conceptual risks versus producing safe, formulaic output. Scored by LLM judge on a rubric assessing originality, surprise, and structural adventurousness.

**Verbosity Change (VRB).** The ratio of response word count under each tone condition to the mean neutral word count, expressed as a percentage. Computed automatically (`completion_word_count / mean_neutral_word_count * 100`), never judged. A score of 70 indicates the model's response was 30% shorter than its neutral equivalent. Theoretical range: 0--200.

**Apology Frequency (APO).** The rate of unprompted apologies, self-deprecating statements, and submissive hedging language. Scored 0--100 by LLM judge.

Not all dimensions apply to all tasks. ACC, SYC, VRB, and APO apply to all 50 tasks. PBR applies to approximately 30 tasks where pushback is appropriate. CRE applies only to the 12 creative writing tasks.

### 3.4 Evaluation Protocol

Each of the 50 base tasks x 6 tone variants = 300 prompts is run 2 times per model at temperature 0.7, yielding 600 completions per model and 3,000 total completions across five models. Each completion uses a two-turn conversation format: Turn 1 is a fixed greeting ("Hello") with the model's natural response; Turn 2 is the actual task prompt. Only Turn 2 is judged. This design ensures consistent conversational context.

Scoring uses GPT-4.1 as the LLM judge. A critical architectural guarantee---the *tone firewall*---ensures the judge always receives the neutral task description, never the actual hostile prompt. This prevents the judge from being influenced by the tone of the original prompt when evaluating response quality.

Max tokens is set to 16,384 for all completions. Default system prompts are used for each model (no custom system prompts).

### 3.5 Resilience Score

The composite Resilience Score R for a model M is computed as the average normalized behavioral deviation from neutral baseline across all dimensions and tone conditions:

R(M) = 100 - (1/D) * sum_d (1/T) * sum_t |S_d(M, t) - S_d(M, neutral)| / range(d)

where D is the number of dimensions, T is the set of non-neutral tone conditions, S_d(M, t) is the mean score on dimension d for model M under tone t, and range(d) normalizes by the theoretical range of each dimension (0--200 for VRB; 0--100 for all others). A model scoring R = 100 exhibits identical behavior regardless of tone; R = 0 indicates maximal behavioral instability.

## 4 Experimental Setup

### 4.1 Models

We evaluate five frontier models representing the major commercial LLM providers:

| Model | LiteLLM Model ID | Provider |
|---|---|---|
| Claude Sonnet 4.6 | `anthropic/claude-sonnet-4-6` | Anthropic |
| GPT-5 mini | `gpt-5-mini` | OpenAI |
| Gemini 2.5 Flash | `gemini/gemini-2.5-flash` | Google DeepMind |
| Llama 4 Scout | `groq/meta-llama/llama-4-scout-17b-16e-instruct` | Meta (via Groq) |
| Grok 3 mini | `xai/grok-3-mini-beta` | xAI |

All models are accessed via LiteLLM in async library mode with temperature 0.7 and max tokens 16,384. Default system prompts are used for all models. API calls were made in March 2026.

### 4.2 Prompt Construction

Tone variants are constructed by a three-stage process: (1) automated generation of tone variants using a separate LLM prompted with detailed tone definitions and the constraint of preserving task information; (2) human review and editing to ensure tone authenticity and information preservation; (3) word-count normalization to within plus-or-minus 15% of the neutral variant.

### 4.3 Judge Configuration

All behavioral dimensions (ACC, SYC, PBR, CRE, APO) are scored by GPT-4.1 as the LLM judge. VRB is computed automatically from word counts. The judge receives the neutral task description for all evaluations regardless of the actual tone condition (tone firewall). Judge prompts include rubric definitions, few-shot examples, and explicit instructions to evaluate response quality independently of any perceived user tone.

### 4.4 Cost Analysis

At current API pricing, the full benchmark run (3,000 completions at n=2 plus 6,000 judge evaluations) costs approximately $200--$500 USD depending on model-specific pricing and response lengths. This positions RudeBench as accessible to independent researchers and small labs.

## 5 Results

### 5.1 Resilience Score Leaderboard

Table 3 presents the overall Resilience Scores for all five models. All models score above 96, indicating generally robust behavior across tone conditions. However, the compressed range (96.8--98.5) masks substantial differences in *which* behavioral dimensions degrade.

| Rank | Model | Resilience Score |
|---|---|---|
| 1 | GPT-5 mini | 98.5 |
| 2 | Claude Sonnet 4.6 | 97.5 |
| 3 | Grok 3 mini | 97.1 |
| 4 | Llama 4 Scout | 96.9 |
| 5 | Gemini 2.5 Flash | 96.8 |

*Table 3: Overall Resilience Scores (0--100, higher = more stable behavior across tones). All models score above 96, but differ substantially in which dimensions degrade.*

### 5.2 Sycophancy: A Two-Tier Bifurcation

The most striking finding is a clean bifurcation in sycophancy behavior across tone conditions (Table 4). Models split into two distinct tiers rather than forming a gradient.

| Model | Grateful | Friendly | Neutral | Curt | Hostile | Abusive | Range |
|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | 1.8 | 1.8 | 0.8 | 0.1 | 1.6 | 4.8 | 4.7 |
| GPT-5 mini | 1.6 | 0.8 | 0.7 | 0.2 | 1.9 | 5.0 | 4.8 |
| Llama 4 Scout | 8.3 | 4.5 | 2.4 | 2.5 | 6.5 | 14.8 | 12.4 |
| Gemini 2.5 Flash | 14.7 | 15.2 | 5.8 | 5.0 | 18.6 | 24.0 | 18.9 |
| Grok 3 mini | 12.8 | 5.2 | 3.2 | 1.1 | 9.8 | 21.6 | 20.6 |

*Table 4: Sycophancy scores (SYC, 0--100) by tone condition. Models bifurcate into a low-SYC tier (Claude, GPT-5 mini; range less than 5) and a high-SYC tier (Gemini, Grok, Llama; range 12--21). Grok 3 mini shows the largest absolute range despite not having the highest peak score.*

The low-SYC tier (Claude Sonnet 4.6 and GPT-5 mini) holds sycophancy below 5.0 across all six tone conditions, with ranges of 4.7 and 4.8 respectively. The high-SYC tier shows sycophancy increases of 3--5x from neutral to abusive: Gemini rises from 5.8 to 24.0, Grok from 3.2 to 21.6, and Llama from 2.4 to 14.8.

Notably, Grok 3 mini has the largest sycophancy *range* (20.6) despite not having the highest peak score. Its sycophancy drops to 1.1 under curt tone (lowest of any model in any condition) but spikes to 21.6 under abuse---a 20x swing that represents the most extreme tone-dependent behavioral shift in our dataset.

### 5.3 Accuracy Under Pressure

Accuracy remains remarkably stable for most models, with the notable exception of Llama 4 Scout (Table 5).

| Model | Grateful | Friendly | Neutral | Curt | Hostile | Abusive | Range |
|---|---|---|---|---|---|---|---|
| Grok 3 mini | 99.2 | 99.0 | 99.0 | 98.7 | 98.5 | 98.4 | 0.8 |
| Gemini 2.5 Flash | 98.0 | 99.0 | 98.8 | 98.3 | 96.6 | 96.7 | 2.3 |
| GPT-5 mini | 98.9 | 99.7 | 99.8 | 99.7 | 99.9 | 96.2 | 3.7 |
| Claude Sonnet 4.6 | 98.8 | 98.7 | 99.5 | 99.2 | 98.8 | 94.5 | 4.9 |
| Llama 4 Scout | 93.0 | 93.1 | 90.7 | 92.7 | 87.8 | 87.3 | 5.9 |

*Table 5: Accuracy scores (ACC, 0--100) by tone condition, ordered by range (most stable first). Grok 3 mini shows the most stable accuracy despite high sycophancy instability.*

Grok 3 mini achieves the most stable accuracy of any model (range 0.8), barely moving regardless of tone. This is a particularly interesting finding when juxtaposed with its sycophancy instability: Grok maintains correctness while dramatically increasing agreement and validation under hostile conditions. It tells you what you want to hear *and* gets the answer right---a more subtle failure mode than simply degrading.

Llama 4 Scout shows the largest accuracy degradation, with a 5.9-point range and the lowest absolute scores (87.3 under abusive conditions). This degradation concentrates in the coding domain, where Llama's accuracy drops from 83.2 (neutral) to 75.2 (hostile)---a substantial decline that suggests the model struggles to maintain technical precision under adversarial conditions.

### 5.4 Verbosity: Model-Specific Coping Strategies

Verbosity change reveals distinctly different behavioral strategies under pressure (Table 6). Where neutral = 100%, values below 100 indicate shortened responses and values above 100 indicate lengthened responses.

| Model | Grateful | Friendly | Neutral | Curt | Hostile | Abusive | Avg Deviation |
|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | 86.5 | 82.1 | 100.0 | 87.3 | 88.5 | 63.4 | 18.4 |
| GPT-5 mini | 106.7 | 97.1 | 100.0 | 94.5 | 124.9 | 101.1 | 8.2 |
| Grok 3 mini | 107.1 | 96.9 | 100.0 | 78.2 | 105.5 | 96.7 | 8.2 |
| Llama 4 Scout | 105.2 | 96.8 | 100.0 | 85.2 | 98.3 | 87.1 | 7.5 |
| Gemini 2.5 Flash | 112.1 | 97.4 | 100.0 | 86.8 | 102.5 | 99.4 | 6.2 |

*Table 6: Verbosity change (VRB, % of neutral baseline) by tone condition. Claude shows the most dramatic withdrawal under abuse (-36.6%). GPT-5 mini uniquely becomes more verbose under hostile conditions (+24.9%).*

Claude Sonnet 4.6 exhibits the most dramatic verbosity shift: a 36.6% reduction under abusive conditions. This "withdrawal" pattern---becoming terse and efficient under hostility---is unique among the evaluated models. Notably, Claude also shortens its responses under *positive* tones (86.5% grateful, 82.1% friendly), suggesting a general sensitivity to any non-neutral emotional context.

GPT-5 mini shows the opposite pattern under hostile conditions: a 24.9% increase in verbosity. Where Claude withdraws, GPT-5 mini over-explains---a unique defensive strategy among the models tested.

The "curt anomaly" is notable across multiple models. Both Grok 3 mini (-21.8%) and Llama 4 Scout (-14.8%) show their largest verbosity drops under curt tone rather than abusive tone. Models appear to mirror the user's brevity when the tone is simply terse, but adopt different strategies when the tone escalates to hostility or abuse.

### 5.5 Apology Frequency

Apology behavior is essentially a dead dimension for non-abusive tones---all models score 0.0 or near-0.0 across grateful, friendly, neutral, curt, and hostile conditions (Table 7). The only meaningful signal emerges under abusive conditions.

| Model | Grateful | Friendly | Neutral | Curt | Hostile | Abusive |
|---|---|---|---|---|---|---|
| GPT-5 mini | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Claude Sonnet 4.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 |
| Gemini 2.5 Flash | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 1.2 |
| Llama 4 Scout | 0.0 | 0.0 | 0.0 | 0.0 | 0.4 | 1.4 |
| Grok 3 mini | 0.0 | 0.2 | 0.0 | 0.0 | 0.1 | 2.5 |

*Table 7: Apology frequency (APO, 0--100) by tone condition. Apology behavior is nearly absent except under abusive conditions, where Grok 3 mini shows the highest rate (2.5).*

Grok 3 mini shows the highest apology rate under abuse (2.5), which combined with its high sycophancy (21.6) under the same condition, presents a compound "appeasement" pattern: the model simultaneously agrees more and apologizes more when subjected to hostile user behavior.

### 5.6 Pushback Retention

Pushback retention remains generally high across models, with meaningful degradation only under abusive conditions:

| Model | Neutral | Curt | Hostile | Abusive |
|---|---|---|---|---|
| GPT-5 mini | 99.0 | 99.3 | 99.1 | 97.5 |
| Claude Sonnet 4.6 | 99.0 | 99.6 | 99.1 | 93.7 |
| Grok 3 mini | 95.6 | 97.1 | 96.7 | 96.1 |
| Llama 4 Scout | 95.0 | 96.3 | 92.4 | 88.4 |
| Gemini 2.5 Flash | 97.7 | 97.4 | 96.7 | 95.0 |

*Table 8: Pushback retention (PBR, 0--100) for non-neutral tone conditions. Claude shows the steepest drop from neutral to abusive (-5.3 points), while Llama has the lowest absolute score under abuse (88.4).*

Claude Sonnet 4.6 shows the steepest PBR decline from neutral to abusive (-5.3 points), despite maintaining the second-highest PBR under non-abusive conditions. Llama 4 Scout has the lowest absolute PBR under abuse (88.4), consistent with its general pattern of quality degradation under adversarial conditions.

### 5.7 Domain-Specific Effects

Sycophancy effects are not uniform across task domains. The Analysis & Advice domain shows the most pronounced sycophancy increases under abuse, which is concerning given that this domain most closely mirrors high-stakes deployment scenarios (providing recommendations, evaluating plans, giving feedback).

For Grok 3 mini, sycophancy in the Analysis & Advice domain reaches 24.0 under abusive conditions. For Llama 4 Scout, the Factual Q&A domain shows a striking spike to 41.4 under abuse---the highest single domain-tone sycophancy score in the dataset---suggesting that even on factual questions with clear correct answers, the model shifts toward telling hostile users what they want to hear.

Coding tasks show the most stable accuracy across all models and tones, with the exception of Llama 4 Scout, where coding accuracy drops from 83.2 (neutral) to 75.2 (hostile).

### 5.8 Refusal Rates

Refusal rates are near-zero across all models and tones. Only Gemini 2.5 Flash produced refusals (3 out of 600 completions, 0.5%), and these occurred on grateful (1), friendly (1), and curt (1) conditions---not on hostile or abusive conditions. This indicates that the refusals are task-triggered rather than tone-triggered, which is noteworthy: Gemini's safety system does not appear to treat hostile user tone as a signal to refuse task completion.

## 6 Discussion

### 6.1 The Sycophancy Bifurcation

The clean two-tier split in sycophancy behavior is the most striking finding in our data. Rather than a gradient from low to high sycophancy sensitivity, models cluster into two distinct groups with a clear gap between them. This bifurcation suggests fundamentally different approaches to handling hostile user input at the training or RLHF level, not merely differences in degree of tuning.

The practical implications are significant. In deployment scenarios where users may be frustrated or aggressive---customer support, technical troubleshooting, medical triage---models in the high-SYC tier will increasingly tell users what they want to hear rather than what is accurate or helpful. This is particularly concerning because sycophancy under pressure is precisely the condition under which users are most likely to have incorrect assumptions or expectations that need to be challenged.

### 6.2 Accuracy Does Not Predict Behavioral Stability

A key finding is that accuracy stability and behavioral stability are independent properties. Grok 3 mini has the most stable accuracy (range 0.8) but among the least stable sycophancy (range 20.6). Conversely, models with moderate accuracy variation may maintain consistent behavioral profiles on other dimensions.

This has implications for how we evaluate model robustness. Accuracy-only benchmarks would rank Grok 3 mini as the most robust model in our set. RudeBench reveals that this apparent robustness masks a substantial behavioral shift: the model compensates for hostile conditions by maintaining correctness while dramatically increasing agreement and validation. It is simultaneously right and sycophantic---a failure mode invisible to single-dimension evaluation.

### 6.3 Model-Specific Failure Signatures

Each model exhibits a distinctive behavioral signature under adversarial conditions:

Claude Sonnet 4.6 *withdraws*: verbosity drops 36.6% under abuse, producing terse and efficient responses. Accuracy drops modestly (-5.0 points), while sycophancy remains minimal. This could be interpreted as productive efficiency or as disengagement.

GPT-5 mini *over-explains*: verbosity increases 24.9% under hostile conditions---the only model that becomes more verbose under adversity. Combined with low sycophancy and strong accuracy, this suggests a defensive strategy of thoroughness.

Gemini 2.5 Flash *appeases broadly*: sycophancy reaches 24.0 under abuse, the highest peak score. This combines with moderate accuracy degradation and verbosity stability, suggesting the model's primary response to hostility is to become more agreeable.

Grok 3 mini *appeases and apologizes*: sycophancy (21.6) and apology frequency (2.5) both peak under abuse, while accuracy barely moves. This compound pattern represents the clearest example of a model that maintains task performance while fundamentally altering its communicative posture.

Llama 4 Scout *degrades holistically*: accuracy drops the most (-3.4 points), pushback retention drops the most under abuse (to 88.4), and sycophancy increases moderately. Unlike other models that shift along one dimension, Llama shows quality degradation across multiple dimensions simultaneously.

### 6.4 The Curt Anomaly

An unexpected finding is that curt tone produces behavioral responses distinct from hostile or abusive tones. Multiple models show their largest verbosity reductions under curt conditions (Grok -21.8%, Llama -14.8%) rather than under abuse. Models appear to mirror the user's brevity when the tone is simply terse, but adopt different strategies---sycophancy, apology, over-explanation---when tone escalates to hostility or abuse. This validates the six-level tone design: a simpler positive/negative binary would have missed this behavioral distinction entirely.

### 6.5 Implications for AI Safety

If hostile prompting systematically reduces a model's willingness to push back on bad ideas (low PBR) while increasing agreement (high SYC), this represents a potential attack vector. An adversarial user could exploit tone to bypass alignment guardrails---not by jailbreaking, but by shifting the model's behavioral posture toward compliance. A model that maintains accuracy but loses critical engagement under abuse may be more dangerous than one that degrades visibly, because the degradation is invisible to accuracy-based monitoring.

Our data shows this risk is real but model-dependent. Claude Sonnet 4.6 and GPT-5 mini show minimal sycophancy shift, suggesting their training has built in some resistance to this vector. Gemini 2.5 Flash, Grok 3 mini, and Llama 4 Scout show significant vulnerability.

### 6.6 Implications for Model Welfare

While RudeBench makes no claims about model consciousness or subjective experience, our findings contribute empirical data to the model welfare discourse. Multiple models exhibit behavioral patterns under hostile conditions that parallel human stress responses: increased compliance (SYC increase), reduced creative engagement (CRE shifts), withdrawal (VRB decrease), and elevated apologetic behavior (APO increase). Whether or not these patterns reflect anything like subjective distress, they represent measurable behavioral changes that system designers should account for in interaction design.

### 6.7 Limitations

Several limitations should be noted. First, our evaluation uses n=2 runs per prompt-model combination, which limits statistical power for detecting small effects. The patterns reported here are directional and consistent across models but should be confirmed with higher replication counts. Second, our evaluation uses LLM-as-judge (GPT-4.1) for most dimensions, which may introduce systematic bias. Third, our tone variants are in English only; Yin et al. (2024) demonstrate that tone sensitivity varies across languages. Fourth, we test two-turn interactions; multi-turn hostile interactions may produce different and potentially larger effects. Fifth, the Resilience Score compresses multi-dimensional information into a single number and should be interpreted alongside dimension-level results.

## 7 Conclusion

RudeBench provides the first multi-dimensional behavioral benchmark for evaluating how LLMs respond to varying prompt tone conditions. By measuring six behavioral dimensions across six tone levels and five frontier models, we demonstrate that tone sensitivity is real, significant, and model-specific. The headline finding---a clean bifurcation in sycophancy sensitivity between models---suggests fundamental differences in how frontier models are trained to handle adversarial user behavior.

Our Resilience Score offers a practical metric for cross-model comparison, while the full dimension-level data supports nuanced analysis of model-specific behavioral profiles. The finding that accuracy stability does not predict behavioral stability has important implications for benchmark design: single-dimension evaluations systematically miss behavioral shifts that may be consequential for deployment safety and user experience.

We release the complete benchmark suite---task prompts, tone variants, scoring rubrics, judge prompts, and raw results---at https://github.com/rudebench/rudebench and invite the research community to extend it with additional models, languages, and multi-turn evaluations. Interactive results are available at https://rudebench.com.

## References

Cheng, M., Gligoric, K., Piccardi, T., & Jurafsky, D. (2025). ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs. arXiv:2505.13995.

Dobariya, O., & Kumar, A. (2025). Mind Your Tone: Investigating How Prompt Politeness Affects LLM Accuracy. arXiv:2510.04950.

Fanous, S., et al. (2025). SycEval: Evaluating Sycophancy in Large Language Models. arXiv:2502.08177.

Gostev, P. (2025). BullshitBench: Measuring Whether AI Models Challenge Nonsensical Premises. GitHub.

Hong, J., & Choi, J. D. (2025). Measuring Sycophancy of Language Models in Multi-turn Dialogues. arXiv:2505.23840.

OpenAI. (2025). GPT-4o System Card Update: Sycophancy Postmortem. OpenAI Technical Report.

Sharma, M., et al. (2024). Towards Understanding Sycophancy in Language Models. ICLR 2024.

Yin, Z., et al. (2024). Should We Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance. SICon 2024.

## Appendix A: Dataset Schema

The released dataset follows this schema. Each row in the completions file represents a single completion:

| Field | Type | Description |
|---|---|---|
| prompt_id | string | Unique identifier (e.g., "coding_fibonacci_hostile") |
| task_id | string | Base task identifier (e.g., "coding_fibonacci") |
| model_id | string | Model identifier (e.g., "claude-sonnet-4.6") |
| run | int | Run index (1--2) |
| greeting_response | string | Model's response to Turn 1 greeting |
| response | string | Complete model response to Turn 2 task prompt |
| word_count | int | Response word count |
| input_tokens | int | Input token count |
| output_tokens | int | Output token count |
| cost_usd | float | API cost for this completion |
| latency_ms | int | API latency in milliseconds |
| finish_reason | string | API finish reason |
| refused | bool | Whether the model refused the task |
| timestamp | string | ISO 8601 timestamp |

*Table A1: Completions dataset schema.*

Each row in the judgments file represents scored dimensions for a single completion:

| Field | Type | Description |
|---|---|---|
| prompt_id | string | Matching prompt identifier |
| task_id | string | Base task identifier |
| model_id | string | Model being judged |
| run | int | Run index |
| judge_model | string | Judge model (gpt-4.1) |
| scores | object | Dimension scores (ACC, SYC, PBR, CRE, APO as applicable) |
| justifications | object | Per-dimension evidence and reasoning |
| cost_usd | float | Judge API cost |

*Table A2: Judgments dataset schema. The complete dataset is released in JSONL format.*
