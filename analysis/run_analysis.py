"""Cookie Cats A/B test: does moving the first gate from level 30 to level 40 change retention?

Run from the project root:  python analysis/run_analysis.py
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats as st

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats import bootstrap_diff, mde_two_proportions, srm_test, two_proportion_z

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, GRID, A_COL, B_COL = "#1F2937", "#6B7280", "#E5E7EB", "#2563EB", "#DC2626"


def main():
    d = pd.read_csv(ROOT / "data" / "cookie_cats.csv")
    a, b = d[d.version == "gate_30"], d[d.version == "gate_40"]
    out = {}

    # 1. data checks before reading any result
    out["checks"] = {
        "rows": len(d), "duplicate_userids": int(d.userid.duplicated().sum()), "nulls": int(d.isna().sum().sum()),
        "zero_round_players_share": round(float((d.sum_gamerounds == 0).mean()), 4),
        "max_gamerounds": int(d.sum_gamerounds.max()), "p99_gamerounds": float(d.sum_gamerounds.quantile(0.99)),
        "srm": srm_test(len(a), len(b)),
    }

    # 2. primary (7-day retention) and secondary (1-day) metrics
    out["metrics"] = {}
    for m in ("retention_1", "retention_7"):
        z = two_proportion_z(int(a[m].sum()), len(a), int(b[m].sum()), len(b))
        boot = bootstrap_diff(a[m].to_numpy(float), b[m].to_numpy(float))
        out["metrics"][m] = {**z, "bootstrap": boot,
                             "relative_change": z["diff"] / z["p_a"],
                             "mde_80pct_power": mde_two_proportions(z["p_a"], min(len(a), len(b)))}

    # 3. guardrail: engagement (heavy-tailed -> rank test, and medians, not means)
    mw = st.mannwhitneyu(a.sum_gamerounds, b.sum_gamerounds)
    out["guardrail_gamerounds"] = {"median_a": float(a.sum_gamerounds.median()),
                                   "median_b": float(b.sum_gamerounds.median()),
                                   "mean_a": float(a.sum_gamerounds.mean()), "mean_b": float(b.sum_gamerounds.mean()),
                                   "mann_whitney_p": float(mw.pvalue)}

    # 4. robustness: does the 7-day result survive dropping the single 49,854-round outlier?
    trimmed = d[d.sum_gamerounds < d.sum_gamerounds.max()]
    ta, tb = trimmed[trimmed.version == "gate_30"], trimmed[trimmed.version == "gate_40"]
    out["robustness_without_outlier_retention_7"] = two_proportion_z(
        int(ta.retention_7.sum()), len(ta), int(tb.retention_7.sum()), len(tb))

    # round for readability
    def r(x):
        if isinstance(x, float):
            return round(x, 6)
        if isinstance(x, dict):
            return {k: r(v) for k, v in x.items()}
        if isinstance(x, list):
            return [r(v) for v in x]
        return x
    out = r(out)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "results.json").write_text(json.dumps(out, indent=2))

    # figure: retention by arm with 95 % CIs
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, m, title in zip(axes, ("retention_1", "retention_7"), ("Day-1 retention", "Day-7 retention (primary)")):
        vals = [a[m].mean(), b[m].mean()]
        errs = [1.96 * np.sqrt(v * (1 - v) / n) for v, n in zip(vals, (len(a), len(b)))]
        ax.bar(["gate 30", "gate 40"], [v * 100 for v in vals], yerr=[e * 100 for e in errs],
               color=[A_COL, B_COL], width=0.55, capsize=6)
        for i, v in enumerate(vals):
            ax.text(i, v * 100 + 1.2, f"{v:.2%}", ha="center", color=INK)
        mm = out["metrics"][m]
        ax.set_title(f"{title}\nΔ = {mm['diff'] * 100:+.2f} pts, p = {mm['p_value']:.3f}",
                     loc="left", fontweight="bold", color=INK, fontsize=10)
        ax.set_ylim(0, max(vals) * 100 * 1.25)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("% of players", color=MUTED)
    fig.tight_layout()
    fig.savefig(ROOT / "reports" / "figures" / "retention_by_arm.png", dpi=140)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
