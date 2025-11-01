import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# Helper functions
# -----------------------------------------------------------

def get_lp_between_ranks(current_rank, current_div, current_lp, target_rank, target_div, target_lp):
    """Calculate total LP between current and target ranks."""
    ranks = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
    total_lp = 0

    current_rank_index = ranks.index(current_rank)
    target_rank_index = ranks.index(target_rank)

    # Prevent backward progression
    if (current_rank_index > target_rank_index) or (
        current_rank_index == target_rank_index and current_div < target_div
    ):
        st.error("❌ Target rank must be higher than current rank.")
        return 0

    # Count LP from current to target
    for r in range(current_rank_index, target_rank_index + 1):
        divisions = [4, 3, 2, 1]
        for d in divisions:
            if r == current_rank_index and d > current_div:
                continue
            if r == target_rank_index and d < target_div:
                continue
            if r == current_rank_index and d == current_div:
                lp_needed = 100 - current_lp
            else:
                lp_needed = 100
            total_lp += lp_needed

    total_lp -= (100 - target_lp)
    return max(total_lp, 0)


def calc_price(lp_amount, base_price, multiplier):
    """Price = total LP * base price * multiplier."""
    return lp_amount * base_price * multiplier


# -----------------------------------------------------------
# Streamlit App UI
# -----------------------------------------------------------

st.set_page_config(page_title="MadBoost LP Calculator", layout="centered")

st.title("🎮 MadBoost LP Calculator")
st.caption("Boost pricing system with reference scaling (Iron IV → Current Rank).")

# ---- Rank input section ----
ranks = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
divisions = [4, 3, 2, 1]

col1, col2, col3 = st.columns(3)
with col1:
    current_rank = st.selectbox("Current Rank", ranks, index=0)
with col2:
    current_div = st.selectbox("Current Division", divisions, index=0)
with col3:
    current_lp = st.number_input("Current LP", min_value=0.0, max_value=99.9, value=0.0, step=0.1)

col4, col5, col6 = st.columns(3)
with col4:
    target_rank = st.selectbox("Target Rank", ranks, index=2)
with col5:
    target_div = st.selectbox("Target Division", divisions, index=3)
with col6:
    target_lp = st.selectbox("Target LP", [10, 30, 50, 70, 90], index=0)

st.divider()

# ---- Base pricing section ----
base_price = st.number_input("Base price per LP ($)", min_value=0.01, value=0.10, step=0.01)
multiplier = st.slider("Difficulty multiplier", 1.0, 3.0, 1.5, 0.1)

# -----------------------------------------------------------
# Main Calculation Logic
# -----------------------------------------------------------

if st.button("⚙️ Calculate LP and Prices"):
    # Client progression
    total_lp = get_lp_between_ranks(current_rank, current_div, current_lp, target_rank, target_div, target_lp)
    if total_lp == 0:
        st.stop()

    client_total_price = calc_price(total_lp, base_price, multiplier)

    # Reference progression (Iron IV → Current Rank)
    iron_ref_lp = get_lp_between_ranks("Iron", 4, 0, current_rank, current_div, current_lp)
    if iron_ref_lp == 0:
        st.error("❌ Unable to compute Iron IV reference path.")
        st.stop()

    iron_ref_price = calc_price(iron_ref_lp, base_price, multiplier)
    iron_base_price = iron_ref_price / iron_ref_lp  # 1 LP price reference

    # ---- Build progression data ----
    step_prices = []
    cumulative = []
    running_total = 0
    for i in range(int(total_lp)):
        step_price = iron_base_price * multiplier  # replaced with Iron IV base
        step_prices.append(step_price)

        # cumulative remains based on client base
        running_total += base_price * multiplier
        cumulative.append(running_total)

    df = pd.DataFrame({
        "Step #": range(1, len(step_prices) + 1),
        "Step Price ($)": [round(p, 4) for p in step_prices],
        "Cumulative ($)": [round(c, 2) for c in cumulative]
    })

    # -----------------------------------------------------------
    # Display results
    # -----------------------------------------------------------
    st.subheader("📊 Results Summary")
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total LP Needed", f"{total_lp}")
        st.metric("Client Total Price", f"${client_total_price:,.2f}")
    with colB:
        st.metric("Reference Path Price (Iron IV → Current)", f"${iron_ref_price:,.2f}")
        st.metric("Reference 1 LP Price", f"${iron_base_price:.4f}")

    st.divider()
    st.subheader("💰 LP Price Progression")
    st.caption("Step Price uses Iron IV base; Cumulative uses client base.")
    st.dataframe(df, use_container_width=True)

    # ---- Chart ----
    fig, ax = plt.subplots()
    ax.plot(df["Step #"], df["Step Price ($)"], label="Step Price ($, Iron IV base)")
    ax.plot(df["Step #"], df["Cumulative ($)"], label="Cumulative ($, Client base)")
    ax.set_xlabel("Step # (LP Gain)")
    ax.set_ylabel("Price ($)")
    ax.legend()
    st.pyplot(fig)

    st.success("✅ Calculation complete!")
