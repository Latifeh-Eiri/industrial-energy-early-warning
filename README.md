# Industrial Energy Early-Warning

## Project Overview

This project focuses on predicting high-energy-demand periods in a manufacturing facility before they happen.

The dataset contains 15-minute electrical measurements from 43 industrial assets, mainly collected during 2025.

The goal is not only to monitor energy demand, but to create an early-warning system that can identify upcoming high-demand periods early enough for operators to react.

The project includes:

- data preparation
- exploratory data analysis
- time-series analysis
- feature engineering
- machine learning
- model evaluation
- error analysis
- SQL analysis
- Power BI dashboard
- Streamlit application

---

## Business Problem

High-energy-demand periods can increase operational cost and put additional pressure on equipment and infrastructure.

Traditional threshold monitoring only detects a problem once demand is already high.

This project asks:

> Can high-demand events be predicted before they occur?

The final model predicts future high-demand conditions at:

- 1 hour ahead
- 2 hours ahead
- 3 hours ahead

The aim is to support earlier operational decisions rather than only reacting after demand has already crossed a threshold.

---

## Dataset

The dataset contains industrial electrical measurements recorded at 15-minute intervals from a manufacturing facility.

After data preparation, the cleaned dataset contains:

- **1,016,182 observations**
- **43 industrial assets**
- mainly **2025 data**
- 15-minute measurements
- asset-level electrical demand
- asset-type information

The cleaned dataset contains no missing values and no duplicate asset-timestamp combinations.

### High-Demand Definition

High demand is defined separately for each asset using its **90th percentile demand threshold**.

This means each asset is compared with its own normal operating range rather than using one fixed threshold for all assets.

For exploratory analysis, thresholds are calculated using the full dataset.

For machine learning, thresholds are calculated using the historical training period only to avoid data leakage.

---

## Project Workflow

### 1. Data Preparation

The raw measurement files are combined and cleaned.

Main steps include:

- keeping total electrical measurements
- checking missing values
- removing unreliable measurement windows
- checking duplicates
- validating timestamps
- adding asset metadata
- removing constant columns
- sorting the data by asset and time

Notebook:

`notebooks/01_data_preparation.ipynb`

---

### 2. Data Understanding and EDA

The exploratory analysis focuses on:

- energy use by asset
- energy use by asset type
- demand distribution
- high-demand periods
- time-based patterns
- asset-specific demand thresholds

One important finding is that about **36% of high-demand periods were not already above the threshold one hour earlier**.

This shows why simple threshold monitoring alone is not enough for early warning.

Notebook:

`notebooks/02_data_understanding_eda.ipynb`

---

### 3. Time-Series Analysis

The time-series analysis looks more closely at how demand changes before new high-demand episodes.

The analysis checks:

- time gaps
- 15-minute demand behaviour
- 1-hour historical demand
- new high-demand episodes
- pre-event demand patterns

The median demand level one hour before a new high-demand event was about **82.9% of the asset threshold**.

This suggests that recent demand history contains useful warning signals before the event begins.

Notebook:

`notebooks/03_time_series_analysis.ipynb`

---

## Feature Engineering

The machine-learning dataset includes historical demand and time-based features such as:

- current demand
- demand 15 minutes ago
- demand 30 minutes ago
- demand 45 minutes ago
- demand 60 minutes ago
- short-term demand changes
- rolling mean
- rolling standard deviation
- demand relative to the asset threshold
- hour of day
- day of week
- weekend indicator
- asset type

Only historical information is used for prediction.

The machine-learning thresholds are calculated using the training period only.

Notebook:

`notebooks/04_feature_engineering.ipynb`

---

## Machine Learning

Three approaches are compared:

- simple threshold baseline
- Logistic Regression
- Random Forest

The data is split chronologically rather than randomly.

A prediction-horizon gap is also used between training and test data to reduce leakage risk.

The individual asset ID is not used as a model feature.

The Random Forest model gave the strongest overall performance and was selected as the final model.

Notebook:

`notebooks/05_machine_learning.ipynb`

---

## Main Results

### 1-Hour Early Warning

Random Forest:

- **ROC-AUC:** 0.964
- **PR-AUC:** 0.811
- **Observation-level recall:** about 93%
- **Observation-level precision:** about 64.6%

At the new-episode level:

- **Threshold baseline recall:** 51.29%
- **Random Forest recall:** 82.82%
- **Improvement:** +31.53 percentage points

This means the model detects many more new high-demand episodes before they begin compared with simple threshold monitoring.

---

## Prediction Horizon Results

| Prediction Horizon | Baseline Recall | Random Forest Recall | Improvement |
|---|---:|---:|---:|
| 1 Hour | 51.29% | 82.82% | +31.53 pp |
| 2 Hours | 45.66% | 80.40% | +34.75 pp |
| 3 Hours | 42.67% | 80.81% | +38.14 pp |

Performance remains around 81% even at prediction horizons of up to three hours.

---

## Why Recall Matters

For this project, recall is more important than precision.

A missed high-demand event may reduce the value of the early-warning system.

The model therefore accepts some false alarms in order to reduce the number of missed events.

At the default threshold:

- recall is about 93%
- precision is about 65%

So out of 100 real high-demand observations, the model detects about 93.

Out of 100 warnings generated by the model, about 65 are correct.

---

## Model Evaluation

The final model is evaluated using:

- confusion matrix
- precision
- recall
- F1 score
- ROC-AUC
- PR-AUC
- threshold sensitivity
- episode-level recall
- error analysis

The project also separates two different types of performance:

**Observation-level performance**

This measures how well individual 15-minute high-demand observations are detected.

**Episode-level performance**

This measures whether the model gives a warning before a new high-demand episode begins.

The episode-level result is especially important because it reflects the real early-warning use case.

Notebook:

`notebooks/06_model_evaluation.ipynb`

---

## Error Analysis

The error analysis investigates:

- false positives
- false negatives
- prediction confidence
- threshold trade-offs
- performance across asset types

At the default 0.50 classification threshold:

- recall is about 93%
- lowering the threshold increases recall but also increases false alarms
- increasing the threshold improves precision but causes more missed high-demand observations

Notebook:

`notebooks/07_error_analysis.ipynb`

---

## SQL Analysis

The SQL part of the project includes:

- data validation
- average demand by asset type
- high-demand rate by asset type
- weekday vs weekend comparison
- time-of-day analysis
- asset risk ranking
- demand behaviour before future high demand
- 1-hour demand changes
- dashboard-ready view

SQL file:

`sql/operational_energy_analysis.sql`

---

## Power BI Dashboard

The Power BI dashboard presents the main operational findings in a visual format.

It is designed to support quick interpretation of:

- asset demand
- high-demand risk
- energy patterns
- operational differences across assets

File:

`dashboard/Industrial_Energy_Early_Warning_Dashboard.pbix`

---

## Streamlit Application

The Streamlit app provides a simple decision-support interface for the project.

It allows the user to:

- select an asset type
- compare prediction horizons
- view episode recall
- compare performance with the baseline
- view demand statistics
- explore potential energy savings
- estimate potential cost savings

The financial section uses user-defined assumptions.

These values are illustrative and are not measured savings from the facility.

App file:

`app/app.py`

Run the app from the project root:

```bash
python -m streamlit run app/app.py
```

Or, if the terminal is already inside the `app` folder:

```bash
python -m streamlit run app.py
```

A small demo dataset is included in `app/data/` so the application can run without the full processed dataset.

---

## Data Source and License

The dataset used in this project is available on Zenodo:

https://zenodo.org/records/19180972

The dataset is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

The full raw and processed datasets are not included in this repository because of their size. A smaller derived dataset is included to support the Streamlit demonstration.

---

## Author

**Latifeh Eiri**

Data Analytics & Data Science Portfolio Project