# Memo: keep the first gate at level 30, after one data check

**To:** Game product lead · **Test:** 90,189 new players randomly assigned to gate at level 30 (control) or level 40
· **Full numbers:** `reports/results.json`

## Recommendation

1. **Do not move the gate to level 40.** Players with the gate at 40 were less likely to come back after a week:
   **18.20% vs 19.02%**, a drop of 0.82 points (−4.3% relative). The chance that level 40 is genuinely worse is
   about 99.9%.
2. **Before closing the test, check the assignment.** The two groups are not the 50/50 split that was intended
   (44,700 vs 45,489 players). A gap this large happens by chance less than 1 time in 100. If some players were
   dropped from one group (for example, a logging bug for players who quit early), the result could be biased.

## Why

| Metric | Gate 30 | Gate 40 | Difference (95% CI) | Verdict |
|---|---:|---:|---|---|
| Day-7 retention (primary) | 19.02% | 18.20% | −0.82 pts (−1.33 to −0.31) | Worse, p = 0.002 |
| Day-1 retention | 44.82% | 44.23% | −0.59 pts (−1.24 to +0.06) | No clear difference, p = 0.07 |
| Rounds played (median) | 17 | 16 | rank test p = 0.050 | Borderline; guardrail not clearly broken |

- The test could detect a difference of 0.74 points at 80% power. The observed −0.82 is above that threshold,
  so the result is not a false negative risk.
- Removing one extreme player (49,854 rounds) changes nothing (−0.82 pts, p = 0.002).

## What this does not tell us

- **Why** players leave earlier with the gate at 40. A plausible reason is that a later break lets players burn out,
  but that is a hypothesis, not something this data shows.
- Revenue: the data has no purchases. A later gate might still change in-app spending.
- We did **not** split results by "players who reached level 30". That group is defined *after* treatment, and
  comparing it would bias the result.
