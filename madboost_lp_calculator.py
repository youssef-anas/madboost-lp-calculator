# Run with: streamlit run madboost_lp_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------
# MADBOOST LP CALCULATOR — Updated Version
# ----------------------------------------------

# ---------- Core LP Pricing Algorithm ----------
def calculate_lp_boost_price(base_price, lp_requested, lp_gain, multipliers):
    """
    Calculate LP boosting total and step progression.
    """
    lp_gain = lp_gain.lower()
    if lp_gain not in multipliers:
        raise ValueError("Gain level must be one of: low, mid, high")

    growth_rate = multipliers[lp_gain] / 100.0
    step_price = base_price
    total_price = 0.0
    progression = []

    for step in range(1, lp_requested + 1):
        step_price = step_price * (1 + growth_rate)
        total_price += step_price
        progression.append({
            "Step": step,
            "Step Price ($)": round(step_price, 2),
            "Cumulative ($)": round(total_price, 2)
        })

    return round(total_price, 2), progression


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="MadBoost LP Calculator", layout="wide")

# Inject custom CSS for dark theme + MadBoost colors
st.markdown("""
    <style>
    body {
        background-color: #0e0e0e;
        color: #ffffff;
    }
    .stApp {
        background-color: #0e0e0e;
    }
    .stButton button {
        background-color: #ff5a00;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #ff7b33;
        color: black;
    }
    .css-1d391kg {
        background-color: #0e0e0e;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Header ----------
col1, col2 = st.columns([1, 3])

with col1:
    try:
        st.image("madboost_logo.jpg", width=180)
    except:
        st.write("🔥 MadBoost")

with col2:
    st.title("MadBoost LP Price Calculator")
    st.write("Dynamic LP pricing system for your boosting service — fast, transparent, and scalable.")

st.markdown("---")

# ---------- Inputs and Results ----------
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Input Settings")

    # ✅ Allow decimal & <1 values
    base_price = st.number_input(
        "Base LP price ($)",
        min_value=0.01,
        value=0.5,
        step=0.01,
        format="%.2f"
    )

    # ✅ Dropdown LP values
    lp_requested = st.selectbox(
        "LP to boost (steps)",
        options=[10, 30, 50, 70, 90],
        index=0
    )

    lp_gain = st.selectbox("Gain level", ["low", "mid", "high"])

    st.markdown("### Tier Multipliers (%)")
    m_low = st.number_input("Low (%)", min_value=0.0, value=5.0, step=0.5)
    m_mid = st.number_input("Mid (%)", min_value=0.0, value=10.0, step=0.5)
    m_high = st.number_input("High (%)", min_value=0.0, value=20.0, step=0.5)

    multipliers = {"low": m_low, "mid": m_mid, "high": m_high}

    st.markdown(" ")
    calc_button = st.button("💰 Calculate")

with col_right:
    if calc_button:
        total, progression = calculate_lp_boost_price(base_price, lp_requested, lp_gain, multipliers)

        st.subheader(f"Results for {lp_requested} LP Boost ({lp_gain.capitalize()} Gain)")
        st.metric(label="Total LP Boosting Price", value=f"${total}")

        df = pd.DataFrame(progression)
        st.dataframe(df, hide_index=True, use_container_width=True)

        # Chart
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df["Step"], df["Step Price ($)"], marker="o", color="#ff5a00")
        ax.set_facecolor("#1e1e1e")
        ax.set_title(f"{lp_requested} LP Price Progression", color="white")
        ax.set_xlabel("Step", color="white")
        ax.set_ylabel("Price ($)", color="white")
        ax.tick_params(colors="white")
        st.pyplot(fig)
    else:
        st.info("👆 Enter your LP details and press **Calculate** to see results.")
