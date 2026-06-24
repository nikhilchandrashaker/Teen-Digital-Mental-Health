"""
04_regression.py  -  Phase 4: Regression Models (core deliverable)

Two OLS models, fit with the from-scratch estimator in ols.py:

  stress_level         ~ behaviors + demographic controls
  academic_performance ~ behaviors + demographic controls

Behaviors: daily social-media hours, sleep, screen-time-before-sleep,
physical activity, in-person social interaction.
Controls : age, gender (dummy), primary platform (dummy).

Outputs per model: coefficient table (coef, SE, t, p, 95% CI, standardized
beta), text summary, VIF table, a coefficient forest plot, residual
diagnostics, and a marginal-effect plot for social-media hours.
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

import config
import utils
import ols

utils.set_style()
df = pd.read_csv(config.CLEAN_CSV)

# Build numeric modeling frame (continuous predictors + dummies)
continuous = config.PREDICTORS + ["age"]
model_df, x_cols = utils.build_model_frame(df, continuous, config.CATEGORICAL)


def nice(term):
    return config.LABELS.get(term, term.replace("_", " "))


def coef_forest(res, fname, title):
    """Forest plot of raw coefficients (excluding intercept) with 95% CI."""
    sf = res.summary_frame()
    sf = sf[sf["term"] != "const"].copy()
    sf = sf.iloc[::-1]  # so first predictor sits on top
    fig, ax = plt.subplots(figsize=(7.2, 0.5 * len(sf) + 1.5))
    y = np.arange(len(sf))
    err = [sf["coef"] - sf["ci_2.5%"], sf["ci_97.5%"] - sf["coef"]]
    colors = [utils.PALETTE[1] if p < 0.05 else "#9aa0a6"
              for p in sf["p_value"]]
    ax.errorbar(sf["coef"], y, xerr=err, fmt="none", ecolor="#888", capsize=3, zorder=1)
    ax.scatter(sf["coef"], y, c=colors, s=55, zorder=2, edgecolor="white")
    ax.axvline(0, color="#444", lw=1, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([nice(t) for t in sf["term"]])
    ax.set_xlabel("Coefficient (unstandardized) with 95% CI")
    ax.set_title(title)
    utils.save_fig(fig, fname)


def run_model(y_col, tag, title):
    res = ols.fit_ols(model_df, y_col, x_cols)
    sf = res.summary_frame().round(4)
    utils.save_table(sf, f"regression_{tag}_coefficients.csv")
    utils.save_text(res.summary_text(), f"regression_{tag}_summary.txt")
    coef_forest(res, f"fig_regression_{tag}_coefficients.png", title)
    print(f"\n[04] {y_col}:  R^2 = {res.r2:.3f}  Adj R^2 = {res.adj_r2:.3f}  "
          f"F = {res.fvalue:.1f} (p = {res.f_pvalue:.2e})")
    show = sf[sf["term"].isin(config.PREDICTORS)][
        ["term", "coef", "std_err", "p_value", "std_beta"]]
    print(show.to_string(index=False))
    return res


res_stress = run_model("stress_level", "stress",
                       "Predictors of stress (OLS, 95% CI)")
res_gpa = run_model("academic_performance", "academic",
                    "Predictors of academic performance (OLS, 95% CI)")

# --- multicollinearity check (continuous predictors) ---------------------
vif = ols.vif_table(model_df, continuous).round(3)
utils.save_table(vif, "regression_vif.csv")
print("\n[04] VIF (variance inflation factors):\n", vif.to_string(index=False))

# --- residual diagnostics for the stress model ---------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
axes[0].scatter(res_stress.fitted, res_stress.resid, alpha=0.25, s=14,
                color=utils.PALETTE[0])
axes[0].axhline(0, color=utils.PALETTE[1], lw=1.6)
axes[0].set_xlabel("Fitted values"); axes[0].set_ylabel("Residuals")
axes[0].set_title("Residuals vs fitted")
stats.probplot(res_stress.resid, dist="norm", plot=axes[1])
axes[1].set_title("Normal Q-Q plot of residuals")
axes[1].get_lines()[0].set_color(utils.PALETTE[0])
axes[1].get_lines()[0].set_alpha(0.4)
axes[1].get_lines()[1].set_color(utils.PALETTE[1])
utils.save_fig(fig, "fig_regression_stress_diagnostics.png")

# --- marginal effect of social-media hours on stress --------------------
# Predict stress across the SM-hours range, holding other continuous
# predictors at their means and dummies at their reference (0) level.
names, beta = res_stress.names, res_stress.beta
base = {nm: (model_df[nm].mean() if nm in model_df.columns else 0.0)
        for nm in names}
base["const"] = 1.0
grid = np.linspace(model_df["daily_social_media_hours"].min(),
                   model_df["daily_social_media_hours"].max(), 60)
preds = []
for v in grid:
    row = dict(base); row["daily_social_media_hours"] = v
    preds.append(sum(beta[i] * row[nm] for i, nm in enumerate(names)))
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.scatter(df["daily_social_media_hours"], df["stress_level"], alpha=0.18, s=14,
           color=utils.PALETTE[0], label="observed")
ax.plot(grid, preds, color=utils.PALETTE[1], lw=2.6,
        label="model (others at mean)")
ax.set_xlabel(config.LABELS["daily_social_media_hours"])
ax.set_ylabel(config.LABELS["stress_level"])
ax.set_title("Adjusted effect of social-media use on stress")
ax.legend()
utils.save_fig(fig, "fig_effect_socialmedia_on_stress.png")
print("[04] Regression figures + diagnostics saved.")
