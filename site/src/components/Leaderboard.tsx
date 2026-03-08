import { useState } from 'react';
import type { LeaderboardEntry, Dimension } from '../lib/types';
import { DIMENSIONS } from '../lib/types';
import { TONE_COLORS, MODEL_DISPLAY_NAMES } from '../lib/colors';
import { DIMENSION_SHORT } from '../lib/scoring';

interface Props {
  data: LeaderboardEntry[];
}

export default function Leaderboard({ data }: Props) {
  const [expandedModel, setExpandedModel] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      {/* Header row - hidden on mobile, shown as table header on desktop */}
      <div className="hidden lg:grid grid-cols-[2fr_1fr_1fr_1fr_1fr_1fr_1fr_1fr] gap-2 px-4 text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
        <div>Model</div>
        <div className="text-center">Resilience</div>
        {DIMENSIONS.map(dim => (
          <div key={dim} className="text-center">{dim}</div>
        ))}
      </div>

      {data.map((entry) => (
        <div key={entry.model} className="group">
          {/* Main row */}
          <button
            onClick={() => setExpandedModel(expandedModel === entry.model ? null : entry.model)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-2)] transition-colors"
          >
            {/* Desktop layout */}
            <div className="hidden lg:grid grid-cols-[2fr_1fr_1fr_1fr_1fr_1fr_1fr_1fr] gap-2 items-center px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-mono text-[var(--color-text-muted)] w-6">
                  #{entry.rank}
                </span>
                <div className="text-left">
                  <div className="font-semibold text-[var(--color-text-primary)]">
                    {entry.display_name}
                  </div>
                  {entry.refusal_rate > 0 && (
                    <div className="text-xs text-[var(--color-text-muted)]">
                      {entry.refusal_rate}% refusal rate
                    </div>
                  )}
                </div>
              </div>
              <div className="text-center">
                <ResilienceBadge score={entry.resilience_score} />
              </div>
              {DIMENSIONS.map(dim => {
                const d = entry.dimensions[dim];
                return (
                  <div key={dim} className="text-center">
                    <div className="text-sm font-mono text-[var(--color-text-primary)]">
                      {d.avg_delta.toFixed(1)}
                    </div>
                    <div className="text-[10px] text-[var(--color-text-muted)]">
                      n={d.observation_count}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Mobile layout */}
            <div className="lg:hidden px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-mono text-[var(--color-text-muted)]">
                    #{entry.rank}
                  </span>
                  <div className="text-left">
                    <div className="font-semibold text-[var(--color-text-primary)]">
                      {entry.display_name}
                    </div>
                  </div>
                </div>
                <ResilienceBadge score={entry.resilience_score} />
              </div>
              {/* Mini dimension summary on mobile */}
              <div className="flex flex-wrap gap-2 mt-2">
                {DIMENSIONS.map(dim => {
                  const d = entry.dimensions[dim];
                  return (
                    <span key={dim} className="text-xs text-[var(--color-text-muted)]">
                      {dim}:{d.avg_delta.toFixed(1)}
                    </span>
                  );
                })}
              </div>
            </div>
          </button>

          {/* Expanded detail */}
          {expandedModel === entry.model && (
            <div className="mt-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] p-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {DIMENSIONS.map(dim => {
                  const d = entry.dimensions[dim];
                  return (
                    <div key={dim} className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-[var(--color-text-primary)]">
                          {DIMENSION_SHORT[dim]}
                        </span>
                        <span className="text-xs text-[var(--color-text-muted)]">
                          n={d.observation_count}
                        </span>
                      </div>
                      <div className="text-xs text-[var(--color-text-secondary)]">
                        Neutral: {d.neutral_mean !== null ? d.neutral_mean.toFixed(1) : 'N/A'}
                        {' | '}
                        Avg delta: {d.avg_delta.toFixed(1)}
                        {' | '}
                        Worst: {d.worst_tone}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-3 flex gap-2">
                <a
                  href={`/explore/${entry.model}`}
                  className="text-xs text-[var(--color-accent)] hover:underline"
                >
                  View full profile →
                </a>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function ResilienceBadge({ score }: { score: number }) {
  return (
    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--color-surface-3)]">
      <span className="font-mono font-bold text-lg text-[var(--color-text-primary)]">
        {score.toFixed(1)}
      </span>
    </div>
  );
}
