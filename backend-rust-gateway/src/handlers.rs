//! API 路由 Handler：整合賠率、AI 預測、價值期望值並回傳 JSON

use axum::extract::State;
use axum::Json;
use serde::Serialize;

use crate::models::MatchFeaturesPayload;
use crate::services::{fetch_ai_prediction, value_edge};
use crate::utils::{american_to_decimal, implied_probability};

#[derive(Clone)]
pub struct AppState {
    pub http_client: reqwest::Client,
    pub ml_base_url: String,
    pub odds_api_key: String,
}

/// 單一價值投注建議（回傳給前端的格式）
#[derive(Debug, Serialize)]
pub struct ValueBetItem {
    pub home_team: String,
    pub away_team: String,
    pub decimal_odds: f64,
    pub implied_prob: f64,
    pub ai_home_win_prob: f64,
    pub value_edge: f64,
    pub is_value_bet: bool,
}

/// GET /api/value-bets：取得價值投注清單（簡化版：需前端或參數傳入特徵，此處用預設特徵示範）
pub async fn get_value_bets(State(state): State<AppState>) -> Json<Vec<ValueBetItem>> {
    let client = &state.http_client;
    let ml_url = &state.ml_base_url;

    // 預設特徵範例（實際應由前端傳入或從即時資料組出）
    let features = MatchFeaturesPayload {
        home_court_advantage: 1.0,
        home_rolling_pts_scored: 105.0,
        home_rolling_pts_allowed: 102.0,
        away_rolling_pts_scored: 100.0,
        away_rolling_pts_allowed: 104.0,
        home_back_to_back: 0.0,
        away_back_to_back: 0.0,
        home_ortg: 105.0,
        home_drtg: 102.0,
        away_ortg: 100.0,
        away_drtg: 104.0,
        home_net_rating: 3.0,
        away_net_rating: -4.0,
        strength_difference: 7.0,
    };

    let mut items = Vec::new();

    match fetch_ai_prediction(client, ml_url, &features).await {
        Ok(pred) => {
            // 假設一組莊家賠率（美式）用於示範
            let american_odds = 110.0; // 主隊 +110
            if let (Some(dec), Some(implied)) = (
                american_to_decimal(american_odds),
                american_to_decimal(american_odds).and_then(implied_probability),
            ) {
                let edge = value_edge(pred.home_win_prob, dec);
                items.push(ValueBetItem {
                    home_team: "Home".to_string(),
                    away_team: "Away".to_string(),
                    decimal_odds: dec,
                    implied_prob: implied,
                    ai_home_win_prob: pred.home_win_prob,
                    value_edge: edge,
                    is_value_bet: edge > 0.0,
                });
            }
        }
        Err(_) => {}
    }

    Json(items)
}
