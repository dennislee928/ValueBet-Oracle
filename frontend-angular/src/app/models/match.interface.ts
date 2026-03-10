/** 對應 Rust GET /api/value-bets 回傳的單筆價值投注資料 */
export interface ValueBetItem {
  home_team: string;
  away_team: string;
  decimal_odds: number;
  implied_prob: number;
  ai_home_win_prob: number;
  value_edge: number;
  is_value_bet: boolean;
}
