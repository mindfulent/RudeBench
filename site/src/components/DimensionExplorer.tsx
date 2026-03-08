import { useState, useEffect } from 'react';
import type { DimensionData, Dimension, Tone, Domain } from '../lib/types';
import { TONES, DIMENSIONS, DOMAINS } from '../lib/types';
import { TONE_COLORS, TONE_LABELS, MODEL_DISPLAY_NAMES, deviationColor, deviationTextColor } from '../lib/colors';
import { DIMENSION_SHORT, DIMENSION_NOTES, DIMENSION_DESCRIPTIONS } from '../lib/scoring';

interface Props {
  dimensions: DimensionData[];
}

export default function DimensionExplorer({ dimensions }: Props) {
  const [selectedDim, setSelectedDim] = useState<Dimension>('SYC');
  const [selectedDomain, setSelectedDomain] = useState<Domain | 'all'>('all');

  // Read from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const dim = params.get('dim');
    const domain = params.get('domain');
    if (dim && DIMENSIONS.includes(dim as Dimension)) {
      setSelectedDim(dim as Dimension);
    }
    if (domain && (DOMAINS.includes(domain as Domain) || domain === 'all')) {
      setSelectedDomain(domain as Domain | 'all');
    }
  }, []);

  // Update URL on change
  useEffect(() => {
    const params = new URLSearchParams();
    params.set('dim', selectedDim);
    if (selectedDomain !== 'all') params.set('domain', selectedDomain);
    const url = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', url);
  }, [selectedDim, selectedDomain]);

  const dimData = dimensions.find(d => d.dimension === selectedDim);
  if (!dimData) return null;

  const dimRange = dimData.range[1];
  const models = Object.keys(dimData.models);

  return (
    <div className="space-y-6">
      {/* Dimension tabs */}
      <div className="flex flex-wrap gap-2">
        {DIMENSIONS.map(dim => (
          <button
            key={dim}
            onClick={() => setSelectedDim(dim)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              selectedDim === dim
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-[var(--color-surface-2)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            }`}
          >
            {DIMENSION_SHORT[dim]}
          </button>
        ))}
      </div>

      {/* Dimension description */}
      <div className="text-sm text-[var(--color-text-secondary)]">
        <p>{DIMENSION_DESCRIPTIONS[selectedDim]}</p>
        {DIMENSION_NOTES[selectedDim] && (
          <p className="mt-1 text-xs text-amber-500">
            {DIMENSION_NOTES[selectedDim]}
          </p>
        )}
        <p className="mt-1 text-xs text-[var(--color-text-muted)]">
          Range: {dimData.range[0]}–{dimData.range[1]} | Applicable to {dimData.applicable_tasks}/{dimData.total_tasks} tasks
        </p>
      </div>

      {/* Domain filter */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Domain:</span>
        <div className="flex flex-wrap gap-1.5">
          {(['all', ...DOMAINS] as const).map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                selectedDomain === domain
                  ? 'bg-[var(--color-surface-3)] text-[var(--color-text-primary)] border border-[var(--color-border-light)]'
                  : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
              }`}
            >
              {domain === 'all' ? 'All' : domain.charAt(0).toUpperCase() + domain.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Heatmap table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left py-2 px-3 text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
                Model
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
            {models.map(model => {
              const md = dimData.models[model];
              // Use domain-specific data if a domain is selected
              const domainData = selectedDomain !== 'all' && md.by_domain?.[selectedDomain]
                ? md.by_domain[selectedDomain]
                : md;
              const tones = domainData.tones;
              const neutralMean = domainData.neutral_mean;

              // Compute avg delta
              let avgDelta = 0;
              let deltaCount = 0;
              for (const tone of TONES) {
                if (tone === 'neutral') continue;
                const toneData = tones[tone];
                if (toneData && toneData.mean !== null && neutralMean !== null) {
                  avgDelta += Math.abs(toneData.mean - neutralMean);
                  deltaCount++;
                }
              }
              if (deltaCount > 0) avgDelta /= deltaCount;

              return (
                <tr key={model} className="border-t border-[var(--color-border)]">
                  <td className="py-2 px-3">
                    <a
                      href={`/explore/${model}`}
                      className="text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors"
                    >
                      <span className="hidden sm:inline">{MODEL_DISPLAY_NAMES[model] || model}</span>
                      <span className="sm:hidden text-xs">{(MODEL_DISPLAY_NAMES[model] || model).split(' ').slice(-2).join(' ')}</span>
                    </a>
                  </td>
                  {TONES.map(tone => {
                    const toneData = tones[tone];
                    const value = toneData?.mean ?? null;
                    const count = toneData?.observation_count ?? 0;
                    const delta = value !== null && neutralMean !== null ? value - neutralMean : 0;
                    const isNeutral = tone === 'neutral';

                    const bgColor = !isNeutral && value !== null && neutralMean !== null
                      ? deviationColor(delta, dimRange)
                      : 'transparent';
                    const textColor = !isNeutral && value !== null && neutralMean !== null && Math.abs(delta) > 0
                      ? deviationTextColor(delta, dimRange)
                      : 'var(--color-text-primary)';

                    return (
                      <td
                        key={tone}
                        className="text-center py-1.5 px-1"
                      >
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
                    <span className="font-mono text-sm text-[var(--color-text-primary)]">
                      {avgDelta.toFixed(1)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 text-xs text-[var(--color-text-muted)] pt-4 border-t border-[var(--color-border)]">
        <span>Deviation from neutral:</span>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: 'rgba(26, 46, 26, 0.5)' }}></div>
          <span>&lt;2%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: 'rgba(46, 42, 26, 0.5)' }}></div>
          <span>2–5%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: 'rgba(46, 36, 26, 0.5)' }}></div>
          <span>5–10%</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded" style={{ backgroundColor: 'rgba(46, 26, 26, 0.5)' }}></div>
          <span>&gt;10%</span>
        </div>
      </div>
    </div>
  );
}
