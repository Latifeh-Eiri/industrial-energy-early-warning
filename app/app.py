from pathlib import Path

import pandas as pd
import streamlit as st


# Set up the page
st.set_page_config(
    page_title="Energy Early-Warning",
    page_icon="⚡",
    layout="wide"
)


# Add the colors and styling for the app
st.markdown(
    """
    <style>

    /* ---------- PAGE ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(106, 55, 255, 0.20),
                transparent 32%
            ),
            radial-gradient(
                circle at 10% 90%,
                rgba(0, 220, 255, 0.10),
                transparent 30%
            ),
            #07111f;

        color: #f4f7fb;
    }


    /* ---------- COMPACT LAYOUT ---------- */

    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 1400px;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }


    /* ---------- SECTION TITLES ---------- */

    h3 {
        color: #bca7ff !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.3rem !important;
    }


    /* ---------- NORMAL TEXT ---------- */

    p {
        color: #d8e1ec;
    }

    .stCaption {
        color: #91a5bb !important;
    }


    /* ---------- METRIC CARDS ---------- */

    div[data-testid="stMetric"] {

        background:
            linear-gradient(
                135deg,
                rgba(20, 36, 65, 0.95),
                rgba(38, 25, 74, 0.90)
            );

        border: 1px solid rgba(76, 210, 255, 0.35);

        border-radius: 12px;

        padding: 0.45rem 0.75rem;

        box-shadow:
            0 4px 18px rgba(0, 0, 0, 0.20);
    }


    /* ---------- METRIC LABELS ---------- */

    div[data-testid="stMetricLabel"] {
        color: #aebdd0 !important;
        font-size: 0.78rem !important;
    }


    /* ---------- METRIC NUMBERS ---------- */

    div[data-testid="stMetricValue"] {
        color: #55e6ff !important;
        font-size: 1.55rem !important;
        font-weight: 750 !important;
    }


    /* ---------- INPUT LABELS ---------- */

    label {
        color: #dce6f2 !important;
        font-weight: 600 !important;
    }


    /* ---------- SELECT BOXES ---------- */

    div[data-baseweb="select"] > div {

        background-color: #101d33 !important;

        border:
            1px solid rgba(142, 108, 255, 0.55) !important;

        border-radius: 8px !important;
    }


    /* ---------- NUMBER INPUTS ---------- */

    div[data-baseweb="input"] {

        background-color: #101d33 !important;

        border-radius: 8px !important;
    }


    /* ---------- DIVIDER ---------- */

    hr {
        border-color: rgba(85, 230, 255, 0.20) !important;

        margin-top: 0.4rem !important;
        margin-bottom: 0.4rem !important;
    }


    /* ---------- EXPANDER ---------- */

    div[data-testid="stExpander"] {

        background-color: rgba(14, 28, 49, 0.70);

        border:
            1px solid rgba(142, 108, 255, 0.30);

        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# Find and load the data file
APP_FOLDER = Path(__file__).parent
DATA_FILE = (
    APP_FOLDER
    / "data"
    / "energy_risk_predictions_demo.csv"
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


df = load_data()


# Get the asset types from the data
asset_options = ["All Assets"] + sorted(
    df["asset_type"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


# Add the title and subtitle
st.markdown(
    """
    <div style="
        font-size: 34px;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
        padding: 0;
        color: #ffffff;
        text-shadow: 0 0 12px rgba(85, 230, 255, 0.30);
    ">
        ⚡ Industrial Energy
        <span style="
            color: #55e6ff;
            -webkit-text-fill-color: #55e6ff;
        ">
            Early-Warning
        </span>
    </div>

    <div style="
        font-size: 14px;
        color: #aebed0;
        margin-top: 4px;
        margin-bottom: 8px;
    ">
        Predicting high-demand energy events before they occur
    </div>
    """,
    unsafe_allow_html=True
)


# Let the user choose an asset and prediction horizon
control1, control2 = st.columns(2)

with control1:
    selected_asset = st.selectbox(
        "Asset",
        asset_options
    )

with control2:
    horizon = st.selectbox(
        "Performance Horizon",
        [
            "1 Hour Ahead",
            "2 Hours Ahead",
            "3 Hours Ahead"
        ]
    )


# Filter the data for the selected asset
if selected_asset == "All Assets":
    filtered_df = df
else:
    filtered_df = df[
        df["asset_type"] == selected_asset
    ]


# Store evaluated episode recall for each prediction horizon
horizon_recall = {
    "1 Hour Ahead": 82.82,
    "2 Hours Ahead": 80.40,
    "3 Hours Ahead": 80.81
}

baseline_recall = {
    "1 Hour Ahead": 51.29,
    "2 Hours Ahead": 45.66,
    "3 Hours Ahead": 42.67
}

improvement_pp = {
    "1 Hour Ahead": 31.53,
    "2 Hours Ahead": 34.75,
    "3 Hours Ahead": 38.14
}

episode_recall = horizon_recall[horizon]
baseline_episode_recall = baseline_recall[horizon]
episode_improvement = improvement_pp[horizon]


# Show the main model results
st.markdown("### 🎯 Early-Warning Performance")

k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Overall Episode Recall",
        f"{episode_recall:.2f}%"
    )

with k2:
    st.metric(
        "Improvement vs Baseline",
        f"+{episode_improvement:.2f} pp"
    )

with k3:
    st.metric(
        "Warning Horizon",
        horizon.replace(" Ahead", "")
    )

st.caption(
    f"Threshold baseline recall at this horizon: "
    f"{baseline_episode_recall:.2f}%."
)


# Calculate statistics from the exported 1-hour prediction data
average_demand = filtered_df["Demand_kW"].mean()

actual_rate = (
    filtered_df["actual_high_demand"].mean() * 100
)

predicted_rate = (
    filtered_df["predicted_high_demand"].mean() * 100
)


# Split the lower part of the page into two sections
st.divider()

left, right = st.columns(2)


# Show information about the selected asset
with left:

    st.markdown("### ⚙️ Asset Overview")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric(
            "Average Demand",
            f"{average_demand:.1f} kW"
        )

    with a2:
        st.metric(
            "Actual High-Demand Rate",
            f"{actual_rate:.1f}%"
        )

    with a3:
        st.metric(
            "Predicted High-Demand Rate",
            f"{predicted_rate:.1f}%"
        )

    if selected_asset == "All Assets":
        st.caption(
            "Statistics calculated across all assets "
            "using the 1-hour prediction dataset."
        )
    else:
        st.caption(
            f"Statistics calculated for {selected_asset} "
            "using the 1-hour prediction dataset."
        )


# Calculate possible energy and cost savings
with right:

    st.markdown("### 💶 Potential Intervention Impact")

    f1, f2, f3 = st.columns(3)

    with f1:
        electricity_price = st.number_input(
            "€/kWh",
            min_value=0.0,
            value=0.20,
            step=0.01
        )

    with f2:
        reduction = st.number_input(
            "Saving / Alert (kWh)",
            min_value=0.0,
            value=50.0,
            step=5.0
        )

    with f3:
        actionable_alerts = st.number_input(
            "Actionable Alerts",
            min_value=0,
            value=10,
            step=1
        )

    energy_saved = reduction * actionable_alerts

    cost_saved = energy_saved * electricity_price

    result1, result2 = st.columns(2)

    with result1:
        st.metric(
            "Potential Energy Saved",
            f"{energy_saved:,.0f} kWh"
        )

    with result2:
        st.metric(
            "Potential Cost Saved",
            f"€{cost_saved:,.2f}"
        )

    st.caption(
        "Illustrative scenario using user-defined assumptions."
    )


# Add some extra information about the model
with st.expander("ℹ️ About the model"):

    st.write(
        """
        The Random Forest early-warning model detects 82.82%
        of new high-demand episodes one hour ahead, compared
        with 51.29% for the threshold baseline.

        Performance remains around 81% at prediction horizons
        of up to three hours.

        The trained model is facility-specific, while the
        framework can be retrained for other energy-intensive
        environments.

        The asset statistics shown in the dashboard use the
        exported 1-hour prediction dataset.

        Financial savings shown here are illustrative scenarios
        and not measured facility savings.
        """
    )