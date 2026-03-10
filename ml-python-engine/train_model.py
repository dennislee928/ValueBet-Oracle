"""
ValueBet Oracle - 模型訓練與驗證
Phase 4: 時間順序切分、StandardScaler、XGBoost 分類、評估指標、特徵重要性、joblib 儲存
Mac 使用者若 XGBoost 載入失敗，請先執行: brew install libomp
"""
from pathlib import Path
from typing import Optional

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from data_pipeline import run_pipeline, DEFAULT_DATE_COL

# 用於訓練的特徵欄位（數值型）
FEATURE_COLUMNS = [
    "home_court_advantage",
    "home_rolling_pts_scored",
    "home_rolling_pts_allowed",
    "away_rolling_pts_scored",
    "away_rolling_pts_allowed",
    "home_back_to_back",
    "away_back_to_back",
    "home_ortg",
    "home_drtg",
    "away_ortg",
    "away_drtg",
    "home_net_rating",
    "away_net_rating",
    "strength_difference",
]
TARGET_CLASS = "is_home_win"
MODELS_DIR = Path(__file__).resolve().parent / "models"


def get_feature_matrix_and_labels(df: pd.DataFrame):
    """從 pipeline 輸出的 DataFrame 取得特徵矩陣 X 與標籤 y（僅使用有完整特徵的列）。"""
    available = [c for c in FEATURE_COLUMNS if c in df.columns]
    missing = set(FEATURE_COLUMNS) - set(available)
    if missing:
        raise ValueError(f"缺少特徵欄位: {missing}")
    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_CLASS].copy()
    # 刪除任一特徵為 NaN 的列（例如前幾場無 rolling 資料）
    valid = X.notna().all(axis=1)
    X = X.loc[valid].astype(np.float64)
    y = y.loc[valid].astype(int)
    return X, y


def train_and_evaluate(
    csv_path: str | Path,
    test_size: float = 0.2,
    random_state: int = 42,
    rolling_window: int = 5,
) -> tuple[XGBClassifier, StandardScaler, pd.Series]:
    """
    按時間順序切分資料、標準化、訓練 XGBoost、評估並回傳模型、Scaler、特徵重要性。
    """
    df = run_pipeline(csv_path, rolling_window=rolling_window)
    df = df.sort_values(DEFAULT_DATE_COL).reset_index(drop=True)
    X, y = get_feature_matrix_and_labels(df)
    if len(X) < 4:
        raise ValueError("資料筆數過少（需至少 4 筆完整特徵），請提供更多歷史賽事 CSV。")
    # 按時間順序切分：前 (1-test_size) 為訓練、後 test_size 為測試
    n = len(X)
    split_idx = int(n * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    # StandardScaler 擬合訓練集並轉換訓練/測試
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    # XGBoost 分類
    clf = XGBClassifier(random_state=random_state, use_label_encoder=False, eval_metric="logloss")
    clf.fit(X_train_scaled, y_train)
    # 預測與機率
    y_pred = clf.predict(X_test_scaled)
    y_prob = clf.predict_proba(X_test_scaled)[:, 1]
    # 評估
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    brier = brier_score_loss(y_test, y_prob)
    print("=== 評估指標 ===")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"Brier Score (越低越好): {brier:.4f}")
    # 特徵重要性
    importance = pd.Series(clf.feature_importances_, index=FEATURE_COLUMNS).sort_values(ascending=True)
    plot_feature_importance(importance)
    return clf, scaler, importance


def plot_feature_importance(importance: pd.Series, out_path: Optional[Path] = None) -> None:
    """繪製特徵重要性條形圖並輸出到 models/。"""
    out_path = out_path or (MODELS_DIR / "feature_importance.png")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    importance.plot(kind="barh", ax=ax)
    ax.set_title("Feature Importance (XGBoost)")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"特徵重要性圖已儲存: {out_path}")


def save_artifacts(clf: XGBClassifier, scaler: StandardScaler) -> None:
    """使用 joblib 將模型與 Scaler 儲存到 models/。"""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODELS_DIR / "xgb_classifier.joblib")
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    joblib.dump(FEATURE_COLUMNS, MODELS_DIR / "feature_columns.joblib")
    print(f"模型與 Scaler 已儲存至 {MODELS_DIR}")


if __name__ == "__main__":
    import sys
    data_dir = Path(__file__).resolve().parent / "data"
    csv_path = sys.argv[1] if len(sys.argv) > 1 else data_dir / "sample_matches.csv"
    if not Path(csv_path).exists():
        print("用法: python train_model.py [路徑/至/歷史賽事.csv]")
        sys.exit(1)
    clf, scaler, importance = train_and_evaluate(csv_path, test_size=0.25, rolling_window=3)
    save_artifacts(clf, scaler)
