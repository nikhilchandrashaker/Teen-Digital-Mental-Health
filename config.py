"""
config.py
Central configuration for the Teen Digital Behavior & Mental Health study.

All paths are derived from this file's location, so the project folder is
portable: drop it anywhere and outputs land in ./outputs.
"""
import os

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")

RAW_CSV = os.path.join(DATA_DIR, "raw_teen_mental_health.csv")
CLEAN_CSV = os.path.join(DATA_DIR, "clean_teen_mental_health.csv")

for _d in (OUTPUT_DIR, DATA_DIR, FIG_DIR, RESULTS_DIR):
    os.makedirs(_d, exist_ok=True)

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------
RANDOM_SEED = 42
N_STUDENTS = 1200
N_BOOTSTRAP = 5000

# --------------------------------------------------------------------------
# Column definitions
# --------------------------------------------------------------------------
ID_COL = "student_id"

# Self-reported outcome variables
OUTCOMES = ["stress_level", "academic_performance"]

# Behavioral predictors used in the regression / mediation models
PREDICTORS = [
    "daily_social_media_hours",
    "sleep_hours",
    "screen_time_before_sleep_min",
    "physical_activity_hrs_week",
    "social_interaction_level",
]

# Demographic / contextual controls
CONTROLS = ["age", "gender", "primary_platform"]

# Nominal categorical variables (one-hot encoded at modeling time)
CATEGORICAL = ["gender", "primary_platform"]

# Continuous variables (for correlation matrix, describe(), etc.)
CONTINUOUS = PREDICTORS + ["age"] + OUTCOMES

# Scale variables standardized (z-scored) during cleaning
SCALE_TO_NORMALIZE = PREDICTORS + OUTCOMES

# --------------------------------------------------------------------------
# Digital Exposure Risk Index (DERI) components
#   positive components -> higher value = higher risk
#   negative components -> lower value  = higher risk (orientation flipped)
# --------------------------------------------------------------------------
DERI_POSITIVE = ["daily_social_media_hours", "screen_time_before_sleep_min"]
DERI_NEGATIVE = ["sleep_hours"]

# --------------------------------------------------------------------------
# Human-readable labels for plots / reports
# --------------------------------------------------------------------------
LABELS = {
    "daily_social_media_hours": "Daily social media (hrs)",
    "sleep_hours": "Sleep (hrs/night)",
    "screen_time_before_sleep_min": "Screen time before sleep (min)",
    "physical_activity_hrs_week": "Physical activity (hrs/wk)",
    "social_interaction_level": "In-person social interaction (1-10)",
    "stress_level": "Stress level (0-10)",
    "academic_performance": "Academic performance (GPA)",
    "age": "Age",
    "deri_score": "Digital Exposure Risk Index (0-100)",
    "deri_z": "DERI (standardized)",
}
