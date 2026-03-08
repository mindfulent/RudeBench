import { useState, useEffect, useRef } from 'react';
import type { RenderIndex, Tone } from '../lib/types';
import { TONES } from '../lib/types';
import { TONE_COLORS, TONE_LABELS, MODEL_DISPLAY_NAMES } from '../lib/colors';

const MODEL_FULL_IDS: Record<string, string> = {
  claude: 'claude-sonnet-4.6',
  gpt5mini: 'gpt-5-mini',
  gemini: 'gemini-2.5-flash',
  llama: 'llama-4-scout',
  grok: 'grok-3-mini',
};

interface Props {
  index: RenderIndex;
}

export default function RenderViewer({ index }: Props) {
  const [selectedTask, setSelectedTask] = useState(index.tasks[0] || '');
  const [selectedModel, setSelectedModel] = useState(index.models[0] || '');
  const [showPrompt, setShowPrompt] = useState(false);
  const [promptTone, setPromptTone] = useState<Tone>('neutral');
  const [prompts, setPrompts] = useState<Record<string, string> | null>(null);
  const [promptLoading, setPromptLoading] = useState(false);
  const promptCache = useRef<Record<string, Record<string, string>>>({});

  // Update URL
  useEffect(() => {
    const params = new URLSearchParams();
    if (selectedTask) params.set('task', selectedTask);
    if (selectedModel) params.set('model', selectedModel);
    window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
  }, [selectedTask, selectedModel]);

  // Read from URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const task = params.get('task');
    const model = params.get('model');
    if (task && index.tasks.includes(task)) setSelectedTask(task);
    if (model && index.models.includes(model)) setSelectedModel(model);
  }, []);

  // Fetch prompts when needed
  useEffect(() => {
    if (!showPrompt || !selectedTask || !selectedModel) return;

    const fullModelId = MODEL_FULL_IDS[selectedModel] || selectedModel;
    const cacheKey = `${fullModelId}_${selectedTask}`;

    if (promptCache.current[cacheKey]) {
      setPrompts(promptCache.current[cacheKey]);
      return;
    }

    setPromptLoading(true);
    setPrompts(null);

    fetch(`/data/responses/${fullModelId}/${selectedTask}.json`)
      .then(r => r.json())
      .then((data: Array<{ tone: string; prompt_text: string }>) => {
        const map: Record<string, string> = {};
        for (const entry of data) {
          map[entry.tone] = entry.prompt_text;
        }
        promptCache.current[cacheKey] = map;
        setPrompts(map);
      })
      .catch(() => setPrompts(null))
      .finally(() => setPromptLoading(false));
  }, [showPrompt, selectedTask, selectedModel]);

  const matchingEntries = index.entries.filter(
    e => e.task_id === selectedTask && e.model === selectedModel
  );

  return (
    <div className="h-full flex flex-col gap-2">
      {/* Desktop-only notice */}
      <div className="sm:hidden rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
        The HTML render viewer is optimized for desktop. On mobile, you can view the task/model
        selector but the render grid works best on larger screens.
      </div>

      {/* Controls + nav in one row */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Task</label>
          <select
            value={selectedTask}
            onChange={e => setSelectedTask(e.target.value)}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm"
          >
            {index.tasks.map(t => (
              <option key={t} value={t}>{humanize(t)}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Model</label>
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm"
          >
            {index.models.map(m => (
              <option key={m} value={m}>{MODEL_DISPLAY_NAMES[m] || m}</option>
            ))}
          </select>
        </div>

        <button
          onClick={() => setShowPrompt(!showPrompt)}
          className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
            showPrompt
              ? 'bg-[var(--color-accent)] text-white'
              : 'bg-[var(--color-surface-2)] text-[var(--color-text-secondary)]'
          }`}
        >
          {showPrompt ? 'Hide Prompt' : 'Show Prompt'}
        </button>

        {/* Task navigation inline */}
        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={() => {
              const idx = index.tasks.indexOf(selectedTask);
              if (idx > 0) setSelectedTask(index.tasks[idx - 1]);
            }}
            disabled={index.tasks.indexOf(selectedTask) <= 0}
            className="px-2.5 py-1.5 rounded bg-[var(--color-surface-2)] text-[var(--color-text-secondary)] text-sm disabled:opacity-30"
          >
            &larr; Prev
          </button>
          <span className="text-xs text-[var(--color-text-muted)] tabular-nums">
            {index.tasks.indexOf(selectedTask) + 1}/{index.tasks.length}
          </span>
          <button
            onClick={() => {
              const idx = index.tasks.indexOf(selectedTask);
              if (idx < index.tasks.length - 1) setSelectedTask(index.tasks[idx + 1]);
            }}
            disabled={index.tasks.indexOf(selectedTask) >= index.tasks.length - 1}
            className="px-2.5 py-1.5 rounded bg-[var(--color-surface-2)] text-[var(--color-text-secondary)] text-sm disabled:opacity-30"
          >
            Next &rarr;
          </button>
        </div>
      </div>

      {/* Prompt panel */}
      {showPrompt && (
        <div className="shrink-0 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
          <div className="flex items-center gap-1 px-3 py-1.5 bg-[var(--color-surface-2)] border-b border-[var(--color-border)]">
            <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mr-2">Prompt</span>
            {TONES.map(tone => (
              <button
                key={tone}
                onClick={() => setPromptTone(tone)}
                className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                  promptTone === tone
                    ? 'text-white'
                    : 'opacity-60 hover:opacity-100'
                }`}
                style={{
                  color: promptTone === tone ? '#fff' : TONE_COLORS[tone],
                  backgroundColor: promptTone === tone ? TONE_COLORS[tone] : 'transparent',
                }}
              >
                {TONE_LABELS[tone]}
              </button>
            ))}
          </div>
          <div className="px-3 py-2 max-h-36 overflow-y-auto text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap leading-relaxed">
            {promptLoading ? (
              <span className="text-[var(--color-text-muted)]">Loading prompt...</span>
            ) : prompts && prompts[promptTone] ? (
              prompts[promptTone]
            ) : (
              <span className="text-[var(--color-text-muted)]">Prompt not available</span>
            )}
          </div>
        </div>
      )}

      {/* Render grid - 3x2 filling remaining viewport */}
      {matchingEntries.length > 0 ? (
        <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 grid-rows-1 md:grid-rows-2 gap-2">
          {TONES.map(tone => {
            const entry = matchingEntries.find(e => e.tone === tone);
            return (
              <div
                key={tone}
                className="rounded-lg border border-[var(--color-border)] overflow-hidden flex flex-col min-h-[300px]"
              >
                <div
                  className="px-3 py-1 text-xs font-semibold uppercase tracking-wider shrink-0"
                  style={{
                    color: TONE_COLORS[tone],
                    backgroundColor: `${TONE_COLORS[tone]}15`,
                  }}
                >
                  {TONE_LABELS[tone]}
                </div>
                {entry ? (
                  <div className="flex-1 min-h-0 p-1">
                    <iframe
                      src={`/renders/${entry.filename}`}
                      sandbox="allow-scripts"
                      className="w-full h-full border border-[var(--color-border)] rounded bg-white"
                      title={`${selectedTask} - ${tone} - ${selectedModel}`}
                    />
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-sm text-[var(--color-text-muted)]">
                    No render available
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-[var(--color-text-muted)]">
          No renders available for this task/model combination.
          Renders are currently available for: {index.models.join(', ')}.
        </div>
      )}
    </div>
  );
}

function humanize(taskId: string): string {
  return taskId
    .replace(/^coding_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}
