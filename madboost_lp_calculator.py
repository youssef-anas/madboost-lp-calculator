# Run locally: streamlit run madboost_lp_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------
# MADBOOST LP CALCULATOR (Dual Comparison Version)
# ---------------------------------------

RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
DIVISIONS = ["IV", "III", "II", "I"]
LP_PER_DIVISION = 100


# -------------------- Rank Helpers --------------------
def rank_index(rank: str, div: str) -> int:
    """Convert rank + division into linear index."""
    return RANKS.index(rank) * len(DIVISIONS) + DIVISIONS.index(div)


# -------------------- LP Calculation --------------------
def calculate_lp_between_ranks(current_rank, current_div, current_lp,
                               target_rank, target_div, target_lp):
    """Total LP difference between two rank/division states."""
    curr_idx = rank_index(current_rank, current_div)
    target_idx = rank_index(target_rank, target_div)

    if target_idx < curr_idx or (target_idx == curr_idx and target_lp <= current_lp):
        return 0, 0, 0  # invalid (lower or same rank)

    total_lp = 0
    if curr_idx == target_idx:
        total_lp = target_lp - current_lp
    else:
        remaining_in_current = LP_PER_DIVISION - current_lp
        total_lp += remaining_in_current
        for i in range(curr_idx + 1, target_idx):
            total_lp += LP_PER_DIVISION
        total_lp += target_lp

    divisions_between = abs(target_idx - curr_idx)
    ranks_between = abs(RANKS.index(target_rank) - RANKS.index(current_rank))
    return total_lp, divisions_between, ranks_between


# -------------------- Pricing Growth --------------------
def calculate_lp_boost_price(base_price, total_lp, lp_gain, multipliers):
    """Progressive LP pricing model."""
    lp_gain = lp_gain.lower()
    g = multipliers[lp_gain] / 100.0
    step_price = base_price
    total_price = 0.0
    progression = []

    for step in range(1, total_lp + 1):
        step_price *= (1 + g)
        total_price += step_price
        if step % 10 == 0:
            progression.append({
                "LP Step": step,
                "Step Price ($)": round(step_price, 2),
                "Cumulative ($)": round(total_price, 2)
            })

    return round(total_price, 2), progression, round(step_price, 2)  # include final step price


# -------------------- Next LP Price --------------------
def next_lp_price(base_price, current_lp, lp_gain, multipliers):
    """Return price of next 1 LP gain."""
    lp_gain = lp_gain.lower()
    g = multipliers[lp_gain] / 100.0
    n = current_lp + 1
    return round(base_price * (1 + g) ** n, 2)


# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="MadBoost Rank Boost Calculator", layout="wide")

# --- Styling ---
st.markdown("""
<style>
body {background-color: #0e0e0e; color: #fff;}
.stApp {background-color: #0e0e0e;}
h1, h2, h3, h4, h5, h6, label, p {color: white !important;}
.stButton button {background-color: #ff5a00; color: white; border-radius: 10px; font-weight: bold;}
.stButton button:hover {background-color: #ff7b33; color: black;}
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
    st.title("MadBoost Rank Boost Calculator")
    st.caption("Now compares client path vs. Iron IV-based pricing reference.")

st.markdown("---")

# --- Inputs ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎯 Current Rank")
    current_rank = st.selectbox("Current Rank", RANKS, index=0)
    current_div = st.selectbox("Current Division", DIVISIONS, index=0)
    current_lp = st.number_input("Current LP", min_value=0, max_value=99, value=0, step=1)

    st.subheader("🚀 Target Rank")
    target_rank = st.selectbox("Target Rank", RANKS, index=2)
    target_div = st.selectbox("Target Division", DIVISIONS, index=0)
    target_lp = st.selectbox("Target LP", [10, 30, 50, 70, 90], index=2)

    st.markdown("### 💵 Pricing Settings")
    base_price = st.number_input("Base LP price ($)", min_value=0.01, value=0.5, step=0.01, format="%.2f")
    lp_gain = st.selectbox("Gain Level", ["low", "mid", "high"])

    st.markdown("### Tier Multipliers (%)")
    m_low = st.number_input("Low (%)", min_value=0.0, value=5.0, step=0.5)
    m_mid = st.number_input("Mid (%)", min_value=0.0, value=10.0, step=0.5)
    m_high = st.number_input("High (%)", min_value=0.0, value=20.0, step=0.5)
    multipliers = {"low": m_low, "mid": m_mid, "high": m_high}

    st.markdown(" ")
    calc_button = st.button("💰 Calculate Boost Price")

# --- Results ---
with col_right:
    if calc_button:
        total_lp, divs, ranks = calculate_lp_between_ranks(
            current_rank, current_div, current_lp, target_rank, target_div, target_lp
        )

        if total_lp <= 0:
            st.warning("⚠️ Invalid input — target rank must be higher or LP greater.")
        else:
            st.subheader(f"Results — {current_rank} {current_div} → {target_rank} {target_div} ({target_lp} LP)")
            st.info(f"🧮 Total LP Required: **{total_lp} LP**")
            st.success(f"🎯 Divisions: {divs} | Ranks: {ranks}")

            # --- Parallel Reference (Iron IV -> Target) ---
            ref_lp, _, _ = calculate_lp_between_ranks("Iron", "IV", 0, target_rank, target_div, target_lp)
            _, _, ref_last_price = calculate_lp_boost_price(base_price, ref_lp, lp_gain, multipliers)

            # --- Client Calculation with User Base Price ---
            total_price_client, progression_client, _ = calculate_lp_boost_price(
                base_price, total_lp, lp_gain, multipliers
            )

            # --- Client Calculation Using Ref Last LP Price as Base ---
            total_price_scaled, progression_scaled, _ = calculate_lp_boost_price(
                ref_last_price, total_lp, lp_gain, multipliers
            )

            next_price = next_lp_price(base_price, current_lp, lp_gain, multipliers)

            # --- Display both results ---
            st.markdown("### 💰 Price Comparison")
            st.metric("Client Path (Your Base)", f"${total_price_client}")
            st.metric("Client Path (Iron IV Base Adjusted)", f"${total_price_scaled}")
            st.caption(f"New base price used from reference: ${ref_last_price:.2f}")

            st.metric("💡 Price for Next 1 LP", f"${next_price}")

            df = pd.DataFrame(progression_client)
            st.dataframe(df, hide_index=True, use_container_width=True)

            # --- Chart Comparison ---
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(df["LP Step"], df["Step Price ($)"], marker="o", color="#ff5a00", label="Client Base")
            df_scaled = pd.DataFrame(progression_scaled)
            ax.plot(df_scaled["LP Step"], df_scaled["Step Price ($)"], color="cyan", linestyle="--", label="Iron IV Adjusted Base")
            ax.set_facecolor("#1e1e1e")
            ax.set_title(f"LP Price Progression ({total_lp} LP)", color="white")
            ax.set_xlabel("LP Step", color="white")
            ax.set_ylabel("Price ($)", color="white")
            ax.tick_params(colors="white")
            ax.legend(facecolor="#1e1e1e", labelcolor="white")
            st.pyplot(fig)
    else:
        st.info("👆 Enter your ranks, then click **Calculate**.")
