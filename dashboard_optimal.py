import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CI/CD Build Optimizer",
    layout="wide"
)

# --- LIGHT THEME STYLING ---
st.markdown("""
    <style>
    /* Light background */
    .stApp {
        background: #f8f9fa;
        color: #212529;
    }

    /* Container cards */
    .block-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #0077b6 !important;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }

    /* Column metric boxes */
    .metric-box {
        background: #e9f5ff;
        border: 1px solid #90e0ef;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: 600;
        color: #023e8a;
        box-shadow: 0px 2px 6px rgba(0, 123, 255, 0.2);
    }

    /* Dataframe table */
    .dataframe {
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
csv_file = "master_build_data_clean.csv"
df = pd.read_csv(csv_file)

st.markdown("<h1 style='text-align:center;'> CI/CD Build Optimizer Dashboard</h1>", unsafe_allow_html=True)

# --- COLUMNS DETECTED ---
st.subheader("📊 Columns Detected")
col_boxes = st.columns(len(df.columns))
for i, c in enumerate(df.columns):
    col_boxes[i].markdown(f"<div class='metric-box'>{c}</div>", unsafe_allow_html=True)

# --- DATA TABLE ---
st.subheader("📁 Build Data")
st.dataframe(df)

# --- VALIDATE DATA ---
required_cols = ["Duration", "Tests_Run", "Tests_Failed", "Build_Status"]
if not all(col in df.columns for col in required_cols):
    st.error(f"Required columns {required_cols} not found! Check CSV.")
elif df.empty:
    st.error("CSV file is empty! Add build records to proceed.")
else:
    # Ensure numeric cols
    df[["Duration", "Tests_Run", "Tests_Failed"]] = df[["Duration", "Tests_Run", "Tests_Failed"]].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=["Duration", "Tests_Run", "Tests_Failed"])

    # Normalize Build_Status
    df["Build_Status"] = df["Build_Status"].astype(str).str.strip().str.title()

    # --- SUMMARY ---
    st.subheader("📈 Summary Statistics")
    st.dataframe(df.describe().transpose())

    # --- BUILD STATUS DISTRIBUTION ---
    st.subheader("📌 Build Status Distribution")
    fig1 = px.histogram(
        df, x="Build_Status", color="Build_Status",
        title="Build Outcomes",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="simple_white"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- DURATION TREND ---
    st.subheader("⏱ Build Duration Trend")
    fig2 = px.line(
        df, y="Duration",
        title="Build Duration Over Time",
        color_discrete_sequence=["#0077b6"],
        template="simple_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- MODEL TRAINING ---
    if len(df) > 0:
        X = df[["Duration", "Tests_Run", "Tests_Failed"]]
        y = df["Build_Status"].map({"Pass": 1, "Fail": 0})

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # --- PREDICTION FORM ---
        st.subheader("🤖 Predict Build Outcome")
        duration = st.number_input("Duration (seconds)", min_value=0, value=5)
        tests_run = st.number_input("Tests Run", min_value=1, value=1)
        tests_failed = st.number_input("Tests Failed", min_value=0, value=0)

        if st.button("Predict Build Status"):
            pred = model.predict([[duration, tests_run, tests_failed]])
            status = "✅ Pass" if pred[0] == 1 else "❌ Fail"
            st.success(f"Predicted Build Status: {status}")
    else:
        st.warning("No valid numeric data available for model training.")
