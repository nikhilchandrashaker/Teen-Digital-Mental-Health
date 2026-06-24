"""
07_summary_for_report.py  -  collate every saved result into one markdown file.

Reads the CSV/TXT artifacts produced by Phases 1-6 and writes
outputs/results/SUMMARY_FOR_REPORT.md: the numeric backbone for the
1-2 page research brief.
"""
import os
import pandas as pd

import config

R = config.RESULTS_DIR
out = ["# Results summary — for the research brief",
       "*All figures are in `outputs/figures/`. Numbers below are produced by "
       "the pipeline; data are SIMULATED (see README).*", ""]


def read(name):
    p = os.path.join(R, name)
    return pd.read_csv(p) if os.path.exists(p) else None


# group means
gm = read("group_means.csv")
if gm is not None:
    out += ["## Descriptive: outcomes by usage group", gm.to_markdown(index=False), ""]

# correlations
cm = read("correlation_matrix.csv")
if cm is not None:
    cm = cm.set_index("variable")
    keys = [("daily_social_media_hours", "stress_level"),
            ("sleep_hours", "stress_level"),
            ("sleep_hours", "academic_performance"),
            ("daily_social_media_hours", "sleep_hours"),
            ("daily_social_media_hours", "academic_performance")]
    lines = [f"- **{a}** vs **{b}**: r = {cm.loc[a, b]:+.3f}" for a, b in keys]
    out += ["## Key correlations (Pearson)", *lines, ""]

# t-tests
tt = read("ttest_results.csv")
if tt is not None:
    out += ["## Group comparisons (Welch t-tests)", tt.to_markdown(index=False), ""]

# regression
for tag, title in [("stress", "Stress model"),
                   ("academic", "Academic-performance model")]:
    cf = read(f"regression_{tag}_coefficients.csv")
    if cf is not None:
        keep = cf[cf["term"].isin(config.PREDICTORS)][
            ["term", "coef", "std_err", "p_value", "std_beta"]]
        out += [f"## Regression — {title} (key predictors)",
                keep.to_markdown(index=False), ""]

# mediation
med = read("mediation_results.csv")
if med is not None:
    out += ["## Mediation (social media -> sleep -> stress)",
            med.to_markdown(index=False), ""]

# DERI
dc = read("deri_correlations.csv")
if dc is not None:
    out += ["## Digital Exposure Risk Index (DERI)",
            dc.to_markdown(index=False), ""]
dq = read("deri_quartile_outcomes.csv")
if dq is not None:
    out += ["### Outcomes by DERI quartile", dq.to_markdown(index=False), ""]

path = os.path.join(R, "SUMMARY_FOR_REPORT.md")
with open(path, "w") as f:
    f.write("\n".join(out))
print(f"[07] Wrote {path}")
