"""
02_descriptive.py  -  Phase 2: Descriptive Social Science

Answers, descriptively:
  Q1. Do heavier social-media users sleep less?
  Q2. Do they report higher stress?
  Q3. Is academic performance lower?

Visuals: boxplots (sleep / stress / GPA by usage group), scatter (sleep vs
usage), histogram (stress distribution).
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import config
import utils

utils.set_style()
df = pd.read_csv(config.CLEAN_CSV)
order = ["Low", "Medium", "High"]

# --- group means table ---------------------------------------------------
g = df.groupby("usage_group", observed=True)
summary = pd.DataFrame({
    "n": g.size(),
    "mean_social_media_hrs": g["daily_social_media_hours"].mean(),
    "mean_sleep_hrs": g["sleep_hours"].mean(),
    "mean_stress": g["stress_level"].mean(),
    "mean_gpa": g["academic_performance"].mean(),
}).round(3).reindex(order)
utils.save_table(summary.reset_index(), "group_means.csv")
print("[02] Mean outcomes by social-media usage group:\n", summary.to_string())

lo, hi = summary.loc["Low"], summary.loc["High"]
print("\n     Descriptive read:")
print(f"     Q1 sleep : Low={lo.mean_sleep_hrs:.2f}h  High={hi.mean_sleep_hrs:.2f}h"
      f"  (High - Low = {hi.mean_sleep_hrs - lo.mean_sleep_hrs:+.2f}h)")
print(f"     Q2 stress: Low={lo.mean_stress:.2f}   High={hi.mean_stress:.2f}"
      f"   (High - Low = {hi.mean_stress - lo.mean_stress:+.2f})")
print(f"     Q3 GPA   : Low={lo.mean_gpa:.2f}    High={hi.mean_gpa:.2f}"
      f"    (High - Low = {hi.mean_gpa - lo.mean_gpa:+.2f})")

# --- boxplots ------------------------------------------------------------
for var, fname in [
    ("sleep_hours", "fig_box_sleep_by_usage.png"),
    ("stress_level", "fig_box_stress_by_usage.png"),
    ("academic_performance", "fig_box_gpa_by_usage.png"),
]:
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    sns.boxplot(data=df, x="usage_group", y=var, order=order,
                hue="usage_group", palette=utils.PALETTE[:3], legend=False, ax=ax)
    ax.set_xlabel("Social-media usage group")
    ax.set_ylabel(config.LABELS[var])
    ax.set_title(f"{config.LABELS[var]} by usage group")
    utils.save_fig(fig, fname)

# --- scatter: sleep vs social-media hours --------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.4))
sns.regplot(data=df, x="daily_social_media_hours", y="sleep_hours",
            scatter_kws={"alpha": 0.22, "s": 14, "color": utils.PALETTE[0]},
            line_kws={"color": utils.PALETTE[1], "lw": 2.2}, ax=ax)
ax.set_xlabel(config.LABELS["daily_social_media_hours"])
ax.set_ylabel(config.LABELS["sleep_hours"])
ax.set_title("Sleep vs daily social-media use")
utils.save_fig(fig, "fig_scatter_sleep_vs_usage.png")

# --- histogram: stress distribution --------------------------------------
fig, ax = plt.subplots(figsize=(6.2, 4.2))
sns.histplot(df["stress_level"], bins=24, kde=True,
             color=utils.PALETTE[0], ax=ax)
ax.axvline(df["stress_level"].mean(), color=utils.PALETTE[1], ls="--", lw=2,
           label=f"mean = {df['stress_level'].mean():.2f}")
ax.set_xlabel(config.LABELS["stress_level"])
ax.set_title("Distribution of reported stress")
ax.legend()
utils.save_fig(fig, "fig_hist_stress.png")
print("[02] Descriptive figures saved.")
