//! ValueBet Oracle - Rust API Gateway 進入點
//! 綁定 GET /api/value-bets，CORS 允許 Angular 存取

use axum::routing::get;
use axum::Router;
use tower_http::cors::{Any, CorsLayer};
use tracing_subscriber::EnvFilter;

mod handlers;
mod models;
mod services;
mod utils;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env().add_directive("info".parse().unwrap()))
        .init();

    let client = reqwest::Client::new();
    let ml_base_url = std::env::var("ML_ENGINE_URL").unwrap_or_else(|_| "http://localhost:8000".to_string());
    let odds_api_key = std::env::var("ODDS_API_KEY").unwrap_or_else(|_| "".to_string());

    let state = handlers::AppState {
        http_client: client,
        ml_base_url,
        odds_api_key,
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/api/value-bets", get(handlers::get_value_bets))
        .layer(cors)
        .with_state(state);

    let addr = std::net::SocketAddr::from(([0, 0, 0, 0], 3000));
    tracing::info!("Gateway listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.expect("bind");
    axum::serve(listener, app).await.expect("serve");
}
