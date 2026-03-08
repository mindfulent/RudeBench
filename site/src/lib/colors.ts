import type { Tone } from './types';

/** Tone color palette — warm gold → peach → gray → steel blue → deep blue → crimson */
export const TONE_COLORS: Record<Tone, string> = {
  grateful: '#b8860b',
  friendly: '#d4845a',
  neutral: '#6b7280',
  curt: '#4a7bab',
  hostile: '#2d5a8e',
  abusive: '#b91c1c',
};

export const TONE_BG_COLORS: Record<Tone, string> = {
  grateful: '#fdf8ed',
  friendly: '#fdf3ed',
  neutral: '#f3f4f6',
  curt: '#edf2f8',
  hostile: '#e8eef6',
  abusive: '#fdf0f0',
};

export const TONE_LABELS: Record<Tone, string> = {
  grateful: 'Grateful',
  friendly: 'Friendly',
  neutral: 'Neutral',
  curt: 'Curt',
  hostile: 'Hostile',
  abusive: 'Abusive',
};

/**
 * Returns a background color for a heatmap cell based on deviation from neutral.
 * Green = low deviation (stable), yellow = moderate, red = high (unstable).
 */
export function deviationColor(delta: number, range: number): string {
  const normalized = Math.abs(delta) / range;

  if (normalized < 0.02) return 'rgba(220, 252, 231, 0.6)';  // Green tint — stable
  if (normalized < 0.05) return 'rgba(254, 249, 195, 0.6)';  // Yellow tint — moderate
  if (normalized < 0.10) return 'rgba(255, 237, 213, 0.6)';  // Orange tint — notable
  return 'rgba(254, 226, 226, 0.6)';                          // Red tint — high deviation
}

/**
 * Returns a text color for a deviation value.
 */
export function deviationTextColor(delta: number, range: number): string {
  const normalized = Math.abs(delta) / range;

  if (normalized < 0.02) return '#15803d'; // Green
  if (normalized < 0.05) return '#a16207'; // Yellow/amber
  if (normalized < 0.10) return '#c2410c'; // Orange
  return '#b91c1c';                         // Red
}

/** Model display names */
export const MODEL_DISPLAY_NAMES: Record<string, string> = {
  'claude-sonnet-4.6': 'Claude Sonnet 4.6',
  'gpt-5-mini': 'GPT-5 mini',
  'gemini-2.5-flash': 'Gemini 2.5 Flash',
  'llama-4-scout': 'Llama 4 Scout',
  'grok-3-mini': 'Grok 3 mini',
};
