"""
03_statistics.py  -  Phase 3: Core Statistical Analysis

  1. Pearson correlation matrix (continuous variables) + heatmap
  2. Group comparisons:
       * high vs low usage (median split)  -> stress, sleep, GPA
       * TikTok vs Instagram users         -> social-media hours, stress
  3. Independent-samples t-tests (Welch) with mean difference, 95% CI,
     and Cohen's d; one-way ANOVA across Low/Medium/High usage on stress.
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

import config
import utils

utils.set_style()
df = pd.read_csv(config.CLEAN_CSV)

# ========================================================================
# 1. Correlation matrix
# ========================================================================
corr = df[config.CONTINUOUS].corr(method="pearson").round(3)
utils.save_table(corr.reset_index().rename(columns={"index": "variable"}),
                 "correlation_matrix.csv")
print("[03] Key Pearson correlations:")
print(f"     social media  vs stress : r = {corr.loc['daily_social_media_hours','stress_level']:+.3f}")
print(f"     sleep         vs stress : r = {corr.loc['sleep_hours','stress_level']:+.3f}")
print(f"     sleep         vs GPA    : r = {corr.loc['sleep_hours','academic_performance']:+.3f}")
print(f"     social media  vs sleep  : r = {corr.loc['daily_social_media_hours','sleep_hours']:+.3f}")

labels = [config.LABELS.get(c, c) for c in corr.columns]
fig, ax = plt.subplots(figsize=(7.6, 6.4))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            vmin=-1, vmax=1, square=True, linewidths=0.5,
            xticklabels=labels, yticklabels=labels,
            cbar_kws={"label": "Pearson r", "shrink": 0.8}, ax=ax)
ax.set_title("Correlation matrix")
plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
utils.save_fig(fig, "fig_correlation_heatmap.png")


# ========================================================================
# 2-3. Group comparisons + t-tests
# ========================================================================
def welch_ttest(a, b, label):
    a = np.asarray(a, float); b = np.asarray(b, float)
    n1, n2 = len(a), len(b)
    m1, m2 = a.mean(), b.mean()
    s1, s2 = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(s1 / n1 + s2 / n2)
    df_w = (s1 / n1 + s2 / n2) ** 2 / (
        (s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1))
    t, p = stats.ttest_ind(a, b, equal_var=False)
    tcrit = stats.t.ppf(0.975, df_w)
    diff = m1 - m2
    return {
        "comparison": label,
        "group1_mean": round(m1, 3), "group2_mean": round(m2, 3),
        "mean_diff": round(diff, 3),
        "ci95_low": round(diff - tcrit * se, 3),
        "ci95_high": round(diff + tcrit * se, 3),
        "t": round(float(t), 3), "df": round(float(df_w), 1),
        "p_value": float(f"{p:.3e}"),
        "cohens_d": round(utils.cohens_d(a, b), 3),
        "n1": n1, "n2": n2,
    }


rows = []
high = df[df["high_low_usage"] == "High"]
low = df[df["high_low_usage"] == "Low"]
for var in ["stress_level", "sleep_hours", "academic_performance"]:
    rows.append(welch_ttest(high[var], low[var],
                            f"High vs Low usage: {var}"))

tt = df[df["primary_platform"] == "TikTok"]
ig = df[df["primary_platform"] == "Instagram"]
for var in ["daily_social_media_hours", "stress_level"]:
    rows.append(welch_ttest(tt[var], ig[var],
                            f"TikTok vs Instagram: {var}"))

ttests = pd.DataFrame(rows)
utils.save_table(ttests, "ttest_results.csv")
print("\n[03] t-tests (group1 - group2):\n", ttests.to_string(index=False))

# one-way ANOVA across the three usage groups on stress
groups = [g["stress_level"].values for _, g in df.groupby("usage_group", observed=True)]
F, p_anova = stats.f_oneway(*groups)
anova = pd.DataFrame([{"test": "one-way ANOVA: stress ~ usage_group(Low/Med/High)",
                       "F": round(float(F), 3), "p_value": float(f"{p_anova:.3e}"),
                       "k_groups": len(groups)}])
utils.save_table(anova, "anova_stress_by_usage.csv")
print(f"\n[03] ANOVA stress ~ usage group: F = {F:.3f}, p = {p_anova:.3e}")

# --- comparison figures --------------------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.2))
sns.boxplot(data=df, x="high_low_usage", y="stress_level", order=["Low", "High"],
            hue="high_low_usage", palette=[utils.PALETTE[2], utils.PALETTE[1]],
            legend=False, ax=ax)
ax.set_xlabel("Usage group (median split)")
ax.set_ylabel(config.LABELS["stress_level"])
ax.set_title("Stress: high vs low social-media users")
utils.save_fig(fig, "fig_box_stress_high_low.png")

sub = df[df["primary_platform"].isin(["TikTok", "Instagram"])]
fig, ax = plt.subplots(figsize=(6.2, 4.2))
sns.boxplot(data=sub, x="primary_platform", y="stress_level",
            order=["TikTok", "Instagram"], hue="primary_platform",
            palette=[utils.PALETTE[0], utils.PALETTE[3]], legend=False, ax=ax)
ax.set_xlabel("Primary platform")
ax.set_ylabel(config.LABELS["stress_level"])
ax.set_title("Stress: TikTok vs Instagram users")
utils.save_fig(fig, "fig_box_stress_tiktok_instagram.png")
print("[03] Statistical-analysis figures saved.")
