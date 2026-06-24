"""
00_generate_data.py  -  Phase 0 (data source)

Generates a SYNTHETIC adolescent survey dataset with a documented
data-generating process (DGP). This exists so the entire pipeline is runnable
end-to-end without external data.

  >>> THE DATA ARE SIMULATED, NOT REAL ADOLESCENTS. <<<

To run the study on real data, replace this step: produce a CSV at
config.RAW_CSV with the same column names (see config.py) and skip 00.

Built-in structure (so the downstream statistics recover real signal):
  social media hours  -> less sleep, less activity, less in-person interaction
  less sleep          -> more stress           (mediation path)
  more social media   -> more stress directly  (direct path)
  more stress / less sleep -> lower GPA
"""
import numpy as np
import pandas as pd

import config

rng = np.random.default_rng(config.RANDOM_SEED)
n = config.N_STUDENTS


def clip(a, lo, hi):
    return np.clip(a, lo, hi)


# --- demographics --------------------------------------------------------
age = rng.integers(13, 19, size=n)                       # 13-18 inclusive
gender = rng.choice(["Female", "Male", "Non-binary"], size=n, p=[0.49, 0.49, 0.02])
platform = rng.choice(
    ["TikTok", "Instagram", "Snapchat", "YouTube", "Other"],
    size=n, p=[0.30, 0.28, 0.18, 0.16, 0.08],
)
platform_boost = pd.Series(platform).map(
    {"TikTok": 0.6, "Instagram": 0.2, "Snapchat": 0.1, "YouTube": 0.0, "Other": -0.2}
).values

# --- behaviors (order respects causal dependencies) ----------------------
sm_hours = clip(rng.normal(3.0 + platform_boost + 0.08 * (age - 13), 1.4), 0.2, 9.0)
activity = clip(rng.normal(5.0 - 0.20 * sm_hours, 2.5), 0.0, 18.0)
screen_before = clip(20 + 14 * sm_hours + rng.normal(0, 25, n), 0, 180)
sleep = clip(
    9.2 - 0.28 * sm_hours - 0.010 * screen_before + 0.03 * activity + rng.normal(0, 0.6, n),
    4.0, 10.0,
)
social = clip(6.8 - 0.30 * sm_hours + rng.normal(0, 1.6, n), 1.0, 10.0)

# --- outcomes ------------------------------------------------------------
stress = clip(
    5.0
    + 0.45 * (sm_hours - 3.0)        # direct effect of social media
    - 0.55 * (sleep - 7.0)           # mediator: sleep
    - 0.12 * (activity - 5.0)
    - 0.18 * (social - 6.0)
    + rng.normal(0, 1.1, n),
    0.0, 10.0,
)
gpa = clip(
    3.30
    - 0.18 * (stress - 5.0)
    + 0.15 * (sleep - 7.0)
    - 0.05 * (sm_hours - 3.0)
    + 0.04 * (activity - 5.0)
    + rng.normal(0, 0.35, n),
    0.0, 4.0,
)

df = pd.DataFrame({
    "student_id": [f"S{1000 + i}" for i in range(n)],
    "age": age,
    "gender": gender,
    "primary_platform": platform,
    "daily_social_media_hours": np.round(sm_hours, 2),
    "screen_time_before_sleep_min": np.round(screen_before).astype(int),
    "sleep_hours": np.round(sleep, 1),
    "physical_activity_hrs_week": np.round(activity, 1),
    "social_interaction_level": np.round(social, 1),
    "stress_level": np.round(stress, 2),
    "academic_performance": np.round(gpa, 2),
})

# --- inject realistic missingness into a few predictor columns -----------
for col, frac in [
    ("screen_time_before_sleep_min", 0.03),
    ("sleep_hours", 0.04),
    ("physical_activity_hrs_week", 0.03),
    ("social_interaction_level", 0.03),
]:
    miss_idx = rng.choice(n, size=int(frac * n), replace=False)
    df.loc[miss_idx, col] = np.nan

df.to_csv(config.RAW_CSV, index=False)
print(f"[00] Generated SYNTHETIC raw data: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"     -> {config.RAW_CSV}")
print(f"     missing cells: {int(df.isna().sum().sum())}")
