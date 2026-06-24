"""
01_clean.py  -  Phase 1: Data Cleaning

  * report and handle missing values (median for numeric, mode for categorical)
  * encode gender / primary platform (integer codes for storage; dummy coding
    is done later, inside the regression, which is correct for nominal vars)
  * normalize scale variables (z-scores -> *_z columns)
  * derive usage groups (tertiles + median split) for group comparisons

Output: outputs/data/clean_teen_mental_health.csv  (DERI added later in Phase 6)
"""
import numpy as np
import pandas as pd

import config
import utils

df = pd.read_csv(config.RAW_CSV)
print(f"[01] Loaded raw: {df.shape}")

# --- 1. missing-value report --------------------------------------------
miss = pd.DataFrame({
    "n_missing": df.isna().sum(),
    "pct_missing": (df.isna().mean() * 100).round(2),
})
miss = miss[miss["n_missing"] > 0].sort_values("n_missing", ascending=False)
utils.save_table(miss.reset_index().rename(columns={"index": "column"}),
                 "missing_report.csv")
print("     missing columns:\n", miss.to_string() if len(miss) else "     none")

# --- 2. imputation -------------------------------------------------------
num_cols = df.select_dtypes(include="number").columns
cat_cols = df.select_dtypes(exclude="number").columns.drop(config.ID_COL)

for c in num_cols:
    if df[c].isna().any():
        df[c] = df[c].fillna(df[c].median())
for c in cat_cols:
    if df[c].isna().any():
        df[c] = df[c].fillna(df[c].mode().iloc[0])
assert df.isna().sum().sum() == 0, "missing values remain after imputation"

# --- 3. encode categoricals (integer codes for reference/storage) --------
for c in config.CATEGORICAL:
    df[c + "_code"] = pd.Categorical(df[c]).codes

# --- 4. normalize scale variables (z-scores, population sd) --------------
for c in config.SCALE_TO_NORMALIZE:
    mu, sd = df[c].mean(), df[c].std(ddof=0)
    df[c + "_z"] = (df[c] - mu) / sd

# --- 5. usage groups -----------------------------------------------------
df["usage_group"] = pd.qcut(
    df["daily_social_media_hours"], 3, labels=["Low", "Medium", "High"]
)
df["usage_group"] = pd.Categorical(
    df["usage_group"], categories=["Low", "Medium", "High"], ordered=True
)
median_sm = df["daily_social_media_hours"].median()
df["high_low_usage"] = np.where(
    df["daily_social_media_hours"] >= median_sm, "High", "Low"
)

df.to_csv(config.CLEAN_CSV, index=False)
print(f"[01] Clean dataset written: {df.shape} -> {config.CLEAN_CSV}")
print(f"     usage_group counts: {df['usage_group'].value_counts().to_dict()}")
