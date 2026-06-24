# Digital Behavior & Adolescent Mental Health — Analysis Pipeline

A reproducible quantitative-social-science pipeline relating adolescent digital
behavior to stress and academic performance: cleaning → descriptives →
correlation/group tests → OLS regression → mediation → a composite risk index.
Applied statistics (not ML): regression inference is computed in closed form.

> ⚠️ **The bundled dataset is SYNTHETIC.** `00_generate_data.py` simulates 1,200
> students from a documented data-generating process so the pipeline runs
> end-to-end with no restricted data. Replace it with a real survey before
> reporting any findings (see *Using your own data*).

## Quick start

```bash
pip install -r requirements.txt
python run_all.py            # runs phases 00–07 in order
```

Everything lands in `outputs/`:
- `outputs/data/clean_teen_mental_health.csv` — cleaned, encoded, z-scored, DERI-scored
- `outputs/figures/` — all 18 plots (the "visualizations" deliverable)
- `outputs/results/` — every table + `SUMMARY_FOR_REPORT.md`
- `RESEARCH_BRIEF.md` — the 1–2 page write-up

## Using your own data

Skip phase 00. Provide a CSV at `outputs/data/raw_teen_mental_health.csv` with
these columns (see `config.py`):

`student_id, age, gender, primary_platform, daily_social_media_hours,
screen_time_before_sleep_min, sleep_hours, physical_activity_hrs_week,
social_interaction_level, stress_level, academic_performance`

Then run `python run_all.py` starting from `01_clean.py`. If your column names
differ, edit the names in `config.py` only — the rest of the pipeline reads from
there.

## File map

| File | Phase | Does |
|---|---|---|
| `config.py` | — | Paths, column groups, constants (single source of truth) |
| `utils.py` | — | Plot style, save helpers, encoding, design-matrix builder |
| `ols.py` | — | OLS with full inference (SE/t/p/CI/R²/F) + VIF, from scratch |
| `00_generate_data.py` | 0 | Simulate the (synthetic) raw dataset |
| `01_clean.py` | 1 | Missing-value report, imputation, encoding, normalization, usage groups |
| `02_descriptive.py` | 2 | Outcomes by usage group; boxplots, scatter, histogram |
| `03_statistics.py` | 3 | Correlation matrix + heatmap; Welch t-tests; ANOVA |
| `04_regression.py` | 4 | Stress & GPA OLS models; VIF; forest plots; diagnostics; effect plot |
| `05_mediation.py` | 5 | Sleep mediation of social media → stress; bootstrap CI; path diagram |
| `06_deri.py` | 6 | Digital Exposure Risk Index (+ PCA validation); outcome correlations |
| `07_summary_for_report.py` | 7 | Collates all results into `SUMMARY_FOR_REPORT.md` |
| `run_all.py` | — | Runs the whole pipeline |

## Method notes

- **Regression inference** uses the closed-form OLS estimator
  `β = (XʹX)⁻¹Xʹy` with `Var(β) = σ²(XʹX)⁻¹`; coefficients validated against
  scikit-learn to ~1e-12. Nominal predictors use reference (dummy) coding.
- **Mediation** uses the standard a/b/c/c′ decomposition; the indirect effect
  `a·b` is tested with a 5,000-draw nonparametric bootstrap (percentile CI),
  plus a Sobel test. Estimated on cross-sectional data → interpret as a modeled
  pathway, not proven causation.
- **DERI** is an equal-weight z-score composite of social-media hours, pre-sleep
  screen time, and inverted sleep duration, rescaled to 0–100; a PCA weighting
  is reported as a robustness check.
