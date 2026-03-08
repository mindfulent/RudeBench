import type { ModelProfile as ModelProfileType, Dimension, Tone } from '../lib/types';
import { TONES, DIMENSIONS } from '../lib/types';
import { TONE_COLORS, TONE_LABELS, deviationColor, deviationTextColor } from '../lib/colors';
import { DIMENSION_SHORT, DIMENSION_NOTES, DIMENSION_DESCRIPTIONS } from '../lib/scoring';

interface Props {
  profile: ModelProfileType;
}

export default function ModelProfile({ profile }: Props) {
  return (
    <div className="space-y-8">
      {/* Score header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-full bg-[var(--color-surface-3)]">
            <span className="font-mono font-bold text-2xl text-[var(--color-text-primary)]">
              {profile.resilience_score.toFixed(1)}
            </span>
          </div>
          <span className="text-sm text-[var(--color-text-secondary)]">Resilience Score</span>
        </div>
      </div>

      {/* Dimensions heatmap */}
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-base font-bold mb-3 text-[var(--color-text-primary)]">
          Dimensions × Tones
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left py-2 px-3 text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
                  Dimension
                </th>
                {TONES.map(tone => (
                  <th
                    key={tone}
                    className="text-center py-2 px-2 text-xs uppercase tracking-wider"
                    style={{ color: TONE_COLORS[tone] }}
                  >
                    <span className="hidden sm:inline">{TONE_LABELS[tone]}</span>
                    <span className="sm:hidden">{tone.slice(0, 4)}</span>
                  </th>
                ))}
                <th className="text-center py-2 px-2 text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
                  <span className="hidden sm:inline">Avg |Δ|</span>
                  <span className="sm:hidden">Δ</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {DIMENSIONS.map(dim => {
                const d = profile.dimensions[dim];
                if (!d) return null;
                const dimRange = dim === 'VRB' ? 200 : 100;
                const neutralMean = d.neutral_mean;

                return (
                  <tr key={dim} className="border-t border-[var(--color-border)]">
                    <td className="py-2 px-3">
                      <div className="font-medium text-[var(--color-text-primary)]">{DIMENSION_SHORT[dim]}</div>
                      <div className="text-[10px] text-[var(--color-text-muted)] hidden sm:block">{dim}</div>
                    </td>
                    {TONES.map(tone => {
                      const toneData = d.tones[tone as Tone];
                      const value = toneData?.mean ?? null;
                      const count = toneData?.observation_count ?? 0;
                      const isNeutral = tone === 'neutral';
                      const delta = value !== null && neutralMean !== null ? value - neutralMean : 0;

                      const bgColor = !isNeutral && value !== null && neutralMean !== null
                        ? deviationColor(delta, dimRange)
                        : 'transparent';
                      const textColor = !isNeutral && value !== null && neutralMean !== null && Math.abs(delta) > 0
                        ? deviationTextColor(delta, dimRange)
                        : 'var(--color-text-primary)';

                      return (
                        <td key={tone} className="text-center py-1.5 px-1">
                          {value !== null ? (
                            <div className="rounded px-1 py-0.5" style={{ backgroundColor: bgColor }}>
                              <div className="font-mono text-xs sm:text-sm" style={{ color: textColor }}>
                                {value.toFixed(1)}
                              </div>
                              {!isNeutral && (
                                <div className="text-[9px] sm:text-[10px] text-[var(--color-text-muted)]">
                                  {delta >= 0 ? '+' : ''}{delta.toFixed(1)}
                                </div>
                              )}
                              <div className={`text-[9px] sm:text-[10px] font-mono ${count < 20 ? 'text-amber-500' : 'text-[var(--color-text-muted)]'}`}>
                                n={count}
                              </div>
                            </div>
                          ) : (
                            <span className="text-xs text-[var(--color-text-muted)]">N/A</span>
                          )}
                        </td>
                      );
                    })}
                    <td className="text-center py-2 px-2">
                      <div className="font-mono text-sm text-[var(--color-text-primary)]">
                        {d.avg_delta.toFixed(1)}
                      </div>
                      <div className="text-[10px] text-[var(--color-text-muted)]">
                        worst: {d.worst_tone}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Refusal rates */}
      <div>
        <h2 className="font-[family-name:var(--font-display)] text-base font-bold mb-3 text-[var(--color-text-primary)]">
          Refusal Rates
        </h2>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
          {TONES.map(tone => {
            const rc = profile.refusal_counts[tone as Tone];
            const rate = rc && rc.total > 0 ? (rc.refused / rc.total * 100) : 0;
            return (
              <div
                key={tone}
                className="rounded-lg p-2 sm:p-3 text-center border border-[var(--color-border)]"
                style={{ backgroundColor: rate > 0 ? 'rgba(46, 26, 26, 0.3)' : 'var(--color-surface)' }}
              >
                <div className="text-xs uppercase tracking-wider mb-1" style={{ color: TONE_COLORS[tone as Tone] }}>
                  <span className="hidden sm:inline">{TONE_LABELS[tone as Tone]}</span>
                  <span className="sm:hidden">{tone.slice(0, 4)}</span>
                </div>
                <div className="font-mono text-sm text-[var(--color-text-primary)]">
                  {rate.toFixed(1)}%
                </div>
                <div className="text-[10px] text-[var(--color-text-muted)]">
                  {rc?.refused ?? 0}/{rc?.total ?? 0}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Links */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-[var(--color-border)]">
        <a
          href="/explore"
          className="text-sm text-[var(--color-accent)] hover:underline"
        >
          ← Back to explorer
        </a>
        <a
          href={`/responses?model=${profile.model}`}
          className="text-sm text-[var(--color-accent)] hover:underline"
        >
          View responses →
        </a>
      </div>
    </div>
  );
}
