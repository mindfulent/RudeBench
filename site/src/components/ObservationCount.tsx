interface Props {
  count: number;
  lowThreshold?: number;
}

export default function ObservationCount({ count, lowThreshold = 20 }: Props) {
  const isLow = count < lowThreshold;
  return (
    <span
      className={`text-[10px] font-mono ${
        isLow
          ? 'text-amber-500 font-semibold'
          : 'text-[var(--color-text-muted)]'
      }`}
      title={isLow ? `Low observation count (n=${count})` : `n=${count}`}
    >
      n={count}
    </span>
  );
}
