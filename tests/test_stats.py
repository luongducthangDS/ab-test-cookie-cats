import sys
from pathlib import Path

import numpy as np
import pytest
from statsmodels.stats.proportion import proportions_ztest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from stats import bootstrap_diff, mde_two_proportions, srm_test, two_proportion_z


def test_srm_balanced_split_passes():
    assert srm_test(5000, 5000)["p_value"] == pytest.approx(1.0)


def test_srm_detects_skewed_split():
    assert srm_test(5300, 4700)["p_value"] < 0.001


def test_z_test_matches_statsmodels():
    ours = two_proportion_z(400, 2000, 460, 2000)
    stat, p = proportions_ztest([460, 400], [2000, 2000])
    assert ours["z"] == pytest.approx(stat)
    assert ours["p_value"] == pytest.approx(p)
    assert ours["diff"] == pytest.approx(0.03)


def test_bootstrap_ci_covers_true_difference():
    a = np.r_[np.ones(1000), np.zeros(4000)]          # exactly 20 %
    b = np.r_[np.ones(1250), np.zeros(3750)]          # exactly 25 %
    r = bootstrap_diff(a, b, n_boot=1000)
    assert r["ci95"][0] < 0.05 < r["ci95"][1]
    assert r["prob_b_worse"] < 0.01


def test_mde_shrinks_with_sample_size():
    assert mde_two_proportions(0.2, 40000) < mde_two_proportions(0.2, 4000)
