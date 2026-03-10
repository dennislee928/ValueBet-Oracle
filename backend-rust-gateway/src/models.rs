//! 對應外部博弈 API（如 The-Odds-API）的賠率資料與 Python 預測請求/回傳結構。

use serde::Deserialize;
use serde::Serialize;

/// 外部賠率 API 單一賽事（簡化結構，可依實際 API 擴充）
#[derive(Debug, Clone, Deserialize)]
pub struct OddsEvent {
    pub id: Option<String>,
    pub sport_key: Option<String>,
    pub home_team: Option<String>,
    pub away_team: Option<String>,
    pub commence_time: Option<String>,
    pub bookmakers: Option<Vec<Bookmaker>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Bookmaker {
    pub key: Option<String>,
    pub title: Option<String>,
    pub markets: Option<Vec<Market>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Market {
    pub key: Option<String>,
    pub outcomes: Option<Vec<Outcome>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Outcome {
    pub name: Option<String>,
    pub price: Option<f64>,
    pub point: Option<f64>,
}

/// 向 Python ML 服務請求預測的 Payload（與 main.py MatchFeatures 對應）
#[derive(Debug, Clone, Serialize)]
pub struct MatchFeaturesPayload {
    pub home_court_advantage: f64,
    pub home_rolling_pts_scored: f64,
    pub home_rolling_pts_allowed: f64,
    pub away_rolling_pts_scored: f64,
    pub away_rolling_pts_allowed: f64,
    pub home_back_to_back: f64,
    pub away_back_to_back: f64,
    pub home_ortg: f64,
    pub home_drtg: f64,
    pub away_ortg: f64,
    pub away_drtg: f64,
    pub home_net_rating: f64,
    pub away_net_rating: f64,
    pub strength_difference: f64,
}

/// Python 預測 API 回傳結構
#[derive(Debug, Clone, Deserialize)]
pub struct PredictionResult {
    pub home_win_prob: f64,
    pub confidence_score: f64,
}
