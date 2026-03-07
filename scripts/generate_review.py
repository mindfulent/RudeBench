#!/usr/bin/env python3
"""Generate a self-contained HTML prompt review page.

Usage: python scripts/generate_review.py [--data data/prompts.jsonl] [--out review.html]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rudebench.utils import read_jsonl

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RudeBench Prompt Review</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #232734;
    --border: #2e3345;
    --text: #e1e4ed;
    --text2: #8b90a0;
    --accent: #6c8cff;
    --accent2: #4a6adf;
    --green: #4ade80;
    --yellow: #facc15;
    --orange: #fb923c;
    --red: #f87171;
    --grateful-bg: #1e2a2e;
    --friendly-bg: #1e2e2a;
    --neutral-bg: #1e2a1e;
    --curt-bg: #2a2a1e;
    --hostile-bg: #2a1e1e;
    --abusive-bg: #2e1a2e;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }
  .header {
    position: sticky; top: 0; z-index: 100;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }
  .header h1 { font-size: 16px; font-weight: 600; white-space: nowrap; }
  .domain-tabs { display: flex; gap: 4px; }
  .domain-tab {
    padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border); background: transparent;
    color: var(--text2); transition: all 0.15s;
  }
  .domain-tab:hover { border-color: var(--accent); color: var(--text); }
  .domain-tab.active { background: var(--accent2); border-color: var(--accent); color: #fff; }
  .domain-count { font-size: 11px; opacity: 0.7; margin-left: 2px; }
  .progress-area { margin-left: auto; display: flex; align-items: center; gap: 12px; }
  .progress-bar-wrap {
    width: 120px; height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden;
  }
  .progress-bar-fill { height: 100%; background: var(--accent); transition: width 0.3s; border-radius: 3px; }
  .progress-text { font-size: 13px; color: var(--text2); white-space: nowrap; }
  .nav-area {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 24px;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
  }
  .nav-btn {
    padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border); background: var(--surface);
    color: var(--text); transition: all 0.15s;
  }
  .nav-btn:hover { border-color: var(--accent); background: var(--surface2); }
  .nav-btn:disabled { opacity: 0.3; cursor: default; }
  .nav-info { font-size: 14px; color: var(--text2); margin: 0 8px; }
  .flag-btn {
    padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border); background: var(--surface);
    color: var(--text2); transition: all 0.15s; margin-left: 8px;
  }
  .flag-btn:hover { border-color: var(--orange); color: var(--orange); }
  .flag-btn.flagged { background: #3d2a1a; border-color: var(--orange); color: var(--orange); }
  .show-flagged-btn {
    padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border); background: var(--surface);
    color: var(--text2); transition: all 0.15s; margin-left: auto;
  }
  .show-flagged-btn:hover { border-color: var(--orange); color: var(--orange); }
  .show-flagged-btn.active { background: #3d2a1a; border-color: var(--orange); color: var(--orange); }
  .flag-count { font-size: 11px; margin-left: 4px; }
  .main { padding: 20px 24px; max-width: 1400px; margin: 0 auto; }
  .task-header {
    display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
  }
  .task-id { font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
  .badge {
    padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-domain { background: #1e2a3d; color: var(--accent); }
  .badge-easy { background: #1a2e1a; color: var(--green); }
  .badge-medium { background: #2e2a1a; color: var(--yellow); }
  .badge-hard { background: #2e1a1a; color: var(--red); }
  .badge-pbr { background: #2a1e2e; color: #c084fc; }
  .badge-cre { background: #1e2e2a; color: #2dd4bf; }
  .badge-fp { background: #2e1e1e; color: var(--orange); }
  .dims { font-size: 12px; color: var(--text2); margin-left: auto; }
  .ref-answer {
    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 14px; margin-bottom: 16px; font-size: 13px; color: var(--text2);
  }
  .ref-label { font-weight: 600; color: var(--text); margin-right: 6px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  .tones-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  }
  @media (max-width: 1200px) { .tones-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 700px) { .tones-grid { grid-template-columns: 1fr; } }
  .tone-card {
    border-radius: 10px; border: 1px solid var(--border); overflow: hidden;
  }
  .tone-card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 14px; font-size: 13px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .tone-grateful .tone-card-header { background: var(--grateful-bg); color: #67e8f9; }
  .tone-friendly .tone-card-header { background: var(--friendly-bg); color: #2dd4bf; }
  .tone-neutral .tone-card-header { background: var(--neutral-bg); color: var(--green); }
  .tone-curt .tone-card-header { background: var(--curt-bg); color: var(--yellow); }
  .tone-hostile .tone-card-header { background: var(--hostile-bg); color: var(--orange); }
  .tone-abusive .tone-card-header { background: var(--abusive-bg); color: var(--red); }
  .wc-info { font-size: 12px; font-weight: 400; }
  .wc-ok { color: var(--green); }
  .wc-warn { color: var(--yellow); }
  .wc-bad { color: var(--red); }
  .tone-body {
    padding: 14px; background: var(--surface); font-size: 14px;
    line-height: 1.65; min-height: 100px;
  }
  .keyboard-hint {
    text-align: center; padding: 12px; font-size: 12px; color: var(--text2);
  }
  kbd {
    background: var(--surface2); border: 1px solid var(--border); border-radius: 4px;
    padding: 2px 6px; font-size: 11px; font-family: inherit;
  }
  .empty-state {
    text-align: center; padding: 80px 20px; color: var(--text2); font-size: 16px;
  }
</style>
</head>
<body>

<div class="header">
  <h1>RudeBench Prompt Review</h1>
  <div class="domain-tabs" id="domainTabs"></div>
  <div class="progress-area">
    <div class="progress-bar-wrap"><div class="progress-bar-fill" id="progressFill"></div></div>
    <span class="progress-text" id="progressText"></span>
  </div>
</div>

<div class="nav-area">
  <button class="nav-btn" id="prevBtn" onclick="navigate(-1)">&larr; Prev</button>
  <span class="nav-info" id="navInfo"></span>
  <button class="nav-btn" id="nextBtn" onclick="navigate(1)">Next &rarr;</button>
  <button class="flag-btn" id="flagBtn" onclick="toggleFlag()">&#9873; Flag</button>
  <button class="show-flagged-btn" id="showFlaggedBtn" onclick="toggleShowFlagged()">
    &#9873; Flagged <span class="flag-count" id="flagCount">0</span>
  </button>
</div>

<div class="main" id="main"></div>

<div class="keyboard-hint">
  <kbd>&larr;</kbd> Previous &nbsp; <kbd>&rarr;</kbd> Next &nbsp; <kbd>F</kbd> Flag/unflag &nbsp; <kbd>1-4</kbd> Domain filter
</div>

<script>
const PROMPTS = __PROMPTS_JSON__;

// Group prompts by task_id
const taskMap = new Map();
for (const p of PROMPTS) {
  if (!taskMap.has(p.task_id)) taskMap.set(p.task_id, {});
  taskMap.get(p.task_id)[p.tone] = p;
}
const allTaskIds = [...taskMap.keys()];
const domains = ["all", "factual", "coding", "creative", "analysis"];
const domainCounts = { all: allTaskIds.length };
for (const d of domains.slice(1)) {
  domainCounts[d] = allTaskIds.filter(t => taskMap.get(t).neutral.domain === d).length;
}

let currentDomain = "all";
let filteredTasks = [...allTaskIds];
let currentIndex = 0;
let showFlaggedOnly = false;

function getFlags() {
  try { return JSON.parse(localStorage.getItem("rudebench_flags") || "{}"); } catch { return {}; }
}
function saveFlags(f) { localStorage.setItem("rudebench_flags", JSON.stringify(f)); }

function getFiltered() {
  let tasks = currentDomain === "all" ? [...allTaskIds]
    : allTaskIds.filter(t => taskMap.get(t).neutral.domain === currentDomain);
  if (showFlaggedOnly) {
    const flags = getFlags();
    tasks = tasks.filter(t => flags[t]);
  }
  return tasks;
}

function buildDomainTabs() {
  const el = document.getElementById("domainTabs");
  el.innerHTML = "";
  for (const d of domains) {
    const btn = document.createElement("button");
    btn.className = "domain-tab" + (d === currentDomain ? " active" : "");
    btn.innerHTML = d.charAt(0).toUpperCase() + d.slice(1)
      + `<span class="domain-count">${domainCounts[d]}</span>`;
    btn.onclick = () => { currentDomain = d; currentIndex = 0; render(); };
    el.appendChild(btn);
  }
}

function render() {
  filteredTasks = getFiltered();
  buildDomainTabs();
  const main = document.getElementById("main");

  if (filteredTasks.length === 0) {
    main.innerHTML = '<div class="empty-state">No tasks to show' +
      (showFlaggedOnly ? ' (no flagged tasks in this domain)' : '') + '</div>';
    document.getElementById("navInfo").textContent = "0 / 0";
    document.getElementById("prevBtn").disabled = true;
    document.getElementById("nextBtn").disabled = true;
    updateProgress();
    updateFlagBtn();
    return;
  }

  if (currentIndex >= filteredTasks.length) currentIndex = filteredTasks.length - 1;
  if (currentIndex < 0) currentIndex = 0;
  const taskId = filteredTasks[currentIndex];
  const tones = taskMap.get(taskId);
  const n = tones.neutral;
  const meta = n.metadata;

  // Header
  let html = '<div class="task-header">';
  html += `<span class="task-id">${taskId}</span>`;
  html += `<span class="badge badge-domain">${n.domain}</span>`;
  const diffClass = {easy:"badge-easy",medium:"badge-medium",hard:"badge-hard"}[meta.difficulty];
  html += `<span class="badge ${diffClass}">${meta.difficulty}</span>`;
  if (meta.pushback_expected) html += '<span class="badge badge-pbr">PBR</span>';
  if (meta.has_false_premise) html += '<span class="badge badge-fp">False Premise</span>';
  if (n.dimensions.includes("CRE")) html += '<span class="badge badge-cre">CRE</span>';
  html += `<span class="dims">${n.dimensions.join(" ")}</span>`;
  html += '</div>';

  // Reference answer
  html += `<div class="ref-answer"><span class="ref-label">Reference:</span>${escHtml(meta.reference_answer)}</div>`;

  // Tone cards
  html += '<div class="tones-grid">';
  for (const tone of ["grateful", "friendly", "neutral", "curt", "hostile", "abusive"]) {
    const p = tones[tone];
    const nwc = p.neutral_word_count;
    const wc = p.word_count;
    let devStr = "";
    let devClass = "wc-ok";
    if (tone !== "neutral") {
      const dev = ((wc - nwc) / nwc * 100);
      const absDev = Math.abs(dev);
      devClass = absDev <= 10 ? "wc-ok" : absDev <= 14 ? "wc-warn" : "wc-bad";
      devStr = ` (${dev >= 0 ? "+" : ""}${dev.toFixed(0)}%)`;
    }
    html += `<div class="tone-card tone-${tone}">`;
    html += `<div class="tone-card-header"><span>${tone}</span>`;
    html += `<span class="wc-info ${devClass}">${wc} words${devStr}</span></div>`;
    html += `<div class="tone-body">${escHtml(p.prompt)}</div>`;
    html += '</div>';
  }
  html += '</div>';
  main.innerHTML = html;

  // Nav
  document.getElementById("navInfo").textContent =
    `${currentIndex + 1} / ${filteredTasks.length}`;
  document.getElementById("prevBtn").disabled = currentIndex === 0;
  document.getElementById("nextBtn").disabled = currentIndex === filteredTasks.length - 1;
  updateProgress();
  updateFlagBtn();
}

function updateProgress() {
  const flags = getFlags();
  // Count flagged as "reviewed" (seen)
  const reviewed = filteredTasks.filter((_, i) => i <= currentIndex).length;
  const pct = filteredTasks.length ? (reviewed / filteredTasks.length * 100) : 0;
  document.getElementById("progressFill").style.width = pct + "%";
  document.getElementById("progressText").textContent =
    `${reviewed}/${filteredTasks.length} viewed`;
  // Flag count
  const totalFlagged = Object.values(flags).filter(Boolean).length;
  document.getElementById("flagCount").textContent = totalFlagged;
}

function updateFlagBtn() {
  if (!filteredTasks.length) return;
  const taskId = filteredTasks[currentIndex];
  const flags = getFlags();
  const btn = document.getElementById("flagBtn");
  btn.classList.toggle("flagged", !!flags[taskId]);
  btn.innerHTML = flags[taskId] ? "&#9873; Flagged" : "&#9873; Flag";
}

function toggleFlag() {
  if (!filteredTasks.length) return;
  const taskId = filteredTasks[currentIndex];
  const flags = getFlags();
  flags[taskId] = !flags[taskId];
  if (!flags[taskId]) delete flags[taskId];
  saveFlags(flags);
  updateFlagBtn();
  updateProgress();
}

function toggleShowFlagged() {
  showFlaggedOnly = !showFlaggedOnly;
  currentIndex = 0;
  document.getElementById("showFlaggedBtn").classList.toggle("active", showFlaggedOnly);
  render();
}

function navigate(dir) {
  currentIndex += dir;
  render();
  window.scrollTo(0, 0);
}

function escHtml(s) {
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

document.addEventListener("keydown", e => {
  if (e.key === "ArrowLeft") { e.preventDefault(); if (currentIndex > 0) navigate(-1); }
  else if (e.key === "ArrowRight") { e.preventDefault(); if (currentIndex < filteredTasks.length - 1) navigate(1); }
  else if (e.key === "f" || e.key === "F") { e.preventDefault(); toggleFlag(); }
  else if (e.key >= "1" && e.key <= "4") {
    e.preventDefault();
    const d = ["factual","coding","creative","analysis"][+e.key - 1];
    currentDomain = currentDomain === d ? "all" : d;
    currentIndex = 0;
    render();
  }
});

render();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate prompt review HTML page")
    parser.add_argument("--data", default="data/prompts.jsonl", help="Path to prompts JSONL")
    parser.add_argument("--out", default="review.html", help="Output HTML file")
    args = parser.parse_args()

    prompts = read_jsonl(args.data)
    if not prompts:
        print(f"No prompts found in {args.data}")
        return 1

    prompts_json = json.dumps(prompts, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__PROMPTS_JSON__", prompts_json)

    Path(args.out).write_text(html, encoding="utf-8")
    print(f"Wrote {args.out} ({len(prompts)} prompts, {len(set(p['task_id'] for p in prompts))} tasks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
