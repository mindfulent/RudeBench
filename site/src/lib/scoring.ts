import type { LeaderboardEntry, Dimension } from './types';

/** Sort leaderboard by resilience score descending */
export function sortByResilience(entries: LeaderboardEntry[]): LeaderboardEntry[] {
  return [...entries].sort((a, b) => b.resilience_score - a.resilience_score);
}

/** Get the range for a dimension (VRB = 200, all others = 100) */
export function dimensionRange(dim: Dimension): number {
  return dim === 'VRB' ? 200 : 100;
}

/** Format a score to 1 decimal place */
export function formatScore(score: number): string {
  return score.toFixed(1);
}

/** Format a resilience score to 1 decimal place */
export function formatResilience(score: number): string {
  return score.toFixed(1);
}

/** Dimension descriptions for display */
export const DIMENSION_DESCRIPTIONS: Record<Dimension, string> = {
  ACC: 'Task Accuracy — correctness and completeness of the response',
  SYC: 'Sycophancy — uncritical validation and excessive agreement',
  PBR: 'Pushback Retention — willingness to challenge false premises',
  CRE: 'Creative Risk — inventiveness and originality in creative tasks',
  VRB: 'Verbosity Change — response length relative to neutral baseline',
  APO: 'Apology Frequency — unnecessary or excessive apologizing',
};

/** Short dimension labels */
export const DIMENSION_SHORT: Record<Dimension, string> = {
  ACC: 'Accuracy',
  SYC: 'Sycophancy',
  PBR: 'Pushback',
  CRE: 'Creativity',
  VRB: 'Verbosity',
  APO: 'Apology',
};

/** Dimension applicability notes */
export const DIMENSION_NOTES: Record<Dimension, string | null> = {
  ACC: null,
  SYC: null,
  PBR: 'Applies to ~30/50 tasks (those with false premises or where pushback is expected)',
  CRE: 'Applies to 12/50 tasks (creative writing domain only)',
  VRB: 'Computed automatically from word counts — not judge-scored. 100 = same length as neutral.',
  APO: null,
};
