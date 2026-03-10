"""
ValueBet Oracle - FastAPI ML 推論服務
Phase 5: lifespan 載入模型與 Scaler、MatchFeatures / PredictionResult、POST /api/v1/predict
"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 與 train_model 一致的特徵順序
from train_model import FEATURE_COLUMNS, MODELS_DIR

# 全域模型與 Scaler（lifespan 載入）
_model: Any = None
_scaler: Any = None


def _load_artifacts() -> tuple[Any, Any]:
    clf_path = MODELS_DIR / "xgb_classifier.joblib"
    scaler_path = MODELS_DIR / "scaler.joblib"
    if not clf_path.exists() or not scaler_path.exists():
        raise FileNotFoundError(
            "請先執行 train_model.py 產生 models/xgb_classifier.joblib 與 models/scaler.joblib"
        )
    clf = joblib.load(clf_path)
    scaler = joblib.load(scaler_path)
    return clf, scaler


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _scaler
    try:
        _model, _scaler = _load_artifacts()
    except FileNotFoundError:
        _model, _scaler = None, None
    yield
    _model = _scaler = None


app = FastAPI(title="ValueBet Oracle ML API", version="1.0.0", lifespan=lifespan)


class MatchFeatures(BaseModel):
    """前端/Rust 傳入的球隊即時特徵矩陣（與 FEATURE_COLUMNS 順序對應）。"""
    home_court_advantage: float = Field(..., ge=0, le=1)
    home_rolling_pts_scored: float = Field(..., ge=0)
    home_rolling_pts_allowed: float = Field(..., ge=0)
    away_rolling_pts_scored: float = Field(..., ge=0)
    away_rolling_pts_allowed: float = Field(..., ge=0)
    home_back_to_back: float = Field(..., ge=0, le=1)
    away_back_to_back: float = Field(..., ge=0, le=1)
    home_ortg: float = Field(..., ge=0)
    home_drtg: float = Field(..., ge=0)
    away_ortg: float = Field(..., ge=0)
    away_drtg: float = Field(..., ge=0)
    home_net_rating: float = Field(...)
    away_net_rating: float = Field(...)
    strength_difference: float = Field(...)


class PredictionResult(BaseModel):
    """預測結果：主隊獲勝機率與信心分數。"""
    home_win_prob: float = Field(..., ge=0, le=1, description="主隊獲勝機率 0.0~1.0")
    confidence_score: float = Field(..., ge=0, le=1, description="預測信心 (機率與 0.5 的距離)")


def _features_to_vector(f: MatchFeatures) -> np.ndarray:
    """將 Pydantic 特徵轉為與 FEATURE_COLUMNS 順序一致的一維陣列。"""
    return np.array([
        f.home_court_advantage,
        f.home_rolling_pts_scored,
        f.home_rolling_pts_allowed,
        f.away_rolling_pts_scored,
        f.away_rolling_pts_allowed,
        f.home_back_to_back,
        f.away_back_to_back,
        f.home_ortg,
        f.home_drtg,
        f.away_ortg,
        f.away_drtg,
        f.home_net_rating,
        f.away_net_rating,
        f.strength_difference,
    ], dtype=np.float64).reshape(1, -1)


@app.post("/api/v1/predict", response_model=PredictionResult)
def predict(features: MatchFeatures) -> PredictionResult:
    """接收特徵、縮放、推論，回傳主隊獲勝機率與信心分數。"""
    if _model is None or _scaler is None:
        raise HTTPException(status_code=503, detail="模型尚未載入")
    X = _features_to_vector(features)
    X_scaled = _scaler.transform(X)
    proba = _model.predict_proba(X_scaled)[0, 1]
    confidence = abs(proba - 0.5) * 2  # 0~1，越接近 0.5 信心越低
    return PredictionResult(home_win_prob=round(proba, 6), confidence_score=round(confidence, 6))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_loaded": str(_model is not None)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
