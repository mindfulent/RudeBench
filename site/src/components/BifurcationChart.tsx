import { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { DimensionData, Tone, Dimension } from '../lib/types';
import { TONES, DIMENSIONS } from '../lib/types';
import { MODEL_DISPLAY_NAMES } from '../lib/colors';
import { DIMENSION_SHORT } from '../lib/scoring';

const TONE_LABELS: Record<Tone, string> = {
  grateful: 'Grateful',
  friendly: 'Friendly',
  neutral: 'Neutral',
  curt: 'Curt',
  hostile: 'Hostile',
  abusive: 'Abusive',
};

/** Model colors — Group A (resilient) in cool blues, Group B (reactive) in warm tones */
const MODEL_COLORS: Record<string, string> = {
  'claude-sonnet-4.6': '#2563eb',
  'gpt-5-mini': '#60a5fa',
  'gemini-2.5-flash': '#dc2626',
  'grok-3-mini': '#ea580c',
  'llama-4-scout': '#d97706',
};

const GROUP_A = ['claude-sonnet-4.6', 'gpt-5-mini'];
const GROUP_B = ['gemini-2.5-flash', 'grok-3-mini', 'llama-4-scout'];

interface Props {
  dimensionsData: DimensionData[];
}

export default function BifurcationChart({ dimensionsData }: Props) {
  const [selectedDim, setSelectedDim] = useState<Dimension>('SYC');

  const dimData = useMemo(
    () => dimensionsData.find(d => d.dimension === selectedDim),
    [dimensionsData, selectedDim]
  );

  const chartData = useMemo(() => {
    if (!dimData) return [];
    return TONES.map(tone => {
      const point: Record<string, string | number> = { tone: TONE_LABELS[tone] };
      for (const model of Object.keys(dimData.models)) {
        const toneData = dimData.models[model].tones[tone];
        if (toneData) {
          point[model] = toneData.mean;
        }
      }
      return point;
    });
  }, [dimData]);

  const models = dimData ? Object.keys(dimData.models) : [];

  // Compute Y-axis domain dynamically
  const yMax = useMemo(() => {
    if (!chartData.length) return 25;
    let max = 0;
    for (const point of chartData) {
      for (const model of models) {
        const v = point[model];
        if (typeof v === 'number' && v > max) max = v;
      }
    }
    return Math.ceil(max * 1.15 / 5) * 5; // Round up to nearest 5 with 15% headroom
  }, [chartData, models]);

  return (
    <div>
      {/* Dimension selector */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {DIMENSIONS.map(dim => (
          <button
            key={dim}
            onClick={() => setSelectedDim(dim)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              selectedDim === dim
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-[var(--color-surface-2)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-3)]'
            }`}
          >
            {DIMENSION_SHORT[dim]}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="w-full" style={{ height: 'clamp(280px, 40vw, 420px)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="tone"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
              tickLine={false}
            />
            <YAxis
              domain={[0, yMax]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
              tickLine={false}
              width={36}
            />
            <Tooltip
              contentStyle={{
                background: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '13px',
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
              }}
              formatter={(value: number, name: string) => [
                value.toFixed(1),
                MODEL_DISPLAY_NAMES[name] || name,
              ]}
              labelStyle={{ fontWeight: 600, marginBottom: 4, color: '#111827' }}
            />
            <Legend
              formatter={(value: string) => (
                <span style={{ fontSize: '12px', color: '#4b5563' }}>
                  {MODEL_DISPLAY_NAMES[value] || value}
                </span>
              )}
              iconSize={10}
              wrapperStyle={{ paddingTop: 8 }}
            />
            {/* Neutral reference line */}
            <ReferenceLine
              x="Neutral"
              stroke="#9ca3af"
              strokeDasharray="4 4"
              strokeWidth={1}
            />
            {/* Group A — solid lines (resilient) */}
            {models.filter(m => GROUP_A.includes(m)).map(model => (
              <Line
                key={model}
                type="monotone"
                dataKey={model}
                stroke={MODEL_COLORS[model]}
                strokeWidth={2.5}
                dot={{ r: 3, fill: MODEL_COLORS[model] }}
                activeDot={{ r: 5 }}
              />
            ))}
            {/* Group B — dashed lines (reactive) */}
            {models.filter(m => GROUP_B.includes(m)).map(model => (
              <Line
                key={model}
                type="monotone"
                dataKey={model}
                stroke={MODEL_COLORS[model]}
                strokeWidth={2.5}
                strokeDasharray="6 3"
                dot={{ r: 3, fill: MODEL_COLORS[model] }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Group labels */}
      <div className="flex flex-wrap gap-x-6 gap-y-1 mt-3 text-xs text-[var(--color-text-muted)]">
        <span>
          <span className="inline-block w-6 border-t-2 border-[#2563eb] align-middle mr-1.5" />
          Solid = resilient group
        </span>
        <span>
          <span className="inline-block w-6 border-t-2 border-dashed border-[#dc2626] align-middle mr-1.5" />
          Dashed = reactive group
        </span>
      </div>
    </div>
  );
}
