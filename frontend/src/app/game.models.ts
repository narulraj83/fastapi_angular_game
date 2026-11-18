export interface BlockShape {
  id: string;
  name: string;
  cells: number[][];
  color: string;
}

export interface GameStatus {
  id: number;
  difficulty: 'easy' | 'medium' | 'hard';
  board: number[][];
  available_blocks: BlockShape[];
  score: number;
  status: 'active' | 'paused' | 'game_over';
  moves: number;
  cleared_lines: number;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  display_name: string;
  best_score: number;
}

export interface HistoryEntry {
  id: number;
  difficulty: string;
  final_score: number;
  moves: number;
  cleared_lines: number;
  completed: boolean;
  created_at: string;
}

export interface Statistics {
  games_played: number;
  total_score: number;
  best_score: number;
  total_moves: number;
  total_cleared_lines: number;
}
