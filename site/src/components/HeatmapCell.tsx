import { deviationColor, deviationTextColor } from '../lib/colors';

interface Props {
  value: number | null;
  neutralValue: number | null;
  range: number;
  observationCount: number;
  showDeviation?: boolean;
}

export default function HeatmapCell({
  value,
  neutralValue,
  range,
  observationCount,
  showDeviation = true,
}: Props) {
  if (value === null) {
    return (
      <div className="px-2 py-1.5 text-center text-xs text-[var(--color-text-muted)]">
        N/A
      </div>
    );
  }

  const delta = neutralValue !== null ? value - neutralValue : 0;
  const bgColor = showDeviation && neutralValue !== null
    ? deviationColor(delta, range)
    : 'transparent';
  const textColor = showDeviation && neutralValue !== null && Math.abs(delta) > 0
    ? deviationTextColor(delta, range)
    : 'var(--color-text-primary)';

  return (
    <div
      className="px-2 py-1.5 text-center rounded"
      style={{ backgroundColor: bgColor }}
    >
      <div className="font-mono text-sm" style={{ color: textColor }}>
        {value.toFixed(1)}
      </div>
      {showDeviation && neutralValue !== null && (
        <div className="text-[10px] text-[var(--color-text-muted)]">
          {delta >= 0 ? '+' : ''}{delta.toFixed(1)}
        </div>
      )}
      {observationCount > 0 && (
        <div className={`text-[10px] font-mono ${observationCount < 20 ? 'text-amber-500' : 'text-[var(--color-text-muted)]'}`}>
          n={observationCount}
        </div>
      )}
    </div>
  );
}
