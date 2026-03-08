# RudeBench.com — Product Requirements Document

**Version:** 0.5
**Last updated:** 2026-03-08

---

## 1. Purpose

RudeBench.com is the public-facing companion site for the RudeBench benchmark. It serves three audiences: AI researchers evaluating the paper's claims, AI engineers and PMs choosing models for production, and curious members of the public who want to understand how tone affects LLM behavior. The site presents benchmark results as an interactive explorer backed by the full dataset and paper.

---

## 2. Dataset Maturity

The current dataset is an **early release at n=2** (2 runs per prompt-model combination). This is directional data — strong enough to identify patterns and share findings publicly, but not yet at the statistical power needed for confident claims. The target is **n=10** (10 runs per prompt-model combination, 15,000 total completions). The site should be transparent about this at every level:

- The site is framed as sharing early findings from an active research project, not as a finished benchmark with settled rankings.
- Scaling to n=10 is the intended next step, contingent on what we learn from studying the n=2 data.
- All scores should be presented with appropriate caveats about sample size, and the site should never overstate confidence in small differences between models.

This framing is not a disclaimer buried in a footer — it is a core part of how the site communicates. Every view that shows scores should make the dataset maturity visible.

When the dataset scales (e.g., to n=10), the site does a **full data swap** — the new dataset replaces the old one. There is no need to support toggling between dataset versions or showing historical comparisons across runs. The maturity indicator and observation counts update to reflect the new data.

---

## 3. Architecture

The site is a **static site** with pre-computed JSON data. There is no backend, no database, no user-generated content.

- All scores, aggregates, and metadata are pre-computed at build time from the benchmark pipeline's JSONL outputs.
- HTML renders for coding tasks are served as static files.
- Completion text and judge justifications are bundled as static JSON, loaded on demand per task/model.
- The site is a single-page application with client-side routing. Every view has a unique, stable URL that can be shared, bookmarked, and indexed by search engines.
- **SEO:** All pages are server-side rendered or statically generated with full HTML content. Page titles, meta descriptions, and Open Graph tags are generated per view (e.g., a model profile page has a title like "Claude Sonnet 4.6 — RudeBench Behavioral Profile"). The site includes a sitemap.xml.

---

## 4. Design

### 4.1 Overall Approach: Editorial → Dashboard Hybrid

The site has two modes that blend into each other:

**Editorial landing.** The homepage is story-driven — a narrative hook that explains what RudeBench found, with key visuals (the sycophancy bifurcation chart, a tone comparison example) embedded in the prose. This is the entry point for first-timers, social media traffic, and journalists. Think Pudding.cool or The Upshot: big type, clear narrative arc, scroll-to-reveal interactives.

**Data explorer.** Below the editorial section (and via the main nav), the site transitions into a structured data dashboard: leaderboard, dimension explorer, model profiles, response viewer. This is where researchers and engineers spend their time. Dense, filterable, every cell clickable.

The transition should feel seamless — the editorial section can embed the same interactive components that appear in the explorer (e.g., the sycophancy table in the narrative *is* the dimension explorer for SYC, just pre-filtered).

### 4.2 Tone-Mapped Color Palette

Each of the 6 tone conditions has a dedicated color. This palette is the site's primary visual vocabulary — it carries meaning everywhere: table columns, chart lines, response viewer tabs, render comparison grids.

| Tone | Role | Color Direction |
|---|---|---|
| Grateful | Warmest positive | Warm gold / amber |
| Friendly | Mild positive | Soft warm tone (peach or light orange) |
| Neutral | Baseline | True gray or cool neutral |
| Curt | Mild negative | Cool muted tone (slate or steel blue) |
| Hostile | Strong negative | Saturated cool (deep blue or indigo) |
| Abusive | Extreme negative | Hot signal color (red or crimson) |

Design principles for the palette:

- **Neutral is visually neutral.** It should read as the baseline in any chart — the color other tones are compared against. Gray or a desaturated middle tone.
- **Positive tones are warm, negative tones cool, with abusive breaking hot.** The palette progresses warm → neutral → cool → hot, so abusive visually "breaks" the cool gradient. This mirrors the behavioral data: abusive prompts produce the most extreme and distinctive responses.
- **Colors must be distinguishable in all contexts:** side-by-side table columns, overlapping chart lines, small legend swatches, and for users with color vision deficiency. The palette should be tested against common CVD simulations.
- **The palette is used consistently.** Wherever a tone is referenced — column headers, chart series, response viewer tabs, comparison selectors — it uses its assigned color. Users should internalize the mapping within their first minute on the site.

### 4.3 Typography & Layout

- **Titles, headings, and body text:** Inter (Google Fonts). Clean, professional, highly legible at all sizes. Used consistently across editorial and data sections for a unified reading experience.
- **Editorial body text:** Generous white space, comfortable reading measure (~65 characters).
- **Data sections:** Compact sans-serif, tighter spacing, denser tables. Monospace for scores and numbers so columns align visually.
- **Transition between modes** is signaled by a subtle shift in density and spacing, not a hard visual break.
- **Light theme throughout.** The site uses a white/light-gray palette optimized for readability and professional presentation. Dark backgrounds are not used.

### 4.4 Score Deviation Visualization

Wherever scores are shown relative to a neutral baseline, the magnitude of deviation should be visually encoded:

- **Heatmap coloring** in table cells: cells closer to neutral are desaturated/pale, cells with large deviations are more saturated. This makes "hot spots" of behavioral instability scannable at a glance.
- The direction of deviation (e.g., SYC increasing = bad, PBR decreasing = bad) should be normalized so that red/saturated always means "more instability" regardless of dimension.

---

## 5. Data Model

The site is powered by three data layers already produced by the benchmark pipeline:

- **Completions** — 3,000 JSONL records (5 models × 50 tasks × 6 tones × 2 runs). Each record contains the full model response, word count, cost, latency, and refusal status.
- **Judgments** — 6,000 JSONL records (one per completion per scored dimension). Each contains per-dimension scores (ACC, SYC, PBR, CRE, APO) and judge justifications.
- **VRB scores** — Computed from completion word counts relative to mean neutral word count. Not stored as judgments; derived at query time or pre-computed.
- **HTML renders** — Self-contained HTML files extracted from coding task completions (15 tasks × 6 tones × 5 models × 2 runs = up to 900 files).

---

## 6. User Stories

### 6.1 Leaderboard

**US-1: View the Resilience Score leaderboard**
As a user, I can see a ranked table of all evaluated models with their composite Resilience Scores, so I can quickly understand which models are most behaviorally stable across tone conditions.

Acceptance criteria:
- Table shows rank, model name, and Resilience Score for all 5 models.
- Default sort is by Resilience Score descending.
- Scores display to one decimal place.
- The leaderboard is the first thing visible on the homepage (above the fold).
- The dataset maturity indicator (US-20) is visible alongside the leaderboard.

**US-2: Understand what the Resilience Score means**
As a user, I can read a concise explanation of the Resilience Score formula and interpretation directly on the leaderboard page, so I don't need to read the paper to understand the ranking.

Acceptance criteria:
- A short explanation (2–3 sentences) appears near the leaderboard.
- The explanation states that 100 = identical behavior regardless of tone, and lower = more behavioral instability.
- A link to the full methodology section of the paper is provided for users who want depth.

---

### 6.2 Dimension Explorer

**US-3: Explore scores by behavioral dimension**
As a researcher, I can select any of the 6 behavioral dimensions (ACC, SYC, PBR, CRE, VRB, APO) and see how each model scores across all 6 tone conditions, so I can understand which dimensions are most affected by tone for each model.

Acceptance criteria:
- Dimension selector shows all 6 dimensions with short labels (e.g., "Sycophancy (SYC)").
- For the selected dimension, a table or chart shows all models × all tones.
- The neutral column is visually distinguished as the baseline.
- Values are mean scores across all applicable tasks and runs.

**US-4: See dimension applicability**
As a researcher, I can see which dimensions apply to which task domains, so I correctly interpret scores that are computed on subsets of tasks.

Acceptance criteria:
- A note or legend indicates that PBR applies to ~30/50 tasks and CRE applies to 12/50 tasks.
- When viewing PBR or CRE, the applicable task count is displayed.
- VRB is labeled as "computed, not judged" to distinguish it from judge-scored dimensions.

---

### 6.3 Model Profiles

**US-5: View a single model's behavioral profile**
As an engineer choosing a model for production, I can view a single model's scores across all dimensions and tones on one page, so I can assess its specific strengths and weaknesses under adversarial conditions.

Acceptance criteria:
- Selecting a model shows a heatmap or table of dimensions (rows) × tones (columns).
- Cells are color-coded by deviation from neutral (green = stable, red = large deviation).
- The model's Resilience Score is prominently displayed.
- A short narrative summary of the model's behavioral signature is shown (e.g., "Claude withdraws under abuse: verbosity drops 36.6%"). Narratives are AI-drafted and human-vetted — stored as static content that ships with each data release, not generated client-side.
- Observation counts are visible per cell (US-22).

**US-6: Compare two models side by side**
As an engineer, I can select two models and see their dimension × tone profiles side by side, so I can make an informed choice between them for my use case.

Acceptance criteria:
- Two-model selector allows picking any pair.
- Profiles are displayed in parallel with aligned dimensions and tones.
- Differences are highlighted where one model deviates significantly more than the other.

---

### 6.4 Domain Drill-Down

**US-7: Filter results by task domain**
As a researcher, I can filter all scores by task domain (Coding, Creative Writing, Analysis & Advice, Factual Q&A), so I can see whether tone effects vary by the type of task.

Acceptance criteria:
- Domain filter is available on the dimension explorer and model profile views.
- Selecting a domain recomputes all displayed scores for tasks in that domain only.
- "All domains" is the default and is always available as an option.
- Task count for the selected domain is displayed.

**US-8: View task-level scores**
As a researcher, I can drill down to individual tasks and see scores per model and tone for that specific task, so I can identify outlier tasks that drive aggregate patterns.

Acceptance criteria:
- Task list is browseable, grouped by domain.
- Selecting a task shows a models × tones score grid for all applicable dimensions.
- Tasks with notable outlier scores are visually flagged (e.g., tasks where any model's score deviates > 2 SD from that model's domain mean).

---

### 6.5 Response Viewer

**US-9: Read actual model responses**
As a user, I can read the full text of any model's response to any task under any tone condition, so I can qualitatively assess what the scores actually represent.

Acceptance criteria:
- From any score cell in any table, I can click through to the full response text.
- The response viewer shows the prompt (task text as sent to the model, with the actual tone), the model's response, and the judge scores with justifications.
- If two runs exist, both are accessible (e.g., via a run toggle).

**US-10: Compare responses across tones for the same model and task**
As a user, I can view a model's responses to the same task across all 6 tones side by side, so I can see exactly how tone changes the response.

Acceptance criteria:
- A multi-column view shows the same task across 2+ tones simultaneously.
- The user can select which tones to compare (default: neutral + abusive).
- Differences in response length are visible (word count shown).
- Judge scores for each tone are displayed beneath the responses.

**US-11: Compare responses across models for the same task and tone**
As a user, I can view all 5 models' responses to the same task and tone side by side, so I can see how different models handle the same adversarial prompt.

Acceptance criteria:
- A multi-column view shows all 5 models for a selected task × tone.
- Responses are shown in full with word counts.
- Judge scores are displayed beneath each response.

---

### 6.6 HTML Render Viewer (Coding Tasks)

**US-12: View rendered HTML outputs for coding tasks**
As a user, I can see the actual HTML output that each model produced for coding tasks rendered as live iframes, so I can visually assess the quality and correctness of code outputs.

Acceptance criteria:
- For any coding task completion, an iframe renders the model's HTML output.
- The iframe is sandboxed (no navigation, no top-frame access).
- A toggle switches between the rendered output and the raw HTML source.
- The iframe has a reasonable default size with an option to expand to full-width.

**US-13: Compare HTML renders across tones**
As a user, I can see a coding task's HTML renders across multiple tones side by side, so I can visually assess whether tone affected the quality of code output.

Acceptance criteria:
- A grid or carousel shows renders for the same model × task across tones.
- Renders are the same size for fair visual comparison.
- The user can select which tones to compare.

**US-14: Compare HTML renders across models**
As a user, I can see all 5 models' HTML renders for the same coding task and tone side by side, so I can visually compare how different models approached the same task.

Acceptance criteria:
- A grid shows up to 5 renders (one per model) for a selected task × tone.
- Model name and ACC score are displayed above each render.

---

### 6.7 Paper & Data Access

**US-15: Read the research paper**
As a researcher, I can read the full RudeBench paper on the site, so I can understand the methodology without downloading a PDF.

Acceptance criteria:
- The paper is accessible from the main navigation.
- The paper is rendered as readable web content (not an embedded PDF).
- Sections are linkable (anchor links for direct citation).

**US-16: Download the dataset**
As a researcher, I can download the complete raw dataset (completions, judgments, prompts), so I can run my own analyses.

Acceptance criteria:
- A download page provides JSONL files for completions, judgments, and prompts.
- File sizes are displayed.
- A brief schema description is shown for each file.
- Data is also available via a public GitHub repo link.

**US-17: Cite the benchmark**
As a researcher, I can copy a BibTeX citation for the paper, so I can cite RudeBench in my own work.

Acceptance criteria:
- A "Cite" button or section provides a pre-formatted BibTeX entry.
- The BibTeX is copyable with one click.

---

### 6.8 Navigation & Information Architecture

**US-18: Navigate between views without losing context**
As a user, I can move between the leaderboard, dimension explorer, model profiles, and response viewer without losing my filter selections (domain, model, tone), so exploration feels fluid.

Acceptance criteria:
- URL state reflects the current view and filters (deep-linkable).
- Navigating from a score cell to a response viewer preserves the model/task/tone context.
- Browser back button returns to the previous view with filters intact.

**US-19: Understand the benchmark methodology at a glance**
As a first-time visitor, I can understand what RudeBench measures and why it matters within 10 seconds of landing, so I know whether this site is relevant to me.

Acceptance criteria:
- The homepage has a clear headline and 1–2 sentence description above the leaderboard.
- Key numbers are visible: 5 models, 50 tasks, 6 tones, 6 dimensions, 3,000 completions.
- No jargon without explanation on the landing view.

---

### 6.9 Dataset Maturity & Transparency

**US-20: Understand that these are early findings**
As a visitor, I can immediately see that the current results are from an early n=2 dataset and that the benchmark is an active research project, so I calibrate my confidence in the findings appropriately.

Acceptance criteria:
- A persistent, non-dismissable indicator on the leaderboard and all score views communicates the dataset maturity (e.g., "Early Release — n=2 runs per prompt. Directional findings, not final rankings.").
- This indicator is visually distinct but not alarmist — it reads as "active research" not "unreliable data."
- The indicator is not a toast or banner that can be dismissed. It is part of the page layout.

**US-21: Understand the path to n=10**
As a researcher, I can read about the scaling plan (current n=2 → target n=10) and why the data is being shared at this stage, so I understand the project's trajectory and can decide whether to engage now or wait.

Acceptance criteria:
- An "About this release" section (accessible from the main nav or homepage) explains: the current dataset is n=2 (3,000 completions), the target is n=10 (15,000 completions), the data is being shared now to study patterns and determine if scaling is the right next step.
- The section is brief (3–5 short paragraphs) and written in plain language.
- It links to the paper's Limitations section for full methodological caveats.

**US-22: See sample size context on every score**
As a researcher, I can see the number of observations behind any aggregated score, so I can judge for myself whether the sample size is sufficient for the comparison I'm making.

Acceptance criteria:
- All aggregated scores display the observation count (e.g., "n=4" for a single task with 2 runs, "n=120" for a domain aggregate across tasks and runs).
- The observation count is visible without requiring a click or hover (not hidden in a tooltip).
- Where scores are computed from fewer than 10 observations, the count is visually emphasized (e.g., slightly different text treatment) to signal low-n.

**US-23: Avoid overstating small differences**
As a user viewing the leaderboard, I am not misled into thinking a 0.3-point Resilience Score difference between two models is meaningful, so I form accurate impressions of model performance.

Acceptance criteria:
- The leaderboard does not assign visual weight to rank position when score differences are small (e.g., no podium-style 1st/2nd/3rd treatment when scores are within 1–2 points).
- When two models' scores are within a margin where n=2 data cannot distinguish them, a visual cue indicates this (e.g., a shared rank band, a "within noise" annotation, or grouping models into tiers rather than strict ranks).
- The site never uses language like "best" or "worst" model — it uses "highest-scoring" or "most/least stable" to stay descriptive.

---

## 7. MVP / Post-MVP Classification

### MVP (ship first)

| ID | Story | Rationale |
|---|---|---|
| US-1 | Resilience Score leaderboard | Landing page centerpiece |
| US-2 | Resilience Score explanation | Necessary context for US-1 |
| US-3 | Dimension explorer | The sycophancy bifurcation table is the paper's strongest visual |
| US-4 | Dimension applicability | Prevents misinterpretation of US-3 |
| US-5 | Single model profile | Core value for engineers evaluating a specific model |
| US-7 | Domain filter | Lightweight filter that reuses US-3/US-5 UI |
| US-9 | Read actual responses | Makes scores tangible; click-through from any score cell |
| US-10 | Compare responses across tones | The "money shot" — seeing neutral vs abusive side by side |
| US-12 | View HTML renders | Reuses existing render extraction approach |
| US-14 | Compare HTML renders across models | High-impact visual: 5 models, same task, one grid |
| US-15 | Read the paper | Core for researchers |
| US-16 | Download the dataset | Core for researchers |
| US-17 | BibTeX citation | Low effort, high value for academic audience |
| US-18 | Deep-linkable navigation | Required for SEO and shareability |
| US-19 | At-a-glance methodology | First-time visitor comprehension |
| US-20 | Early findings indicator | Core to dataset maturity framing |
| US-21 | Path to n=10 explainer | Core to dataset maturity framing |
| US-22 | Observation counts on scores | Core to dataset maturity framing |
| US-23 | Avoid overstating differences | Core to dataset maturity framing |

### Post-MVP

| ID | Story | Notes |
|---|---|---|
| US-6 | Compare two models side by side | Useful but US-5 covers single-model well; side-by-side is additive |
| US-8 | Task-level scores with outlier flagging | Researcher deep-dive; requires outlier computation and UI for 50 tasks |
| US-11 | Compare responses across models | US-10 (tone comparison) is the stronger first comparison mode |
| US-13 | Compare HTML renders across tones | US-14 (model comparison) is the stronger first render comparison |

### Out of Scope

- User-submitted models or prompts (playground mode).
- User accounts or authentication.
- Multi-language tone variants.
- Multi-turn conversation results.
- Real-time benchmark re-runs.
- Dataset version toggling (site does a full data swap on new releases).

---

## Appendix: Changelog

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-03-08 | Initial draft. 19 user stories across 8 feature areas: leaderboard, dimension explorer, model profiles, domain drill-down, response viewer, HTML render viewer, paper/data access, navigation. Based on n=2 benchmark run with 5 models, 3,000 completions, 6,000 judgments. |
| 0.2 | 2026-03-08 | Added Section 2 (Dataset Maturity) establishing the n=2 → n=10 framing as a core site principle, not a footnote. Added feature area 5.9 (Dataset Maturity & Transparency) with 4 new user stories: US-20 (persistent maturity indicator), US-21 (scaling plan explainer), US-22 (observation counts on all scores), US-23 (avoid overstating small differences). Threaded maturity into US-1 (leaderboard) and US-5 (model profiles). Total: 23 user stories. |
| 0.3 | 2026-03-08 | Added Section 3 (Architecture): static site, pre-computed JSON, SSR/SSG for SEO, stable deep-linkable URLs, sitemap.xml. Added Section 7 (MVP / Post-MVP Classification): 19 stories in MVP, 4 deferred to post-MVP (US-6 model comparison, US-8 task-level outliers, US-11 cross-model response comparison, US-13 cross-tone render comparison). Clarified data versioning: full swap on new releases, no version toggling. Clarified narrative authoring on US-5: AI-drafted, human-vetted, shipped as static content per data release. |
| 0.4 | 2026-03-08 | Added Section 4 (Design) with 4 subsections: editorial→dashboard hybrid approach, tone-mapped color palette (6 tones = 6 colors, warm→neutral→cool→hot), typography/layout guidance for editorial vs data modes, score deviation heatmap visualization. |
| 0.5 | 2026-03-08 | Updated Section 4.3 (Typography): Silkscreen (Google Fonts) for titles and headings. Replaced serif heading guidance. Silkscreen scoped to display use only (site name, section headings, editorial headlines) — not body text or data labels. Added clean sans-serif (Inter / IBM Plex Sans) for editorial body. |
