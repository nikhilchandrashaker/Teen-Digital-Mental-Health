# Results summary — for the research brief
*All figures are in `outputs/figures/`. Numbers below are produced by the pipeline; data are SIMULATED (see README).*

## Descriptive: outcomes by usage group
| usage_group   |   n |   mean_social_media_hrs |   mean_sleep_hrs |   mean_stress |   mean_gpa |
|:--------------|----:|------------------------:|-----------------:|--------------:|-----------:|
| Low           | 404 |                   1.946 |            8.267 |         3.831 |      3.632 |
| Medium        | 398 |                   3.455 |            7.618 |         4.924 |      3.357 |
| High          | 398 |                   4.993 |            7.049 |         6.01  |      2.963 |

## Key correlations (Pearson)
- **daily_social_media_hours** vs **stress_level**: r = +0.608
- **sleep_hours** vs **stress_level**: r = -0.575
- **sleep_hours** vs **academic_performance**: r = +0.584
- **daily_social_media_hours** vs **sleep_hours**: r = -0.652
- **daily_social_media_hours** vs **academic_performance**: r = -0.587

## Group comparisons (Welch t-tests)
| comparison                                    |   group1_mean |   group2_mean |   mean_diff |   ci95_low |   ci95_high |       t |     df |   p_value |   cohens_d |   n1 |   n2 |
|:----------------------------------------------|--------------:|--------------:|------------:|-----------:|------------:|--------:|-------:|----------:|-----------:|-----:|-----:|
| High vs Low usage: stress_level               |         5.725 |         4.106 |       1.619 |      1.46  |       1.778 |  19.998 | 1194.8 | 5.683e-77 |      1.154 |  601 |  599 |
| High vs Low usage: sleep_hours                |         7.2   |         8.097 |      -0.896 |     -0.979 |      -0.814 | -21.34  | 1195.6 | 7.132e-86 |     -1.232 |  601 |  599 |
| High vs Low usage: academic_performance       |         3.076 |         3.563 |      -0.486 |     -0.539 |      -0.433 | -17.946 | 1139.1 | 1.294e-63 |     -1.036 |  601 |  599 |
| TikTok vs Instagram: daily_social_media_hours |         3.843 |         3.359 |       0.484 |      0.278 |       0.69  |   4.617 |  704.8 | 4.618e-06 |      0.347 |  370 |  339 |
| TikTok vs Instagram: stress_level             |         5.164 |         4.773 |       0.391 |      0.152 |       0.631 |   3.21  |  700.8 | 0.001389  |      0.241 |  370 |  339 |

## Regression — Stress model (key predictors)
| term                         |    coef |   std_err |   p_value |   std_beta |
|:-----------------------------|--------:|----------:|----------:|-----------:|
| daily_social_media_hours     |  0.4246 |    0.0345 |    0      |     0.3662 |
| sleep_hours                  | -0.5262 |    0.057  |    0      |    -0.2776 |
| screen_time_before_sleep_min |  0.0001 |    0.0015 |    0.9656 |     0.0012 |
| physical_activity_hrs_week   | -0.1336 |    0.0143 |    0      |    -0.1985 |
| social_interaction_level     | -0.1529 |    0.0217 |    0      |    -0.1513 |

## Regression — Academic-performance model (key predictors)
| term                         |    coef |   std_err |   p_value |   std_beta |
|:-----------------------------|--------:|----------:|----------:|-----------:|
| daily_social_media_hours     | -0.1299 |    0.0112 |    0      |    -0.3433 |
| sleep_hours                  |  0.1887 |    0.0185 |    0      |     0.3051 |
| screen_time_before_sleep_min | -0.0001 |    0.0005 |    0.9    |    -0.0035 |
| physical_activity_hrs_week   |  0.0597 |    0.0046 |    0      |     0.2717 |
| social_interaction_level     |  0.0191 |    0.0071 |    0.0068 |     0.058  |

## Mediation (social media -> sleep -> stress)
|   a (X->M) |   b (M->Y|X) |   c_total (X->Y) |   c_prime_direct (X->Y|M) |   indirect (a*b) |   boot_ci95_low |   boot_ci95_high |   prop_mediated |   sobel_z |   sobel_p |    n |
|-----------:|-------------:|-----------------:|--------------------------:|-----------------:|----------------:|-----------------:|----------------:|----------:|----------:|-----:|
|    -0.3987 |       -0.589 |            0.705 |                    0.4702 |           0.2348 |          0.1895 |           0.2837 |          0.3331 |    10.114 | 4.779e-24 | 1200 |

## Digital Exposure Risk Index (DERI)
| index               | outcome              |   pearson_r |    p_value |
|:--------------------|:---------------------|------------:|-----------:|
| DERI (equal weight) | stress_level         |       0.62  | 1.56e-128  |
| DERI (equal weight) | academic_performance |      -0.612 | 3.057e-124 |
| DERI (PCA, 75% var) | stress_level         |       0.621 | 6.426e-129 |
| DERI (PCA, 75% var) | academic_performance |      -0.613 | 1.144e-124 |

### Outcomes by DERI quartile
| deri_quartile   |   n |   mean_stress |   mean_gpa |   mean_deri_score |
|:----------------|----:|--------------:|-----------:|------------------:|
| Q1              | 300 |         3.622 |      3.688 |            26.294 |
| Q2              | 300 |         4.629 |      3.467 |            41.653 |
| Q3              | 300 |         5.21  |      3.228 |            51.876 |
| Q4              | 300 |         6.206 |      2.893 |            68.913 |
