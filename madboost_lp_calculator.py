# Run: streamlit run madboost_lp_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------
# MADBOOST LP CALCULATOR (Iron IV → Current Rank Reference)
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
def calculate_reference_base_price(base_price, current_rank, current_div, current_lp, multiplier):
    """Compute Iron IV → current rank base LP reference."""
    iron_ref_lp, _, _ = calculate_lp_between_ranks("Iron", "IV", 0, current_rank, current_div, current_lp)
    if iron_ref_lp == 0:
        return base_price  # fallback if invalid
    iron_ref_price = iron_ref_lp * base_price * multiplier
    return iron_ref_price / iron_ref_lp  # 1 LP reference base price


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
    st.caption("Now using Iron IV → Current Rank base for reference pricing.")

st.markdown("---")

# --- Inputs ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎯 Current Rank")
    current_rank = st.selectbox("Current Rank", RANKS, index=0)
    current_div = st.selectbox("Current Division", DIVISIONS, index=0)
    current_lp = st.number_input("Current LP", min_value=0.0, max_value=99.9, value=0.0, step=0.1)

    st.subheader("🚀 Target Rank")
    target_rank = st.selectbox("Target Rank", RANKS, index=2)
    target_div = st.selectbox("Target Division", DIVISIONS, index=0)
    target_lp = st.selectbox("Target LP", [10, 30, 50, 70, 90], index=2)

    st.markdown("### 💵 Pricing Settings")
    base_price = st.number_input("Base LP price ($)", min_value=0.01, value=0.1, step=0.01, format="%.2f")
    multiplier = st.slider("Difficulty multiplier", 1.0, 3.0, 1.5, 0.1)

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

            # --- Reference base price (Iron IV -> Current)
            iron_base_price = calculate_reference_base_price(base_price, current_rank, current_div, current_lp, multiplier)

            # --- Client calculation (normal)
            client_total_price = total_lp * base_price * multiplier

            # --- Reference-adjusted calculation ---
            ref_total_price = total_lp * iron_base_price * multiplier

            # --- Build progression table ---
            step_prices = []
            cumulative = []
            running_total = 0
            for i in range(int(total_lp)):
                step_price = iron_base_price * multiplier  # uses new Iron IV base
                step_prices.append(step_price)

                running_total += base_price * multiplier  # keep client base for cumulative
                cumulative.append(running_total)

            df = pd.DataFrame({
                "Step #": range(1, len(step_prices) + 1),
                "Step Price ($)": [round(p, 4) for p in step_prices],
                "Cumulative ($)": [round(c, 2) for c in cumulative]
            })

            # --- Display results ---
            st.markdown("### 💰 Price Summary")
            colA, colB = st.columns(2)
            with colA:
                st.metric("Client Total (Base Price)", f"${client_total_price:,.2f}")
                st.metric("Reference 1 LP Price", f"${iron_base_price:.4f}")
            with colB:
                st.metric("Reference-Based Total", f"${ref_total_price:,.2f}")
                st.metric("Total LP Needed", f"{total_lp}")

            st.caption("Step price uses Iron IV reference base; cumulative remains on client base.")
            st.dataframe(df, use_container_width=True)

            # --- Chart ---
            fig, ax = plt.subplots()
            ax.plot(df["Step #"], df["Step Price ($)"], label="Step Price ($, Iron IV base)")
            ax.plot(df["Step #"], df["Cumulative ($)"], label="Cumulative ($, Client base)")
            ax.set_xlabel("Step # (LP Gain)")
            ax.set_ylabel("Price ($)")
            ax.legend()
            ax.set_facecolor("#1e1e1e")
            st.pyplot(fig)

            st.success("✅ Calculation complete!")

    else:
        st.info("👆 Enter your ranks, then click **Calculate Boost Price**.")
