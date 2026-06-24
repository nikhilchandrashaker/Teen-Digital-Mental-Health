"""
06_deri.py  -  Phase 6: Digital Exposure Risk Index (original contribution)

DERI combines three behaviors into a single per-student risk score:
    + daily social-media hours        (more = higher risk)
    + screen time before sleep        (more = higher risk)
    - sleep hours                     (less = higher risk -> orientation flipped)

Construction: standardize each component (z-score), flip the sleep component,
average with equal weights -> deri_z, then min-max rescale to 0-100 -> deri_score.
Equal weighting keeps the index transparent and explainable; we validate it
against a PCA-derived weighting as a robustness check.

The index is appended to clean_teen_mental_health.csv and correlated with the
stress and academic-performance outcomes.
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

import config
import utils

utils.set_style()
df = pd.read_csv(config.CLEAN_CSV)

# --- assemble oriented standardized components ---------------------------
comp = pd.DataFrame(index=df.index)
for c in config.DERI_POSITIVE:
    comp[c] = df[c + "_z"]
for c in config.DERI_NEGATIVE:
    comp["neg_" + c] = -df[c + "_z"]          # flip: less sleep = more risk

df["deri_z"] = comp.mean(axis=1)              # equal-weight composite
lo, hi = df["deri_z"].min(), df["deri_z"].max()
df["deri_score"] = 100 * (df["deri_z"] - lo) / (hi - lo)   # 0-100, sample-relative
df["deri_quartile"] = pd.qcut(df["deri_z"], 4, labels=["Q1", "Q2", "Q3", "Q4"])

# --- correlations with outcomes -----------------------------------------
rows = []
for out in config.OUTCOMES:
    r, p = stats.pearsonr(df["deri_z"], df[out])
    rows.append({"index": "DERI (equal weight)", "outcome": out,
                 "pearson_r": round(r, 3), "p_value": float(f"{p:.3e}")})

# --- PCA robustness check ------------------------------------------------
pca = PCA(n_components=1)
pc1 = pca.fit_transform(comp.values).ravel()
if np.corrcoef(pc1, df["deri_z"])[0, 1] < 0:   # align sign with DERI
    pc1 = -pc1
df["deri_pca"] = pc1
ev = pca.explained_variance_ratio_[0]
r_align = np.corrcoef(pc1, df["deri_z"])[0, 1]
for out in config.OUTCOMES:
    r, p = stats.pearsonr(pc1, df[out])
    rows.append({"index": f"DERI (PCA, {ev:.0%} var)", "outcome": out,
                 "pearson_r": round(r, 3), "p_value": float(f"{p:.3e}")})

deri_corr = pd.DataFrame(rows)
utils.save_table(deri_corr, "deri_correlations.csv")
print("[06] DERI correlations with outcomes:\n", deri_corr.to_string(index=False))
print(f"     PCA first component explains {ev:.1%} of component variance; "
      f"corr(PCA, equal-weight DERI) = {r_align:.3f}")

# --- quartile outcome means ---------------------------------------------
q = df.groupby("deri_quartile", observed=True).agg(
    n=("deri_z", "size"),
    mean_stress=("stress_level", "mean"),
    mean_gpa=("academic_performance", "mean"),
    mean_deri_score=("deri_score", "mean"),
).round(3)
utils.save_table(q.reset_index(), "deri_quartile_outcomes.csv")
print("\n[06] Outcomes by DERI quartile:\n", q.to_string())

# --- persist DERI back into the clean dataset (final deliverable) --------
df.to_csv(config.CLEAN_CSV, index=False)
print(f"[06] DERI columns appended to {config.CLEAN_CSV}")

# ---------------------------- figures -----------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.2))
sns.histplot(df["deri_score"], bins=26, kde=True, color=utils.PALETTE[3], ax=ax)
ax.set_xlabel(config.LABELS["deri_score"])
ax.set_title("Distribution of the Digital Exposure Risk Index")
utils.save_fig(fig, "fig_deri_distribution.png")

for out, fname in [("stress_level", "fig_deri_vs_stress.png"),
                   ("academic_performance", "fig_deri_vs_academic.png")]:
    r = df["deri_z"].corr(df[out])
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    sns.regplot(data=df, x="deri_score", y=out,
                scatter_kws={"alpha": 0.2, "s": 14, "color": utils.PALETTE[0]},
                line_kws={"color": utils.PALETTE[1], "lw": 2.4}, ax=ax)
    ax.set_xlabel(config.LABELS["deri_score"])
    ax.set_ylabel(config.LABELS[out])
    ax.set_title(f"DERI vs {config.LABELS[out]}  (r = {r:+.2f})")
    utils.save_fig(fig, fname)

# quartile comparison (stress + GPA side by side)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
order = ["Q1", "Q2", "Q3", "Q4"]
sns.barplot(data=df, x="deri_quartile", y="stress_level", order=order,
            hue="deri_quartile", palette="flare", legend=False,
            errorbar="se", ax=axes[0])
axes[0].set_xlabel("DERI quartile (Q1=lowest risk)")
axes[0].set_ylabel(config.LABELS["stress_level"])
axes[0].set_title("Mean stress by DERI quartile")
sns.barplot(data=df, x="deri_quartile", y="academic_performance", order=order,
            hue="deri_quartile", palette="crest", legend=False,
            errorbar="se", ax=axes[1])
axes[1].set_xlabel("DERI quartile (Q1=lowest risk)")
axes[1].set_ylabel(config.LABELS["academic_performance"])
axes[1].set_title("Mean GPA by DERI quartile")
utils.save_fig(fig, "fig_deri_quartile_outcomes.png")
print("[06] DERI figures saved.")
