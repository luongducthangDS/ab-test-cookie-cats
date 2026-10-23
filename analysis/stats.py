"""Small, tested statistics helpers for a two-arm A/B test on binary metrics."""
import numpy as np
from scipy import stats


def srm_test(n_a: int, n_b: int, expected_share_a: float = 0.5) -> dict:
    """Sample-ratio mismatch: is the split consistent with the intended allocation?"""
    total = n_a + n_b
    expected = [total * expected_share_a, total * (1 - expected_share_a)]
    chi2, p = stats.chisquare([n_a, n_b], expected)
    return {"n_a": n_a, "n_b": n_b, "share_a": n_a / total, "chi2": float(chi2), "p_value": float(p)}


def two_proportion_z(x_a: int, n_a: int, x_b: int, n_b: int) -> dict:
    """Difference B - A with a pooled-variance z-test and an unpooled 95 % Wald CI."""
    p_a, p_b = x_a / n_a, x_b / n_b
    pooled = (x_a + x_b) / (n_a + n_b)
    se_pooled = np.sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se_pooled
    se = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    diff = p_b - p_a
    return {"p_a": p_a, "p_b": p_b, "diff": diff, "ci95": [diff - 1.96 * se, diff + 1.96 * se],
            "z": float(z), "p_value": float(2 * stats.norm.sf(abs(z)))}


def bootstrap_diff(a: np.ndarray, b: np.ndarray, n_boot: int = 5000, seed: int = 0) -> dict:
    """Bootstrap distribution of mean(b) - mean(a); returns 95 % CI and P(diff < 0)."""
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = rng.choice(b, b.size).mean() - rng.choice(a, a.size).mean()
    return {"ci95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
            "prob_b_worse": float((diffs < 0).mean())}


def mde_two_proportions(p: float, n_per_arm: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Smallest absolute difference detectable with this sample size (normal approximation)."""
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    return float(z * np.sqrt(2 * p * (1 - p) / n_per_arm))
