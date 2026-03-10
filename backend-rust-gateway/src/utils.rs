//! 賠率轉換工具：美式/分數賠率 -> 小數賠率、隱含機率

/// 美式賠率 (American Odds) 轉小數賠率 (Decimal Odds)
/// 正數如 +150 => 2.5，負數如 -200 => 1.5
pub fn american_to_decimal(american: f64) -> Option<f64> {
    if american == 0.0 {
        return None;
    }
    let decimal = if american > 0.0 {
        1.0 + american / 100.0
    } else {
        1.0 + 100.0 / (-american)
    };
    Some(decimal)
}

/// 分數賠率 (Fractional，如 3/2) 轉小數賠率
/// numerator/denominator => decimal = 1 + num/den
pub fn fractional_to_decimal(numerator: f64, denominator: f64) -> Option<f64> {
    if denominator == 0.0 {
        return None;
    }
    Some(1.0 + numerator / denominator)
}

/// 隱含機率 (Implied Probability): 1 / Decimal_Odds
pub fn implied_probability(decimal_odds: f64) -> Option<f64> {
    if decimal_odds <= 0.0 {
        return None;
    }
    Some(1.0 / decimal_odds)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_american_to_decimal() {
        assert!((american_to_decimal(150.0).unwrap() - 2.5).abs() < 1e-6);
        assert!((american_to_decimal(-200.0).unwrap() - 1.5).abs() < 1e-6);
    }

    #[test]
    fn test_implied_probability() {
        assert!((implied_probability(2.0).unwrap() - 0.5).abs() < 1e-6);
    }
}
