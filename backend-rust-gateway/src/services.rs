//! 外部賠率 API 與 Python ML 服務呼叫、價值期望值計算

use crate::models::{MatchFeaturesPayload, PredictionResult};
use crate::utils::{american_to_decimal, implied_probability};
use reqwest::Client;
use serde_json::Value;

const ML_PREDICT_URL: &str = "http://localhost:8000/api/v1/predict";

/// 價值期望值 (Value Edge): (AI_Prob * Decimal_Odds) - 1。> 0 表示 Value Bet
pub fn value_edge(ai_prob: f64, decimal_odds: f64) -> f64 {
    (ai_prob * decimal_odds) - 1.0
}

/// 向本機 Python 服務取得 AI 勝率
pub async fn fetch_ai_prediction(
    client: &Client,
    ml_base_url: &str,
    features: &MatchFeaturesPayload,
) -> Result<PredictionResult, String> {
    let url = format!("{}/api/v1/predict", ml_base_url.trim_end_matches('/'));
    let res = client
        .post(&url)
        .json(features)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    if !res.status().is_success() {
        let status = res.status();
        let body = res.text().await.unwrap_or_default();
        return Err(format!("ML API error {}: {}", status, body));
    }
    let result: PredictionResult = res.json().await.map_err(|e| e.to_string())?;
    Ok(result)
}

/// 向外部賠率 API 獲取今日賽事賠率（簡化：實際需依 The-Odds-API 等文件組 URL 與 headers）
pub async fn fetch_live_odds(
    client: &Client,
    api_key: &str,
    sport: &str,
) -> Result<Vec<Value>, String> {
    let url = format!(
        "https://api.the-odds-api.com/v4/sports/{}/odds/?apiKey={}&regions=us&markets=h2h",
        sport, api_key
    );
    let res = client
        .get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    if !res.status().is_success() {
        let status = res.status();
        let body = res.text().await.unwrap_or_default();
        return Err(format!("Odds API error {}: {}", status, body));
    }
    let events: Vec<Value> = res.json().await.map_err(|e| e.to_string())?;
    Ok(events)
}

/// 從賠率數值（美式）轉小數並計算隱含機率
pub fn decimal_and_implied_from_american(american: f64) -> (Option<f64>, Option<f64>) {
    let decimal = american_to_decimal(american);
    let implied = decimal.and_then(implied_probability);
    (decimal, implied)
}
