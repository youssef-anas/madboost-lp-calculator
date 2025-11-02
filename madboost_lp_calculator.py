# Run with: streamlit run madboost_lp_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# RANK & LP SYSTEM
# -----------------------------------------------------------

RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
DIVISIONS = ["IV", "III", "II", "I"]
LP_PER_DIVISION = 100


def rank_index(rank, div):
    return RANKS.index(rank) * len(DIVISIONS) + DIVISIONS.index(div)


def calculate_lp_between_ranks(current_rank, current_div, current_lp,
                               target_rank, target_div, target_lp):
    """Compute total LP distance between current and target ranks."""
    curr_idx = rank_index(current_rank, current_div)
    target_idx = rank_index(target_rank, target_div)

    if target_idx < curr_idx or (target_idx == curr_idx and target_lp <= current_lp):
        return 0, 0, 0

    total_lp = 0
    if curr_idx == target_idx:
        total_lp = target_lp - current_lp
    else:
        # Since current_lp is guaranteed to be an integer (0-99), this calculation is fine.
        total_lp += (LP_PER_DIVISION - current_lp)
        for i in range(curr_idx + 1, target_idx):
            total_lp += LP_PER_DIVISION
        total_lp += target_lp

    divs = abs(target_idx - curr_idx)
    ranks = abs(RANKS.index(target_rank) - RANKS.index(current_rank))
    # Returns an integer LP value
    return int(total_lp), divs, ranks


# -----------------------------------------------------------
# PRICE PROGRESSION LOGIC
# -----------------------------------------------------------

def calculate_price_progression(base_price, total_lp, lp_gain, multipliers):
    """Progressive LP pricing based on gain level."""
    gain = lp_gain.lower()
    growth = multipliers[gain] / 100.0
    step_price = base_price
    total_price = 0.0
    progression = []

    for step in range(1, int(total_lp) + 1):
        # Applies the price growth
        step_price *= (1 + growth)
        total_price += step_price
        
        # Records progression every 10 steps or at the final step
        if step % 10 == 0 or step == int(total_lp):
            progression.append({
                "LP Step": step,
                "Step Price ($)": round(step_price, 4), # Keeping 4 decimal places for internal precision
                "Cumulative ($)": round(total_price, 2)
            })

    # Total price is rounded to 2 decimal places for currency display
    return round(total_price, 2), progression, step_price


# -----------------------------------------------------------
# STREAMLIT UI
# -----------------------------------------------------------

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
        st.write("🔥 **MadBoost**")
with col2:
    st.title("MadBoost Rank Boost Calculator")
    st.caption("Two-path linked LP pricing system — Reference path determines client’s base rate.")

st.markdown("---")

# --- Inputs ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎯 Current Rank")
    current_rank = st.selectbox("Current Rank", RANKS, index=0)
    current_div = st.selectbox("Current Division", DIVISIONS, index=0)

    # Current LP remains an integer input (0-99)
    current_lp = st.number_input("Current LP",
                                 min_value=0,
                                 max_value=99,
                                 value=0,
                                 step=1,
                                 format="%d")

    st.subheader("🚀 Target Rank")
    target_rank = st.selectbox("Target Rank", RANKS, index=2)
    target_div = st.selectbox("Target Division", DIVISIONS, index=0)
    target_lp = st.selectbox("Target LP", [10, 30, 50, 70, 90], index=2)

    st.markdown("### 💵 Pricing Settings")
    # 🔑 CHANGE 1: Base LP price to three decimal places
    base_price = st.number_input("Base LP price ($)",
                                 min_value=0.001,
                                 value=0.100,
                                 step=0.001,       # Step set to 1/1000th
                                 format="%.3f")  # Format set to three decimal places

    lp_gain = st.selectbox("Gain Level", ["low", "mid", "high"])

    st.markdown("### Tier Multipliers (%)")
    # 🔑 CHANGE 2: Multipliers to three decimal places
    m_low = st.number_input("Low (%)", min_value=0.000, value=5.000, step=0.001, format="%.3f")
    m_mid = st.number_input("Mid (%)", min_value=0.000, value=10.000, step=0.001, format="%.3f")
    m_high = st.number_input("High (%)", min_value=0.000, value=20.000, step=0.001, format="%.3f")
    multipliers = {"low": m_low, "mid": m_mid, "high": m_high}

    st.markdown(" ")
    calc_button = st.button("💰 **Calculate Boost Price**")

# --- Results ---
with col_right:
    if calc_button:
        total_lp, divs, ranks = calculate_lp_between_ranks(
            current_rank, current_div, current_lp, target_rank, target_div, target_lp
        )

        if total_lp <= 0:
            st.warning("⚠️ Invalid input — target rank must be higher or LP greater.")
        else:
            # ---------- REFERENCE PATH: Iron IV → Current ----------
            ref_lp, _, _ = calculate_lp_between_ranks("Iron", "IV", 0, current_rank, current_div, current_lp)
            ref_total_price, ref_progression, ref_final_step = calculate_price_progression(
                base_price, ref_lp, lp_gain, multipliers
            )

            # ---------- CLIENT PATH: Current → Target ----------
            client_total_price, client_progression, _ = calculate_price_progression(
                ref_final_step, total_lp, lp_gain, multipliers
            )

            # ---------- DataFrames ----------
            df_ref = pd.DataFrame(ref_progression)
            df_client = pd.DataFrame(client_progression)

            # --- Summary ---
            st.subheader(f"Results — {current_rank} {current_div} → {target_rank} {target_div} ({target_lp} LP)")
            st.info(f"🧮 Total LP Required: **{total_lp} LP**")
            st.success(f"🎯 Divisions: {divs} | Ranks: {ranks}")

            colA, colB = st.columns(2)
            with colA:
                st.markdown("### 🧱 Reference Path (Iron IV → Current)")
                st.metric("Total LP", f"{ref_lp}")
                st.metric("Total Price", f"${ref_total_price:,.2f}")
                # Display final step price with 4 decimal places for internal precision
                st.metric("Final Step Price", f"${ref_final_step:.4f}")
                st.dataframe(df_ref, use_container_width=True)

            with colB:
                st.markdown("### 🚀 Client Path (Current → Target)")
                st.metric("Total LP", f"{total_lp}")
                st.metric("Total Price", f"${client_total_price:,.2f}")
                # Display starting LP price with 4 decimal places for internal precision
                st.metric("Starting LP Price", f"${ref_final_step:.4f}")
                st.dataframe(df_client, use_container_width=True)

            # --- Charts ---
            st.markdown("### 📈 LP Price Progression Comparison")
            fig, ax = plt.subplots()
            ax.plot(df_ref["LP Step"], df_ref["Step Price ($)"], label="Reference Path")
            ax.plot(df_client["LP Step"], df_client["Step Price ($)"], label="Client Path (inherits Ref final price)")
            ax.set_xlabel("LP Step")
            ax.set_ylabel("Price ($)")
            ax.legend()
            ax.set_facecolor("#1e1e1e")
            ax.tick_params(colors='white', which='both')
            ax.spines['left'].set_color('white')
            ax.spines['bottom'].set_color('white')
            fig.patch.set_facecolor('#0e0e0e')
            ax.title.set_color('white')
            st.pyplot(fig) 

            st.success("✅ Calculation complete!")

    else:
        st.info("👆 Enter your ranks, then click **Calculate Boost Price**.")