"""
ols.py
Ordinary Least Squares with full classical inference, implemented from
scratch with NumPy/SciPy (no statsmodels dependency).

This keeps the regression mathematics transparent, which suits a quantitative
social-science / applied-statistics project: every standard error, t-statistic
and p-value below comes from the closed-form OLS estimator, not a black box.

    beta_hat   = (X'X)^-1 X'y
    resid      = y - X beta_hat
    sigma^2    = RSS / (n - k)              (unbiased error variance)
    Var(beta)  = sigma^2 (X'X)^-1
    t_j        = beta_j / SE_j   ~ t(n - k)
"""
import numpy as np
import pandas as pd
from scipy import stats


class OLSResults:
    """Fit OLS on a numeric design matrix X (intercept already included)."""

    def __init__(self, y, X, names, dependent="y"):
        self.names = list(names)
        self.dependent = dependent
        self.y = np.asarray(y, dtype=float)
        self.X = np.asarray(X, dtype=float)
        self.n, self.k = self.X.shape          # k includes the intercept

        XtX = self.X.T @ self.X
        self.XtX_inv = np.linalg.pinv(XtX)     # pinv for numerical safety
        self.beta = self.XtX_inv @ self.X.T @ self.y
        self.fitted = self.X @ self.beta
        self.resid = self.y - self.fitted

        self.dof = self.n - self.k
        self.rss = float(self.resid @ self.resid)
        self.sigma2 = self.rss / self.dof
        self.cov_beta = self.sigma2 * self.XtX_inv
        self.se = np.sqrt(np.diag(self.cov_beta))

        self.tvalues = self.beta / self.se
        self.pvalues = 2 * stats.t.sf(np.abs(self.tvalues), self.dof)
        tcrit = stats.t.ppf(0.975, self.dof)
        self.ci_low = self.beta - tcrit * self.se
        self.ci_high = self.beta + tcrit * self.se

        ybar = self.y.mean()
        self.tss = float(((self.y - ybar) ** 2).sum())
        self.r2 = 1 - self.rss / self.tss
        self.adj_r2 = 1 - (1 - self.r2) * (self.n - 1) / (self.n - self.k)

        p = self.k - 1                          # predictors excluding intercept
        self.fvalue = ((self.tss - self.rss) / p) / (self.rss / self.dof)
        self.f_pvalue = stats.f.sf(self.fvalue, p, self.dof)

        # Standardized (beta) coefficients: beta_j * sd(x_j) / sd(y)
        sy = self.y.std(ddof=1)
        self.std_beta = np.full(self.k, np.nan)
        for j in range(self.k):
            if self.names[j] == "const":
                continue
            sx = self.X[:, j].std(ddof=1)
            self.std_beta[j] = self.beta[j] * sx / sy if sy > 0 else np.nan

    # ------------------------------------------------------------------
    def summary_frame(self):
        return pd.DataFrame({
            "term": self.names,
            "coef": self.beta,
            "std_err": self.se,
            "t": self.tvalues,
            "p_value": self.pvalues,
            "ci_2.5%": self.ci_low,
            "ci_97.5%": self.ci_high,
            "std_beta": self.std_beta,
        })

    def summary_text(self):
        L = []
        L.append(f"OLS Regression  -  dependent variable: {self.dependent}")
        L.append("=" * 78)
        L.append(f"N = {self.n}    df(resid) = {self.dof}    parameters = {self.k}")
        L.append(f"R-squared = {self.r2:.4f}      Adj. R-squared = {self.adj_r2:.4f}")
        L.append(f"F({self.k - 1}, {self.dof}) = {self.fvalue:.3f}      "
                 f"Prob(F) = {self.f_pvalue:.3e}")
        L.append("-" * 78)
        L.append(f"{'term':30s}{'coef':>9s}{'std_err':>9s}{'t':>8s}"
                 f"{'p':>11s}{'std_beta':>10s}")
        L.append("-" * 78)
        for j, nm in enumerate(self.names):
            sb = "" if np.isnan(self.std_beta[j]) else f"{self.std_beta[j]:>10.3f}"
            star = ""
            if self.pvalues[j] < 0.001:
                star = " ***"
            elif self.pvalues[j] < 0.01:
                star = " **"
            elif self.pvalues[j] < 0.05:
                star = " *"
            L.append(f"{nm:30s}{self.beta[j]:>9.4f}{self.se[j]:>9.4f}"
                     f"{self.tvalues[j]:>8.3f}{self.pvalues[j]:>11.3e}{sb}{star}")
        L.append("=" * 78)
        L.append("Signif. codes:  *** p<0.001   ** p<0.01   * p<0.05")
        return "\n".join(L)


def fit_ols(df, y_col, x_cols):
    """Fit OLS of y_col on x_cols (numeric, intercept added automatically)."""
    d = df[[y_col] + list(x_cols)].dropna().copy()
    y = d[y_col].values
    X = np.column_stack([np.ones(len(d))] + [d[c].values for c in x_cols])
    names = ["const"] + list(x_cols)
    return OLSResults(y, X, names, dependent=y_col)


def vif_table(df, x_cols):
    """Variance inflation factors: VIF_j = 1 / (1 - R^2_j) where R^2_j comes
    from regressing predictor j on all the other predictors."""
    d = df[list(x_cols)].dropna().copy()
    rows = []
    for col in x_cols:
        others = [c for c in x_cols if c != col]
        y = d[col].values
        if not others:
            rows.append({"term": col, "VIF": 1.0, "R2_on_others": 0.0})
            continue
        X = np.column_stack([np.ones(len(d))] + [d[c].values for c in others])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred = X @ beta
        ss_res = float(((y - pred) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        vif = np.inf if r2 >= 1 else 1.0 / (1.0 - r2)
        rows.append({"term": col, "VIF": vif, "R2_on_others": r2})
    return pd.DataFrame(rows)
