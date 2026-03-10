"""
ValueBet Oracle - 數據管道：讀取、清理、特徵工程
Phase 2: 數據收集與清理
Phase 3: 特徵工程 (Home-Court, Rolling, Fatigue, ORtg/DRtg, Strength Difference, Labels)
"""
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

# 預設欄位（可依實際 CSV 調整）
DEFAULT_DATE_COL = "date"
DEFAULT_HOME_TEAM = "home_team"
DEFAULT_AWAY_TEAM = "away_team"
DEFAULT_HOME_SCORE = "home_score"
DEFAULT_AWAY_SCORE = "away_score"

# 球隊名稱對應：統一為標準名稱（例如 'LA Lakers' -> 'Los Angeles Lakers'）
TEAM_NAME_ALIASES: dict[str, str] = {
    "LA Lakers": "Los Angeles Lakers",
    "Lakers": "Los Angeles Lakers",
    "LA Clippers": "Los Angeles Clippers",
    "NY Knicks": "New York Knicks",
    "GSW": "Golden State Warriors",
    "Warriors": "Golden State Warriors",
    "Cavs": "Cleveland Cavaliers",
    "Celtics": "Boston Celtics",
    "Heat": "Miami Heat",
    "Spurs": "San Antonio Spurs",
    "Nets": "Brooklyn Nets",
}


def load_raw_matches(
    csv_path: str | Path,
    date_col: str = DEFAULT_DATE_COL,
    home_team_col: str = DEFAULT_HOME_TEAM,
    away_team_col: str = DEFAULT_AWAY_TEAM,
    home_score_col: str = DEFAULT_HOME_SCORE,
    away_score_col: str = DEFAULT_AWAY_SCORE,
) -> pd.DataFrame:
    """使用 pandas 讀取歷史賽事 CSV。"""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到資料檔: {path}")
    df = pd.read_csv(path)
    # 統一欄位名稱（若 CSV 用不同名稱可於呼叫端傳入）
    rename = {}
    if date_col != DEFAULT_DATE_COL and date_col in df.columns:
        rename[date_col] = DEFAULT_DATE_COL
    if home_team_col != DEFAULT_HOME_TEAM and home_team_col in df.columns:
        rename[home_team_col] = DEFAULT_HOME_TEAM
    if away_team_col != DEFAULT_AWAY_TEAM and away_team_col in df.columns:
        rename[away_team_col] = DEFAULT_AWAY_TEAM
    if home_score_col != DEFAULT_HOME_SCORE and home_score_col in df.columns:
        rename[home_score_col] = DEFAULT_HOME_SCORE
    if away_score_col != DEFAULT_AWAY_SCORE and away_score_col in df.columns:
        rename[away_score_col] = DEFAULT_AWAY_SCORE
    if rename:
        df = df.rename(columns=rename)
    return df


def clean_missing_and_invalid(df: pd.DataFrame) -> pd.DataFrame:
    """清除缺失值與不完整/非法比賽紀錄。"""
    required = [DEFAULT_DATE_COL, DEFAULT_HOME_TEAM, DEFAULT_AWAY_TEAM, DEFAULT_HOME_SCORE, DEFAULT_AWAY_SCORE]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"缺少必要欄位: {col}")
    # 刪除任一首要欄位為 NaN 的列
    out = df.dropna(subset=required).copy()
    # 分數需為非負整數
    out = out[
        out[DEFAULT_HOME_SCORE].ge(0) & out[DEFAULT_AWAY_SCORE].ge(0)
        & out[DEFAULT_HOME_SCORE].apply(lambda x: x == int(x) if pd.notna(x) else False)
        & out[DEFAULT_AWAY_SCORE].apply(lambda x: x == int(x) if pd.notna(x) else False)
    ]
    out[DEFAULT_HOME_SCORE] = out[DEFAULT_HOME_SCORE].astype(int)
    out[DEFAULT_AWAY_SCORE] = out[DEFAULT_AWAY_SCORE].astype(int)
    return out.reset_index(drop=True)


def normalize_dates_utc(df: pd.DataFrame) -> pd.DataFrame:
    """轉換日期/時間格式，統一為 UTC 以利時間序列分析。"""
    out = df.copy()
    col = DEFAULT_DATE_COL
    out[col] = pd.to_datetime(out[col], utc=True, errors="coerce")
    out = out.dropna(subset=[col])
    out = out.sort_values(col).reset_index(drop=True)
    return out


def normalize_team_names(df: pd.DataFrame, alias_map: Optional[dict[str, str]] = None) -> pd.DataFrame:
    """處理球隊名稱不一致，使用名稱對應字典。"""
    alias_map = alias_map or TEAM_NAME_ALIASES
    out = df.copy()
    def map_team(name: str) -> str:
        if pd.isna(name):
            return name
        s = str(name).strip()
        return alias_map.get(s, s)
    out[DEFAULT_HOME_TEAM] = out[DEFAULT_HOME_TEAM].apply(map_team)
    out[DEFAULT_AWAY_TEAM] = out[DEFAULT_AWAY_TEAM].apply(map_team)
    return out


# ---------- Phase 3: 特徵工程 ----------

def add_home_court_advantage(df: pd.DataFrame) -> pd.DataFrame:
    """主場優勢：固定特徵 1=主場, 0=客場（對主隊而言主場為 1）。"""
    out = df.copy()
    out["home_court_advantage"] = 1
    return out


def add_rolling_team_stats(
    df: pd.DataFrame,
    window: int = 5,
    team_col_home: str = DEFAULT_HOME_TEAM,
    team_col_away: str = DEFAULT_AWAY_TEAM,
    date_col: str = DEFAULT_DATE_COL,
) -> pd.DataFrame:
    """利用 pandas rolling 視窗計算每隊過去 window 場的平均得分與失分。"""
    out = df.copy()
    out = out.sort_values(date_col).reset_index(drop=True)
    # 先為每場比賽計算主客隊的「到該場為止」的歷史
    home_pts_scored = []
    home_pts_allowed = []
    away_pts_scored = []
    away_pts_allowed = []
    for i in range(len(out)):
        row = out.iloc[i]
        home_team = row[team_col_home]
        away_team = row[team_col_away]
        date = row[date_col]
        # 主隊：過去作為「主隊」的得分與「客隊」對手的得分
        home_as_home = out[(out[team_col_home] == home_team) & (out[date_col] < date)].tail(window)
        home_as_away = out[(out[team_col_away] == home_team) & (out[date_col] < date)].tail(window)
        home_scores = list(home_as_home[DEFAULT_HOME_SCORE]) + list(home_as_away[DEFAULT_AWAY_SCORE])
        home_allowed = list(home_as_home[DEFAULT_AWAY_SCORE]) + list(home_as_away[DEFAULT_HOME_SCORE])
        # 客隊
        away_as_home = out[(out[team_col_home] == away_team) & (out[date_col] < date)].tail(window)
        away_as_away = out[(out[team_col_away] == away_team) & (out[date_col] < date)].tail(window)
        away_scores = list(away_as_home[DEFAULT_HOME_SCORE]) + list(away_as_away[DEFAULT_AWAY_SCORE])
        away_allowed = list(away_as_home[DEFAULT_AWAY_SCORE]) + list(away_as_away[DEFAULT_HOME_SCORE])
        # 平均
        home_pts_scored.append(np.mean(home_scores) if home_scores else np.nan)
        home_pts_allowed.append(np.mean(home_allowed) if home_allowed else np.nan)
        away_pts_scored.append(np.mean(away_scores) if away_scores else np.nan)
        away_pts_allowed.append(np.mean(away_allowed) if away_allowed else np.nan)
    out["home_rolling_pts_scored"] = home_pts_scored
    out["home_rolling_pts_allowed"] = home_pts_allowed
    out["away_rolling_pts_scored"] = away_pts_scored
    out["away_rolling_pts_allowed"] = away_pts_allowed
    return out


def add_back_to_back_fatigue(
    df: pd.DataFrame,
    date_col: str = DEFAULT_DATE_COL,
    team_col_home: str = DEFAULT_HOME_TEAM,
    team_col_away: str = DEFAULT_AWAY_TEAM,
) -> pd.DataFrame:
    """疲勞指數：標記是否為背靠背出賽（前一日也有比賽）。"""
    out = df.copy()
    out = out.sort_values(date_col).reset_index(drop=True)
    home_b2b = []
    away_b2b = []
    for i in range(len(out)):
        d = out.iloc[i][date_col]
        h = out.iloc[i][team_col_home]
        a = out.iloc[i][team_col_away]
        prev_d = out[out[date_col] < d][date_col].max() if pd.notna(d) else None
        if prev_d is None or pd.isna(prev_d):
            home_b2b.append(0)
            away_b2b.append(0)
            continue
        prev_games = out[out[date_col] == prev_d]
        h_played = ((prev_games[team_col_home] == h) | (prev_games[team_col_away] == h)).any()
        a_played = ((prev_games[team_col_home] == a) | (prev_games[team_col_away] == a)).any()
        home_b2b.append(1 if h_played else 0)
        away_b2b.append(1 if a_played else 0)
    out["home_back_to_back"] = home_b2b
    out["away_back_to_back"] = away_b2b
    return out


def add_offensive_defensive_rating(df: pd.DataFrame) -> pd.DataFrame:
    """進攻效率 (ORtg) / 防守效率 (DRtg)：以每百回合得分/失分概念，用 rolling 得分/失分近似。"""
    out = df.copy()
    if "home_rolling_pts_scored" in out.columns and "away_rolling_pts_allowed" in out.columns:
        out["home_ortg"] = out["home_rolling_pts_scored"]
        out["home_drtg"] = out["home_rolling_pts_allowed"]
        out["away_ortg"] = out["away_rolling_pts_scored"]
        out["away_drtg"] = out["away_rolling_pts_allowed"]
    else:
        out["home_ortg"] = out[DEFAULT_HOME_SCORE]
        out["home_drtg"] = out[DEFAULT_AWAY_SCORE]
        out["away_ortg"] = out[DEFAULT_AWAY_SCORE]
        out["away_drtg"] = out[DEFAULT_HOME_SCORE]
    return out


def add_strength_difference(df: pd.DataFrame) -> pd.DataFrame:
    """雙方實力差距：主隊 (ORtg - DRtg) - 客隊 (ORtg - DRtg)。"""
    out = df.copy()
    out["home_net_rating"] = out["home_ortg"] - out["home_drtg"]
    out["away_net_rating"] = out["away_ortg"] - out["away_drtg"]
    out["strength_difference"] = out["home_net_rating"] - out["away_net_rating"]
    return out


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    """目標變數：is_home_win (0/1) 用於分類，point_difference 用於迴歸。"""
    out = df.copy()
    out["is_home_win"] = (out[DEFAULT_HOME_SCORE] > out[DEFAULT_AWAY_SCORE]).astype(int)
    out["point_difference"] = out[DEFAULT_HOME_SCORE] - out[DEFAULT_AWAY_SCORE]
    return out


def run_pipeline(
    csv_path: str | Path,
    rolling_window: int = 5,
    team_aliases: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """執行完整管道：讀取 → 清理 → 日期正規化 → 隊名正規化 → 特徵與標籤。"""
    df = load_raw_matches(csv_path)
    df = clean_missing_and_invalid(df)
    df = normalize_dates_utc(df)
    df = normalize_team_names(df, alias_map=team_aliases)
    df = add_home_court_advantage(df)
    df = add_rolling_team_stats(df, window=rolling_window)
    df = add_back_to_back_fatigue(df)
    df = add_offensive_defensive_rating(df)
    df = add_strength_difference(df)
    df = add_labels(df)
    return df


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent / "data"
    sample = data_dir / "sample_matches.csv"
    if sample.exists():
        result = run_pipeline(sample, rolling_window=3)
        print(result.head())
        print("Columns:", list(result.columns))
    else:
        print("請將 NBA/英超歷史數據 CSV 放入 data/ 目錄後再執行。")
