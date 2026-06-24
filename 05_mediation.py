"""
05_mediation.py  -  Phase 5: Mediation Analysis

Question: does SLEEP mediate the relationship between social-media use and
stress?  i.e.  social media -> less sleep -> more stress.

Standard 3-equation decomposition (X = social media, M = sleep, Y = stress):
    a  :  M ~ X
    b  :  Y ~ X + M      (coefficient on M)
    c' :  Y ~ X + M      (coefficient on X = direct effect)
    c  :  Y ~ X          (total effect)
    indirect (mediated) effect = a * b   (should equal c - c')

Inference on the indirect effect uses nonparametric bootstrap (the modern
standard; the sampling distribution of a*b is non-normal), supplemented with
the classic Sobel test.
"""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import config
import utils
import ols

utils.set_style()
df = pd.read_csv(config.CLEAN_CSV)

X, M, Y = "daily_social_media_hours", "sleep_hours", "stress_level"
d = df[[X, M, Y]].dropna().copy()

# --- path estimates ------------------------------------------------------
a_res = ols.fit_ols(d, M, [X])
a = a_res.beta[a_res.names.index(X)]
se_a = a_res.se[a_res.names.index(X)]

bc_res = ols.fit_ols(d, Y, [X, M])
b = bc_res.beta[bc_res.names.index(M)]
se_b = bc_res.se[bc_res.names.index(M)]
c_prime = bc_res.beta[bc_res.names.index(X)]

c_res = ols.fit_ols(d, Y, [X])
c = c_res.beta[c_res.names.index(X)]

indirect = a * b
prop_mediated = indirect / c if c != 0 else np.nan

# --- bootstrap the indirect effect --------------------------------------
rng = np.random.default_rng(config.RANDOM_SEED)
xv, mv, yv = d[X].values, d[M].values, d[Y].values
n = len(d)
boot = np.empty(config.N_BOOTSTRAP)
for i in range(config.N_BOOTSTRAP):
    idx = rng.integers(0, n, n)
    xb, mb, yb = xv[idx], mv[idx], yv[idx]
    Xa = np.column_stack([np.ones(n), xb])
    a_i = np.linalg.lstsq(Xa, mb, rcond=None)[0][1]
    Xb = np.column_stack([np.ones(n), xb, mb])
    b_i = np.linalg.lstsq(Xb, yb, rcond=None)[0][2]
    boot[i] = a_i * b_i
ci_low, ci_high = np.percentile(boot, [2.5, 97.5])

# --- Sobel test ----------------------------------------------------------
sobel_z = indirect / np.sqrt(b**2 * se_a**2 + a**2 * se_b**2)
sobel_p = 2 * stats.norm.sf(abs(sobel_z))

results = pd.DataFrame([{
    "a (X->M)": round(a, 4),
    "b (M->Y|X)": round(b, 4),
    "c_total (X->Y)": round(c, 4),
    "c_prime_direct (X->Y|M)": round(c_prime, 4),
    "indirect (a*b)": round(indirect, 4),
    "boot_ci95_low": round(ci_low, 4),
    "boot_ci95_high": round(ci_high, 4),
    "prop_mediated": round(prop_mediated, 4),
    "sobel_z": round(sobel_z, 3),
    "sobel_p": float(f"{sobel_p:.3e}"),
    "n": n,
}])
utils.save_table(results, "mediation_results.csv")

sig = "significant (CI excludes 0)" if (ci_low > 0 or ci_high < 0) else "not significant"
txt = (
    "MEDIATION: social media (X) -> sleep (M) -> stress (Y)\n"
    "=======================================================\n"
    f"a  (X -> M)                : {a:+.4f}\n"
    f"b  (M -> Y | X)            : {b:+.4f}\n"
    f"c  total  (X -> Y)         : {c:+.4f}\n"
    f"c' direct (X -> Y | M)     : {c_prime:+.4f}\n"
    f"indirect effect (a*b)      : {indirect:+.4f}\n"
    f"  bootstrap 95% CI         : [{ci_low:+.4f}, {ci_high:+.4f}]  -> {sig}\n"
    f"  Sobel z                  : {sobel_z:.3f}  (p = {sobel_p:.3e})\n"
    f"proportion mediated        : {prop_mediated:.1%}\n"
    f"n                          : {n}   bootstrap draws: {config.N_BOOTSTRAP}\n\n"
    "Interpretation: a*b captures how much of social media's association with\n"
    "stress runs THROUGH reduced sleep; c' is the remaining direct association.\n"
)
utils.save_text(txt, "mediation_results.txt")
print("[05] Mediation results:\n" + txt)

# --- path diagram --------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.2, 4.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
nodes = {"X": (1.4, 1.4, "Social media\n(hrs/day)"),
         "M": (5.0, 4.3, "Sleep\n(hrs/night)"),
         "Y": (8.6, 1.4, "Stress\n(0-10)")}
for key, (x, y, lab) in nodes.items():
    ax.add_patch(FancyBboxPatch((x - 1.1, y - 0.55), 2.2, 1.1,
                 boxstyle="round,pad=0.08", fc=utils.PALETTE[0],
                 ec="#1c4a63", alpha=0.9))
    ax.text(x, y, lab, ha="center", va="center", color="white",
            fontsize=11, fontweight="bold")


def arrow(p1, p2, label, dx=0, dy=0.35):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=18,
                 lw=2, color="#444", shrinkA=38, shrinkB=38))
    mx, my = (p1[0] + p2[0]) / 2 + dx, (p1[1] + p2[1]) / 2 + dy
    ax.text(mx, my, label, ha="center", va="center", fontsize=10,
            fontweight="bold", color=utils.PALETTE[1],
            bbox=dict(fc="white", ec="none", alpha=0.85))


arrow(nodes["X"][:2], nodes["M"][:2], f"a = {a:+.2f}", dx=-0.6, dy=0.3)
arrow(nodes["M"][:2], nodes["Y"][:2], f"b = {b:+.2f}", dx=0.6, dy=0.3)
arrow(nodes["X"][:2], nodes["Y"][:2],
      f"c = {c:+.2f}  (direct c' = {c_prime:+.2f})", dy=-0.45)
ax.text(5.0, 0.35, f"indirect a*b = {indirect:+.3f}   "
        f"[boot 95% CI {ci_low:+.2f}, {ci_high:+.2f}]   "
        f"proportion mediated = {prop_mediated:.0%}",
        ha="center", fontsize=10, style="italic")
ax.set_title("Sleep as a mediator of social media -> stress", fontweight="bold")
utils.save_fig(fig, "fig_mediation_path_diagram.png")

# --- bootstrap distribution ---------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.hist(boot, bins=40, color=utils.PALETTE[0], alpha=0.85)
ax.axvline(0, color="#444", ls="--", lw=1.5, label="no mediation")
ax.axvline(ci_low, color=utils.PALETTE[1], ls=":", lw=2)
ax.axvline(ci_high, color=utils.PALETTE[1], ls=":", lw=2, label="95% CI")
ax.axvline(indirect, color=utils.PALETTE[2], lw=2.4, label="point estimate")
ax.set_xlabel("Bootstrapped indirect effect (a*b)")
ax.set_ylabel("Frequency")
ax.set_title("Bootstrap distribution of the mediated effect")
ax.legend()
utils.save_fig(fig, "fig_mediation_bootstrap.png")
print("[05] Mediation figures saved.")
