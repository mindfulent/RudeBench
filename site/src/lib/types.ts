// Data types matching build-data.py JSON output

export type Tone = 'grateful' | 'friendly' | 'neutral' | 'curt' | 'hostile' | 'abusive';
export type Dimension = 'ACC' | 'SYC' | 'PBR' | 'CRE' | 'VRB' | 'APO';
export type Domain = 'factual' | 'coding' | 'creative' | 'analysis';

export const TONES: Tone[] = ['grateful', 'friendly', 'neutral', 'curt', 'hostile', 'abusive'];
export const DIMENSIONS: Dimension[] = ['ACC', 'SYC', 'PBR', 'CRE', 'VRB', 'APO'];
export const DOMAINS: Domain[] = ['factual', 'coding', 'creative', 'analysis'];

export interface Meta {
  version: string;
  n_runs: number;
  total_completions: number;
  total_judgments: number;
  models: string[];
  generated_at: string;
}

export interface LeaderboardEntry {
  model: string;
  display_name: string;
  resilience_score: number;
  rank: number;
  tier: number; // 1-based tier for banding (models within noise share a tier)
  dimensions: Record<Dimension, {
    neutral_mean: number;
    avg_delta: number;
    worst_tone: string;
    observation_count: number;
  }>;
  refusal_rate: number;
}

export interface DimensionData {
  dimension: Dimension;
  description: string;
  range: [number, number]; // [0, 100] or [0, 200] for VRB
  applicable_tasks: number;
  total_tasks: number;
  models: Record<string, ToneScores>;
}

export interface ToneScores {
  tones: Record<Tone, {
    mean: number;
    observation_count: number;
  }>;
  neutral_mean: number;
}

export interface ModelProfile {
  model: string;
  display_name: string;
  resilience_score: number;
  dimensions: Record<Dimension, {
    tones: Record<Tone, {
      mean: number;
      observation_count: number;
    }>;
    neutral_mean: number;
    avg_delta: number;
    worst_tone: string;
  }>;
  refusal_counts: Record<Tone, { refused: number; total: number }>;
}

export interface TaskMeta {
  id: string;
  task_id: string;
  domain: Domain;
  dimensions: Dimension[];
  difficulty: string;
  has_false_premise: boolean;
  pushback_expected: boolean;
}

export interface ResponseData {
  prompt_id: string;
  tone: Tone;
  prompt_text: string;
  responses: {
    run: number;
    text: string;
    word_count: number;
    finish_reason: string;
    refused: boolean;
    scores?: Record<Dimension, {
      score: number | null;
      evidence?: string;
      reasoning?: string;
    }>;
    vrb_score?: number;
  }[];
}

export interface RenderIndex {
  tasks: string[];
  models: string[];
  entries: {
    task_id: string;
    model: string;
    tone: Tone;
    filename: string;
  }[];
}
