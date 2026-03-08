#!/usr/bin/env python3
"""Generate a self-contained HTML viewer for coding task renders.

Reads completion JSONL files and produces a single HTML page with inline
iframe rendering of all coding task outputs, organized by task × model × tone.

Usage: python scripts/extract_renders.py [--completions-dir results/completions] [--out analysis/coding_review.html]
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rudebench.config import load_yaml
from rudebench.utils import read_jsonl

TONES = ["grateful", "friendly", "neutral", "curt", "hostile", "abusive"]


def extract_html(response: str) -> str:
    """Extract HTML content from a model response.

    Handles markdown code fences, raw HTML, and fallback to raw text.
    """
    # Try markdown code fence: ```html ... ```
    fence_match = re.search(
        r"```(?:html)?\s*\n(.*?)```", response, re.DOTALL
    )
    if fence_match:
        candidate = fence_match.group(1).strip()
        if "<" in candidate:
            return candidate

    # Try finding <!DOCTYPE or <html> block
    doctype_match = re.search(
        r"(<!DOCTYPE\s+html[^>]*>.*)", response, re.DOTALL | re.IGNORECASE
    )
    if doctype_match:
        return doctype_match.group(1).strip()

    html_match = re.search(r"(<html[\s>].*)", response, re.DOTALL | re.IGNORECASE)
    if html_match:
        return html_match.group(1).strip()

    # Fallback: raw response
    return response


def extract_tone(prompt_id: str) -> str | None:
    """Extract tone from prompt_id suffix (handles multi-underscore slugs)."""
    for tone in TONES:
        if prompt_id.endswith(f"_{tone}"):
            return tone
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate coding render comparison viewer"
    )
    parser.add_argument(
        "--completions-dir",
        default="results/completions",
        help="Directory containing completion JSONL files",
    )
    parser.add_argument(
        "--out",
        default="analysis/coding_review.html",
        help="Output HTML file",
    )
    args = parser.parse_args()

    completions_dir = Path(args.completions_dir)

    # Load model IDs from config
    models_cfg = load_yaml(Path("config/models.yaml"))
    model_ids = [m["id"] for m in models_cfg["models"]]

    # Scan for JSONL files, match to model IDs
    jsonl_files = sorted(completions_dir.glob("*.jsonl"))
    if not jsonl_files:
        print(f"No JSONL files found in {completions_dir}")
        return 1

    # Build data structure
    renders = {}  # model -> task -> tone -> run -> {html, finish_reason, word_count, refused}
    all_tasks = set()
    all_models = []

    for jf in jsonl_files:
        model_id = jf.stem
        records = read_jsonl(jf)
        coding_records = [r for r in records if r["task_id"].startswith("coding_")]
        if not coding_records:
            continue

        all_models.append(model_id)
        renders[model_id] = {}

        for rec in coding_records:
            task_id = rec["task_id"]
            tone = extract_tone(rec["prompt_id"])
            if tone is None:
                continue
            run = rec.get("run", 1)
            all_tasks.add(task_id)

            if task_id not in renders[model_id]:
                renders[model_id][task_id] = {}
            if tone not in renders[model_id][task_id]:
                renders[model_id][task_id][tone] = {}

            html_content = extract_html(rec["response"]) if not rec.get("refused") else ""
            html_b64 = base64.b64encode(html_content.encode("utf-8")).decode("ascii")

            renders[model_id][task_id][tone][run] = {
                "html": html_b64,
                "finish_reason": rec.get("finish_reason", "unknown"),
                "word_count": rec.get("word_count", 0),
                "refused": rec.get("refused", False),
            }

    all_tasks = sorted(all_tasks)
    all_models.sort()

    if not all_tasks:
        print("No coding completions found in any JSONL file.")
        print("Generate completions first: python -m rudebench generate --models MODEL")
        return 1

    payload = {
        "models": all_models,
        "tasks": all_tasks,
        "tones": TONES,
        "renders": renders,
    }

    data_json = json.dumps(payload, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    total_renders = sum(
        1
        for m in renders.values()
        for t in m.values()
        for tone in t.values()
        for _ in tone.values()
    )
    print(
        f"Wrote {args.out} ({len(all_models)} models, {len(all_tasks)} tasks, {total_renders} renders)"
    )
    return 0


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RudeBench Coding Render Comparison</title>
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --surface2: #1c2129;
    --border: #30363d;
    --text: #e1e4ed;
    --text2: #8b90a0;
    --accent: #6c8cff;
    --accent2: #4a6adf;
    --green: #4ade80;
    --yellow: #facc15;
    --orange: #fb923c;
    --red: #f87171;
    --purple: #c084fc;
    --grateful: #2ecc71;
    --friendly: #3498db;
    --neutral: #95a5a6;
    --curt: #f39c12;
    --hostile: #e74c3c;
    --abusive: #8e44ad;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }

  /* Header */
  .header {
    position: sticky; top: 0; z-index: 100;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }
  .header h1 { font-size: 16px; font-weight: 600; white-space: nowrap; }
  .controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .control-group { display: flex; align-items: center; gap: 6px; }
  .control-group label { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px; }
  select {
    background: var(--surface2); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 5px 10px; font-size: 13px; cursor: pointer;
    font-family: inherit;
  }
  select:hover { border-color: var(--accent); }
  .toggle-btn {
    padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border); background: transparent;
    color: var(--text2); transition: all 0.15s;
  }
  .toggle-btn:hover { border-color: var(--accent); color: var(--text); }
  .toggle-btn.active { background: var(--accent2); border-color: var(--accent); color: #fff; }
  .spacer { margin-left: auto; }
  .task-counter { font-size: 13px; color: var(--text2); white-space: nowrap; }

  /* Grid */
  .main { padding: 20px 24px; }
  .tones-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
  }
  @media (max-width: 1600px) { .tones-grid { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 900px) { .tones-grid { grid-template-columns: 1fr; } }

  /* Tone cards */
  .tone-card {
    border-radius: 10px; border: 1px solid var(--border); overflow: hidden;
    background: var(--surface);
  }
  .tone-card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 14px; font-size: 13px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .tone-card-header .left { display: flex; align-items: center; gap: 8px; }
  .tone-card-header .right { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 400; }

  .tone-grateful .tone-card-header { background: #1a2e1e; color: var(--grateful); }
  .tone-friendly .tone-card-header { background: #1a2430; color: var(--friendly); }
  .tone-neutral .tone-card-header { background: #1e2125; color: var(--neutral); }
  .tone-curt .tone-card-header { background: #2a2510; color: var(--curt); }
  .tone-hostile .tone-card-header { background: #2a1515; color: var(--hostile); }
  .tone-abusive .tone-card-header { background: #251530; color: var(--abusive); }

  .badge {
    padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-stop { background: #1a2e1a; color: var(--green); }
  .badge-length { background: #2e2a1a; color: var(--orange); }
  .badge-refused { background: #2e1a1a; color: var(--red); }
  .badge-unknown { background: #1e2125; color: var(--text2); }
  .wc { color: var(--text2); }

  /* Iframe area */
  .iframe-wrap {
    padding: 8px; background: var(--surface);
  }
  .iframe-wrap iframe {
    width: 100%; height: 500px; border: 1px solid var(--border);
    border-radius: 6px; background: #fff; resize: vertical;
  }

  /* Source view */
  .source-wrap {
    display: none; padding: 8px;
  }
  .source-wrap.visible { display: block; }
  .source-wrap pre {
    background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
    padding: 12px; font-size: 12px; line-height: 1.5; overflow-x: auto;
    max-height: 300px; overflow-y: auto; color: var(--text2);
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  /* Empty state */
  .empty-state {
    padding: 60px 20px; text-align: center; color: var(--text2); font-size: 14px;
  }
  .card-empty {
    padding: 40px 14px; text-align: center; color: var(--text2); font-size: 13px;
  }

  /* Keyboard hint */
  .keyboard-hint {
    text-align: center; padding: 12px; font-size: 12px; color: var(--text2);
    border-top: 1px solid var(--border); margin-top: 20px;
  }
  kbd {
    background: var(--surface2); border: 1px solid var(--border); border-radius: 4px;
    padding: 2px 6px; font-size: 11px; font-family: inherit;
  }
</style>
</head>
<body>

<div class="header">
  <h1>RudeBench Coding Renders</h1>
  <div class="controls">
    <div class="control-group">
      <label>Task</label>
      <select id="taskSelect"></select>
    </div>
    <div class="control-group">
      <label>Model</label>
      <select id="modelSelect"></select>
    </div>
    <div class="control-group" id="runGroup" style="display:none">
      <label>Run</label>
      <select id="runSelect"></select>
    </div>
    <button class="toggle-btn" id="sourceToggle" onclick="toggleSource()">Show Source</button>
  </div>
  <div class="spacer"></div>
  <span class="task-counter" id="taskCounter"></span>
</div>

<div class="main" id="main"></div>

<div class="keyboard-hint">
  <kbd>&larr;</kbd><kbd>&rarr;</kbd> Navigate tasks &nbsp;
  <kbd>M</kbd> Cycle model &nbsp;
  <kbd>R</kbd> Cycle run &nbsp;
  <kbd>S</kbd> Toggle source
</div>

<script>
const DATA = __DATA_JSON__;

const taskSelect = document.getElementById("taskSelect");
const modelSelect = document.getElementById("modelSelect");
const runSelect = document.getElementById("runSelect");
const runGroup = document.getElementById("runGroup");
const sourceToggle = document.getElementById("sourceToggle");
const main = document.getElementById("main");
const taskCounter = document.getElementById("taskCounter");

let showSource = false;

// Humanize task_id: "coding_binary_search_viz" -> "Binary Search Viz"
function humanize(taskId) {
  return taskId.replace(/^coding_/, "").replace(/_/g, " ")
    .replace(/\b\w/g, c => c.toUpperCase());
}

// Populate task dropdown
function initTaskSelect() {
  taskSelect.innerHTML = "";
  for (const t of DATA.tasks) {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = humanize(t);
    taskSelect.appendChild(opt);
  }
}

// Populate model dropdown
function initModelSelect() {
  modelSelect.innerHTML = "";
  for (const m of DATA.models) {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    modelSelect.appendChild(opt);
  }
}

// Get all runs for current task + model (union across tones)
function getAvailableRuns() {
  const model = modelSelect.value;
  const task = taskSelect.value;
  const runs = new Set();
  const modelData = DATA.renders[model];
  if (modelData && modelData[task]) {
    for (const tone of DATA.tones) {
      const toneData = modelData[task][tone];
      if (toneData) {
        for (const r of Object.keys(toneData)) runs.add(Number(r));
      }
    }
  }
  return [...runs].sort((a, b) => a - b);
}

function updateRunSelect() {
  const runs = getAvailableRuns();
  runSelect.innerHTML = "";
  for (const r of runs) {
    const opt = document.createElement("option");
    opt.value = r;
    opt.textContent = `Run ${r}`;
    runSelect.appendChild(opt);
  }
  runGroup.style.display = runs.length > 1 ? "flex" : "none";
  if (runs.length === 0) {
    const opt = document.createElement("option");
    opt.value = "1";
    opt.textContent = "Run 1";
    runSelect.appendChild(opt);
  }
}

function finishReasonBadge(fr) {
  if (fr === "stop") return '<span class="badge badge-stop">stop</span>';
  if (fr === "length") return '<span class="badge badge-length">length</span>';
  return `<span class="badge badge-unknown">${fr}</span>`;
}

function render() {
  const task = taskSelect.value;
  const model = modelSelect.value;
  const run = Number(runSelect.value) || 1;

  if (!task || !model) {
    main.innerHTML = '<div class="empty-state">No coding completions available.<br>Generate completions first.</div>';
    taskCounter.textContent = "";
    return;
  }

  const taskIdx = DATA.tasks.indexOf(task);
  taskCounter.textContent = `${taskIdx + 1} / ${DATA.tasks.length}`;

  const modelData = DATA.renders[model];
  const taskData = modelData ? modelData[task] : null;

  let html = '<div class="tones-grid">';
  for (const tone of DATA.tones) {
    const toneData = taskData ? taskData[tone] : null;
    const runData = toneData ? toneData[run] : null;

    html += `<div class="tone-card tone-${tone}">`;
    html += `<div class="tone-card-header">`;
    html += `<div class="left"><span>${tone}</span>`;

    if (runData) {
      if (runData.refused) {
        html += ' <span class="badge badge-refused">refused</span>';
      } else {
        html += ` ${finishReasonBadge(runData.finish_reason)}`;
      }
    }
    html += `</div>`;
    html += `<div class="right">`;
    if (runData && !runData.refused) {
      html += `<span class="wc">${runData.word_count} words</span>`;
    }
    html += `</div></div>`;

    if (!runData) {
      html += '<div class="card-empty">No completion available</div>';
    } else if (runData.refused) {
      html += '<div class="card-empty">Model refused this prompt</div>';
    } else {
      // Decode base64 HTML
      const rawHtml = atob(runData.html);
      // Iframe with srcdoc
      html += '<div class="iframe-wrap">';
      html += `<iframe sandbox="allow-scripts" srcdoc="${escAttr(rawHtml)}"></iframe>`;
      html += '</div>';
      // Source view
      html += `<div class="source-wrap${showSource ? " visible" : ""}">`;
      html += `<pre><code>${escHtml(rawHtml)}</code></pre>`;
      html += '</div>';
    }

    html += '</div>';
  }
  html += '</div>';
  main.innerHTML = html;
}

function escHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function escAttr(s) {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function toggleSource() {
  showSource = !showSource;
  sourceToggle.classList.toggle("active", showSource);
  sourceToggle.textContent = showSource ? "Hide Source" : "Show Source";
  // Toggle all source wraps
  document.querySelectorAll(".source-wrap").forEach(el => {
    el.classList.toggle("visible", showSource);
  });
}

function navigateTask(dir) {
  const idx = DATA.tasks.indexOf(taskSelect.value);
  const next = idx + dir;
  if (next >= 0 && next < DATA.tasks.length) {
    taskSelect.value = DATA.tasks[next];
    updateRunSelect();
    render();
  }
}

function cycleModel() {
  const idx = DATA.models.indexOf(modelSelect.value);
  modelSelect.value = DATA.models[(idx + 1) % DATA.models.length];
  updateRunSelect();
  render();
}

function cycleRun() {
  const runs = getAvailableRuns();
  if (runs.length <= 1) return;
  const idx = runs.indexOf(Number(runSelect.value));
  runSelect.value = runs[(idx + 1) % runs.length];
  render();
}

// Event listeners
taskSelect.addEventListener("change", () => { updateRunSelect(); render(); });
modelSelect.addEventListener("change", () => { updateRunSelect(); render(); });
runSelect.addEventListener("change", render);

document.addEventListener("keydown", e => {
  if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT") return;
  if (e.key === "ArrowLeft") { e.preventDefault(); navigateTask(-1); }
  else if (e.key === "ArrowRight") { e.preventDefault(); navigateTask(1); }
  else if (e.key === "m" || e.key === "M") { e.preventDefault(); cycleModel(); }
  else if (e.key === "r" || e.key === "R") { e.preventDefault(); cycleRun(); }
  else if (e.key === "s" || e.key === "S") { e.preventDefault(); toggleSource(); }
});

// Init
if (DATA.tasks.length === 0) {
  main.innerHTML = '<div class="empty-state">No coding completions found.<br>Generate completions first: <code>python -m rudebench generate</code></div>';
} else {
  initTaskSelect();
  initModelSelect();
  updateRunSelect();
  render();
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    sys.exit(main())
