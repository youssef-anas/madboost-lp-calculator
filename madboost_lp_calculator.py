# Run with: streamlit run madboost_lp_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------
# MADBOOST LP CALCULATOR — TARGET LP SYSTEM
# ----------------------------------------------

# Rank order (lowest to highest)
RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
DIVISIONS = ["IV", "III", "II", "I"]
LP_PER_DIVISION = 100  # LP needed per division


# ---------- LP GAP CALCULATION ----------
def calculate_total_lp(current_lp, target_lp):
    """
    Calculate total LP needed based on current LP and target LP goal (10, 30, 50, 70, 90).
    Handles rollover beyond 100 LP.
    """
    total_lp = target_lp
    if current_lp + target_lp > LP_PER_DIVISION:
        rollover = (current_lp + target_lp) - LP_PER_DIVISION
        total_lp = LP_PER_DIVISION - current_lp + rollover
    return total_lp


# ---------- LP Pricing Algorithm ----------
def calculate_lp_boost_price(base_price, total_lp, lp_gain, multipliers):
    lp_gain = lp_gain.lower()
    if lp_gain not in multipliers:
        raise ValueError("Gain level must be one of: low, mid, high")

    growth_rate = multipliers[lp_gain] / 100.0
    step_price = base_price
    total_price = 0.0
    progression = []

    for step in range(1, total_lp + 1):
        step_price = step_price * (1 + growth_rate)
        total_price += step_price
        if step % 10 == 0:  # record every 10 LP steps for display
            progression.append({
                "LP Step": step,
                "Step Price ($)": round(step_price, 2),
                "Cumulative ($)": round(total_price, 2)
            })

    return round(total_price, 2), progression


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="MadBoost LP Calculator", layout="wide")

# --- Styling ---
st.markdown("""
<style>
body {background-color: #0e0e0e; color: #fff;}
.stApp {background-color: #0e0e0e;}
.stButton button {
    background-color: #ff5a00; color: white; border-radius: 10px; font-weight: bold;
}
.stButton button:hover {
    background-color: #ff7b33; color: black;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("madboost_logo.jpg", width=180)
    except:
        st.write("🔥 MadBoost")
with col2:
    st.title("MadBoost LP Price Calculator")
    st.write("Calculate LP boost pricing based on current LP and target goal — simple and accurate.")

st.markdown("---")

# --- Inputs ---
col_left, col_right = st.columns([1, 2])
with col_left:
    st.subheader("Rank & LP Info")

    # Current rank and LP
    current_rank = st.selectbox("Current Rank", RANKS, index=3)  # default Gold
    current_div = st.selectbox("Current Division", DIVISIONS, index=0)  # default IV
    current_lp = st.number_input("Current LP", min_value=0, max_value=99, value=0, step=1)

    # ✅ Target LP options
    target_lp = st.selectbox("Target LP Gain", options=[10, 30, 50, 70, 90], index=0)

    # Pricing settings
    st.markdown("### Pricing Settings")
    base_price = st.number_input("Base LP price ($)", min_value=0.01, value=0.5, step=0.01, format="%.2f")
    lp_gain = st.selectbox("Gain level", ["low", "mid", "high"])

    st.markdown("### Tier Multipliers (%)")
    m_low = st.number_input("Low (%)", min_value=0.0, value=5.0, step=0.5)
    m_mid = st.number_input("Mid (%)", min_value=0.0, value=10.0, step=0.5)
    m_high = st.number_input("High (%)", min_value=0.0, value=20.0, step=0.5)

    multipliers = {"low": m_low, "mid": m_mid, "high": m_high}

    st.markdown(" ")
    calc_button = st.button("💰 Calculate Total Price")

with col_right:
    if calc_button:
        total_lp = calculate_total_lp(current_lp, target_lp)
        st.subheader(f"Results — {current_rank} {current_div} ({current_lp} LP)")
        st.info(f"🧮 Total LP to Boost: **{total_lp} LP**")

        total_price, progression = calculate_lp_boost_price(base_price, total_lp, lp_gain, multipliers)
        st.metric(label="Total Boosting Price", value=f"${total_price}")

        df = pd.DataFrame(progression)
        st.dataframe(df, hide_index=True, use_container_width=True)

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df["LP Step"], df["Step Price ($)"], marker="o", color="#ff5a00")
        ax.set_facecolor("#1e1e1e")
        ax.set_title(f"LP Price Progression ({total_lp} LP Boost)", color="white")
        ax.set_xlabel("LP Step", color="white")
        ax.set_ylabel("Price ($)", color="white")
        ax.tick_params(colors="white")
        st.pyplot(fig)
    else:
        st.info("👆 Choose your LP target and press **Calculate** to see results.")
