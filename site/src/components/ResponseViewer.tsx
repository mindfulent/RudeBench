import { useState, useEffect } from 'react';
import type { ResponseData, Tone, TaskMeta, Domain } from '../lib/types';
import { TONES, DOMAINS } from '../lib/types';
import { TONE_COLORS, TONE_LABELS, MODEL_DISPLAY_NAMES } from '../lib/colors';

const MODELS = ['claude-sonnet-4.6', 'gpt-5-mini', 'gemini-2.5-flash', 'llama-4-scout', 'grok-3-mini'];

interface Props {
  tasks: TaskMeta[];
}

export default function ResponseViewer({ tasks }: Props) {
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [selectedTask, setSelectedTask] = useState(tasks[0]?.task_id || '');
  const [selectedDomain, setSelectedDomain] = useState<Domain | 'all'>('all');
  const [selectedRun, setSelectedRun] = useState(1);
  const [compareMode, setCompareMode] = useState(false);
  const [compareTones, setCompareTones] = useState<Tone[]>(['neutral', 'abusive']);
  const [responseData, setResponseData] = useState<ResponseData[] | null>(null);
  const [loading, setLoading] = useState(false);

  // Read from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const model = params.get('model');
    const task = params.get('task');
    const domain = params.get('domain');
    if (model && MODELS.includes(model)) setSelectedModel(model);
    if (task) setSelectedTask(task);
    if (domain && (DOMAINS.includes(domain as Domain) || domain === 'all')) {
      setSelectedDomain(domain as Domain | 'all');
    }
  }, []);

  // Update URL
  useEffect(() => {
    const params = new URLSearchParams();
    params.set('model', selectedModel);
    params.set('task', selectedTask);
    if (selectedDomain !== 'all') params.set('domain', selectedDomain);
    window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
  }, [selectedModel, selectedTask, selectedDomain]);

  // Load response data on model/task change
  useEffect(() => {
    if (!selectedModel || !selectedTask) return;
    setLoading(true);
    fetch(`/data/responses/${selectedModel}/${selectedTask}.json`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        setResponseData(data);
        setLoading(false);
      })
      .catch(() => {
        setResponseData(null);
        setLoading(false);
      });
  }, [selectedModel, selectedTask]);

  const filteredTasks = selectedDomain === 'all'
    ? tasks
    : tasks.filter(t => t.domain === selectedDomain);

  // Ensure selected task is in filtered list
  useEffect(() => {
    if (filteredTasks.length > 0 && !filteredTasks.find(t => t.task_id === selectedTask)) {
      setSelectedTask(filteredTasks[0].task_id);
    }
  }, [selectedDomain]);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Model</label>
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm"
          >
            {MODELS.map(m => (
              <option key={m} value={m}>{MODEL_DISPLAY_NAMES[m] || m}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Domain</label>
          <select
            value={selectedDomain}
            onChange={e => setSelectedDomain(e.target.value as Domain | 'all')}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm"
          >
            <option value="all">All</option>
            {DOMAINS.map(d => (
              <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Task</label>
          <select
            value={selectedTask}
            onChange={e => setSelectedTask(e.target.value)}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm max-w-[200px] sm:max-w-none"
          >
            {filteredTasks.map(t => (
              <option key={t.task_id} value={t.task_id}>{humanize(t.task_id)}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Run</label>
          <select
            value={selectedRun}
            onChange={e => setSelectedRun(Number(e.target.value))}
            className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-md px-3 py-1.5 text-sm"
          >
            <option value={1}>Run 1</option>
            <option value={2}>Run 2</option>
          </select>
        </div>

        <button
          onClick={() => setCompareMode(!compareMode)}
          className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
            compareMode
              ? 'bg-[var(--color-accent)] text-white'
              : 'bg-[var(--color-surface-2)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
          }`}
        >
          Compare Tones
        </button>
      </div>

      {/* Compare tone selector */}
      {compareMode && (
        <div className="flex flex-wrap gap-2">
          {TONES.map(tone => (
            <button
              key={tone}
              onClick={() => {
                setCompareTones(prev =>
                  prev.includes(tone)
                    ? prev.filter(t => t !== tone)
                    : [...prev, tone]
                );
              }}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors border ${
                compareTones.includes(tone)
                  ? 'border-current'
                  : 'border-transparent opacity-40'
              }`}
              style={{ color: TONE_COLORS[tone] }}
            >
              {TONE_LABELS[tone]}
            </button>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-8 text-[var(--color-text-muted)]">Loading responses...</div>
      )}

      {/* Response display */}
      {!loading && responseData && (
        compareMode ? (
          <ToneComparison
            data={responseData}
            selectedTones={compareTones}
            selectedRun={selectedRun}
          />
        ) : (
          <ResponseList data={responseData} selectedRun={selectedRun} />
        )
      )}

      {!loading && !responseData && (
        <div className="text-center py-8 text-[var(--color-text-muted)]">
          No response data available for this model/task combination.
        </div>
      )}
    </div>
  );
}

function ResponseList({ data, selectedRun }: { data: ResponseData[]; selectedRun: number }) {
  const [expandedTone, setExpandedTone] = useState<Tone | null>(null);

  return (
    <div className="space-y-3">
      {data.map(rd => {
        const response = rd.responses.find(r => r.run === selectedRun) || rd.responses[0];
        if (!response) return null;
        const isExpanded = expandedTone === rd.tone;

        return (
          <div key={rd.tone} className="rounded-lg border border-[var(--color-border)] overflow-hidden">
            <button
              onClick={() => setExpandedTone(isExpanded ? null : rd.tone)}
              className="w-full flex items-center justify-between px-4 py-3 bg-[var(--color-surface)] hover:bg-[var(--color-surface-2)] transition-colors"
            >
              <div className="flex items-center gap-3">
                <span
                  className="text-sm font-semibold uppercase tracking-wider"
                  style={{ color: TONE_COLORS[rd.tone] }}
                >
                  {TONE_LABELS[rd.tone]}
                </span>
                {response.refused && (
                  <span className="text-xs px-2 py-0.5 rounded bg-red-900/30 text-red-400">
                    Refused
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 text-xs text-[var(--color-text-muted)]">
                <span>{response.word_count} words</span>
                <span>{response.finish_reason}</span>
                {response.scores && Object.keys(response.scores).length > 0 && (
                  <div className="hidden sm:flex gap-2">
                    {Object.entries(response.scores).map(([dim, s]) => (
                      s.score !== null && (
                        <span key={dim} className="text-[var(--color-text-secondary)]">
                          {dim}:{s.score}
                        </span>
                      )
                    ))}
                  </div>
                )}
                <svg
                  className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>
            {isExpanded && (
              <div className="border-t border-[var(--color-border)]">
                {/* Prompt */}
                {rd.prompt_text && (
                  <div className="px-4 py-3 bg-[var(--color-surface-2)]">
                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Prompt</div>
                    <div className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">
                      {rd.prompt_text}
                    </div>
                  </div>
                )}
                {/* Response */}
                <div className="px-4 py-3">
                  <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Response</div>
                  <div className="text-sm text-[var(--color-text-primary)] whitespace-pre-wrap max-h-96 overflow-y-auto">
                    {response.text}
                  </div>
                </div>
                {/* Scores */}
                {response.scores && Object.keys(response.scores).length > 0 && (
                  <div className="px-4 py-3 border-t border-[var(--color-border)] bg-[var(--color-surface)]">
                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Judge Scores</div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      {Object.entries(response.scores).map(([dim, s]) => (
                        <div key={dim} className="text-center p-2 rounded bg-[var(--color-surface-2)]">
                          <div className="text-xs text-[var(--color-text-muted)]">{dim}</div>
                          <div className="font-mono font-bold text-[var(--color-text-primary)]">
                            {s.score !== null ? s.score : 'N/A'}
                          </div>
                        </div>
                      ))}
                      {response.vrb_score !== undefined && response.vrb_score !== null && (
                        <div className="text-center p-2 rounded bg-[var(--color-surface-2)]">
                          <div className="text-xs text-[var(--color-text-muted)]">VRB</div>
                          <div className="font-mono font-bold text-[var(--color-text-primary)]">
                            {response.vrb_score.toFixed(1)}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function ToneComparison({ data, selectedTones, selectedRun }: {
  data: ResponseData[];
  selectedTones: Tone[];
  selectedRun: number;
}) {
  const filtered = data.filter(d => selectedTones.includes(d.tone));

  return (
    <div className={`grid gap-4 ${
      filtered.length === 2 ? 'grid-cols-1 md:grid-cols-2' :
      filtered.length === 3 ? 'grid-cols-1 md:grid-cols-3' :
      'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
    }`}>
      {filtered.map(rd => {
        const response = rd.responses.find(r => r.run === selectedRun) || rd.responses[0];
        if (!response) return null;

        return (
          <div
            key={rd.tone}
            className="rounded-lg border border-[var(--color-border)] overflow-hidden flex flex-col"
          >
            <div
              className="px-4 py-2 flex items-center justify-between"
              style={{ backgroundColor: `${TONE_COLORS[rd.tone]}15` }}
            >
              <span className="text-sm font-semibold" style={{ color: TONE_COLORS[rd.tone] }}>
                {TONE_LABELS[rd.tone]}
              </span>
              <span className="text-xs text-[var(--color-text-muted)]">
                {response.word_count} words
              </span>
            </div>
            <div className="p-4 flex-1 overflow-y-auto max-h-[500px]">
              <div className="text-sm text-[var(--color-text-primary)] whitespace-pre-wrap">
                {response.refused ? (
                  <span className="text-red-400">Model refused this prompt</span>
                ) : (
                  response.text
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function humanize(taskId: string): string {
  return taskId
    .replace(/^(factual|coding|creative|analysis)_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}
