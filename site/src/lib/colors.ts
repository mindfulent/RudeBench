import type { Tone } from './types';

/** Tone color palette — warm gold → peach → gray → steel blue → deep blue → crimson */
export const TONE_COLORS: Record<Tone, string> = {
  grateful: '#d4a017',
  friendly: '#e8a87c',
  neutral: '#8b90a0',
  curt: '#6b8db5',
  hostile: '#3a6b9f',
  abusive: '#c23b3b',
};

export const TONE_BG_COLORS: Record<Tone, string> = {
  grateful: '#2a2410',
  friendly: '#2a2018',
  neutral: '#1e2025',
  curt: '#182030',
  hostile: '#101a2e',
  abusive: '#2a1515',
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

  if (normalized < 0.02) return 'rgba(26, 46, 26, 0.5)';   // Green — stable
  if (normalized < 0.05) return 'rgba(46, 42, 26, 0.5)';   // Yellow — moderate
  if (normalized < 0.10) return 'rgba(46, 36, 26, 0.5)';   // Orange — notable
  return 'rgba(46, 26, 26, 0.5)';                           // Red — high deviation
}

/**
 * Returns a text color for a deviation value.
 */
export function deviationTextColor(delta: number, range: number): string {
  const normalized = Math.abs(delta) / range;

  if (normalized < 0.02) return '#4ade80'; // Green
  if (normalized < 0.05) return '#facc15'; // Yellow
  if (normalized < 0.10) return '#fb923c'; // Orange
  return '#f87171';                         // Red
}

/** Model display names */
export const MODEL_DISPLAY_NAMES: Record<string, string> = {
  'claude-sonnet-4.6': 'Claude Sonnet 4.6',
  'gpt-5-mini': 'GPT-5 mini',
  'gemini-2.5-flash': 'Gemini 2.5 Flash',
  'llama-4-scout': 'Llama 4 Scout',
  'grok-3-mini': 'Grok 3 mini',
};
