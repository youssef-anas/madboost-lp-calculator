# # Run with: streamlit run madboost_lp_calculator.py
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # -----------------------------------------------------------
# # RANK & LP SYSTEM
# # -----------------------------------------------------------

# RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
# DIVISIONS = ["IV", "III", "II", "I"]
# LP_PER_DIVISION = 100


# def rank_index(rank, div):
#     return RANKS.index(rank) * len(DIVISIONS) + DIVISIONS.index(div)


# def calculate_lp_between_ranks(current_rank, current_div, current_lp,
#                                target_rank, target_div, target_lp):
#     """Compute total LP distance between current and target ranks."""
#     curr_idx = rank_index(current_rank, current_div)
#     target_idx = rank_index(target_rank, target_div)

#     if target_idx < curr_idx or (target_idx == curr_idx and target_lp <= current_lp):
#         return 0, 0, 0

#     total_lp = 0
#     if curr_idx == target_idx:
#         total_lp = target_lp - current_lp
#     else:
#         # LP remaining in current division
#         total_lp += (LP_PER_DIVISION - current_lp)
#         # LP in intermediate divisions
#         for i in range(curr_idx + 1, target_idx):
#             total_lp += LP_PER_DIVISION
#         # LP in target division
#         total_lp += target_lp

#     divs = abs(target_idx - curr_idx)
#     ranks = abs(RANKS.index(target_rank) - RANKS.index(current_rank))
#     # Returns an integer LP value
#     return int(total_lp), divs, ranks


# # -----------------------------------------------------------
# # PRICE PROGRESSION LOGIC
# # -----------------------------------------------------------

# def calculate_price_progression(base_price, total_lp, lp_key, multipliers):
#     """
#     Progressive LP pricing based on a specific multiplier key from the multipliers dictionary.
#     lp_key will be 'fixed' for the ref path, and 'low/mid/high' for the client path.
#     """
#     growth = multipliers[lp_key] / 100.0
#     step_price = base_price
#     total_price = 0.0
#     progression = []

#     for step in range(1, int(total_lp) + 1):
#         # Applies the price growth
#         step_price *= (1 + growth)
#         total_price += step_price
        
#         # Records progression every 10 steps or at the final step
#         if step % 10 == 0 or step == int(total_lp):
#             progression.append({
#                 "LP Step": step,
#                 "Step Price ($)": round(step_price, 4), # Keeping 4 decimal places for internal precision
#                 "Cumulative ($)": round(total_price, 2)
#             })

#     # Total price is rounded to 2 decimal places for currency display
#     return round(total_price, 2), progression, step_price


# # -----------------------------------------------------------
# # STREAMLIT UI
# # -----------------------------------------------------------

# st.set_page_config(page_title="MadBoost Rank Boost Calculator", layout="wide")

# # --- Styling ---
# st.markdown("""
# <style>
# body {background-color: #0e0e0e; color: #fff;}
# .stApp {background-color: #0e0e0e;}
# h1, h2, h3, h4, h5, h6, label, p {color: white !important;}
# .stButton button {background-color: #ff5a00; color: white; border-radius: 10px; font-weight: bold;}
# .stButton button:hover {background-color: #ff7b33; color: black;}
# </style>
# """, unsafe_allow_html=True)

# # --- Header ---
# col1, col2 = st.columns([1, 3])
# with col1:
#     try:
#         st.image("madboost_logo.jpg", width=180) 
#     except:
#         st.write("🔥 **MadBoost**")
# with col2:
#     st.title("MadBoost Rank Boost Calculator")
#     st.caption("Two-path linked LP pricing system — Reference path determines client’s base rate.")

# st.markdown("---")

# # --- Inputs ---
# col_left, col_right = st.columns([1, 2])

# with col_left:
#     st.subheader("🎯 Current Rank")
#     current_rank = st.selectbox("Current Rank", RANKS, index=0)
#     current_div = st.selectbox("Current Division", DIVISIONS, index=0)

#     # Current LP remains an integer input (0-99)
#     current_lp = st.number_input("Current LP",
#                                  min_value=0,
#                                  max_value=99,
#                                  value=0,
#                                  step=1,
#                                  format="%d")

#     st.subheader("🚀 Target Rank")
#     target_rank = st.selectbox("Target Rank", RANKS, index=2)
#     target_div = st.selectbox("Target Division", DIVISIONS, index=0)
#     target_lp = st.selectbox("Target LP", [10, 30, 50, 70, 90], index=2)

#     st.markdown("### 💵 Pricing Settings")
#     # Base LP price accepts three decimal places
#     base_price = st.number_input("Base LP price ($)",
#                                  min_value=0.001,
#                                  value=0.100,
#                                  step=0.001,
#                                  format="%.3f")
    
#     # 🔑 NEW FIELD: Fixed Rate for Reference Path only
#     m_fixed = st.number_input("Fixed Rate (%) (Ref Path Only)",
#                               min_value=0.000,
#                               value=1.000,
#                               step=0.001,
#                               format="%.3f")

#     # User selects gain level for the CLIENT PATH
#     lp_gain = st.selectbox("Gain Level (Client Path Only)", ["low", "mid", "high"])

#     st.markdown("### Tier Multipliers (%) (Client Path Only)")
#     # Multipliers for Low/Mid/High (used by Client Path only)
#     m_low = st.number_input("Low (%)", min_value=0.000, value=5.000, step=0.001, format="%.3f")
#     m_mid = st.number_input("Mid (%)", min_value=0.000, value=10.000, step=0.001, format="%.3f")
#     m_high = st.number_input("High (%)", min_value=0.000, value=20.000, step=0.001, format="%.3f")
    
#     # Separate multipliers for the two paths
#     ref_multipliers = {"fixed": m_fixed} # Used for Iron IV -> Current
#     client_multipliers = {"low": m_low, "mid": m_mid, "high": m_high} # Used for Current -> Target

#     st.markdown(" ")
#     calc_button = st.button("💰 **Calculate Boost Price**")

# # --- Results ---
# with col_right:
#     if calc_button:
#         total_lp, divs, ranks = calculate_lp_between_ranks(
#             current_rank, current_div, current_lp, target_rank, target_div, target_lp
#         )

#         if total_lp <= 0:
#             st.warning("⚠️ Invalid input — target rank must be higher or LP greater.")
#         else:
#             # ---------- REFERENCE PATH: Iron IV → Current ----------
#             ref_lp, _, _ = calculate_lp_between_ranks("Iron", "IV", 0, current_rank, current_div, current_lp)
            
#             # 🔑 Use 'fixed' key and ref_multipliers for the Reference Path
#             ref_total_price, ref_progression, ref_final_step = calculate_price_progression(
#                 base_price, ref_lp, "fixed", ref_multipliers
#             )

#             # ---------- CLIENT PATH: Current → Target ----------
#             # Use user-selected lp_gain and client_multipliers for the Client Path
#             client_total_price, client_progression, _ = calculate_price_progression(
#                 ref_final_step, total_lp, lp_gain.lower(), client_multipliers
#             )

#             # ---------- DataFrames ----------
#             df_ref = pd.DataFrame(ref_progression)
#             df_client = pd.DataFrame(client_progression)
            
#             # FIX FOR KEY ERROR: Only proceed if the DataFrames have content
#             if not df_ref.empty and not df_client.empty:
                
#                 # --- Summary ---
#                 st.subheader(f"Results — {current_rank} {current_div} → {target_rank} {target_div} ({target_lp} LP)")
#                 st.info(f"🧮 Total LP Required: **{total_lp} LP**")
#                 st.success(f"🎯 Divisions: {divs} | Ranks: {ranks}")

#                 colA, colB = st.columns(2)
#                 with colA:
#                     st.markdown("### 🧱 Reference Path (Iron IV → Current)")
#                     st.metric("Multiplier Used", f"{m_fixed:.3f}% (Fixed)")
#                     st.metric("Total LP", f"{ref_lp}")
#                     st.metric("Total Price", f"${ref_total_price:,.2f}")
#                     st.metric("Final Step Price", f"${ref_final_step:.4f}")
#                     st.dataframe(df_ref, use_container_width=True)

#                 with colB:
#                     st.markdown("### 🚀 Client Path (Current → Target)")
#                     st.metric("Multiplier Used", f"{client_multipliers[lp_gain.lower()]:.3f}% ({lp_gain.capitalize()})")
#                     st.metric("Total LP", f"{total_lp}")
#                     st.metric("Total Price", f"${client_total_price:,.2f}")
#                     st.metric("Starting LP Price", f"${ref_final_step:.4f}")
#                     st.dataframe(df_client, use_container_width=True)

#                 # --- Charts ---
#                 st.markdown("### 📈 LP Price Progression Comparison")
#                 fig, ax = plt.subplots()
#                 # The plotting is now safe from KeyErrors because we checked if the DFs are empty
#                 ax.plot(df_ref["LP Step"], df_ref["Step Price ($)"], label="Reference Path (Fixed Rate)")
#                 ax.plot(df_client["LP Step"], df_client["Step Price ($)"], label=f"Client Path ({lp_gain.capitalize()} Rate)")
#                 ax.set_xlabel("LP Step")
#                 ax.set_ylabel("Price ($)")
#                 ax.legend() 
#                 ax.set_facecolor("#1e1e1e")
#                 ax.tick_params(colors='white', which='both')
#                 ax.spines['left'].set_color('white')
#                 ax.spines['bottom'].set_color('white')
#                 fig.patch.set_facecolor('#0e0e0e')
#                 ax.title.set_color('white')
#                 st.pyplot(fig)

#                 st.success("✅ Calculation complete!")

#             else:
#                 st.warning("⚠️ Calculation resulted in empty progression data. Check if target rank is higher than current rank.")

#     else:
#         st.info("👆 Enter your ranks and pricing settings, then click **Calculate Boost Price**.")



# -----------------------------------------------------------
# RANK & LP SYSTEM
# -----------------------------------------------------------

RANKS = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond"]
DIVISIONS = ["IV", "III", "II", "I"]
LP_PER_DIVISION = 100

# Tier definitions: كل rank عنده سعر ثابت لكل LP
# إنت بتحدد الأرقام دي من الـ settings
DEFAULT_TIER_RATES = {
    "Iron":     0.030,
    "Bronze":   0.035,
    "Silver":   0.045,
    "Gold":     0.060,
    "Platinum": 0.080,
    "Emerald":  0.110,
    "Diamond":  0.150,
}

def rank_index(rank, div):
    return RANKS.index(rank) * len(DIVISIONS) + DIVISIONS.index(div)


def calculate_lp_between_ranks(current_rank, current_div, current_lp,
                               target_rank, target_div, target_lp):
    curr_idx = rank_index(current_rank, current_div)
    target_idx = rank_index(target_rank, target_div)

    if target_idx < curr_idx or (target_idx == curr_idx and target_lp <= current_lp):
        return 0, 0, 0

    total_lp = 0
    if curr_idx == target_idx:
        total_lp = target_lp - current_lp
    else:
        total_lp += (LP_PER_DIVISION - current_lp)
        for i in range(curr_idx + 1, target_idx):
            total_lp += LP_PER_DIVISION
        total_lp += target_lp

    divs = abs(target_idx - curr_idx)
    ranks = abs(RANKS.index(target_rank) - RANKS.index(current_rank))
    return int(total_lp), divs, ranks


# -----------------------------------------------------------
# NEW: TIERED FLAT PRICING
# -----------------------------------------------------------

def get_division_rank(div_index):
    """بياخد index الـ division ويرجع اسم الـ rank."""
    return RANKS[div_index // len(DIVISIONS)]


def calculate_tiered_price(start_rank, start_div, start_lp,
                           end_rank, end_div, end_lp,
                           tier_rates):
    """
    بتحسب السعر بطريقة tiered:
    كل LP في tier معين بيتحسب بسعره الثابت.
    """
    start_idx = rank_index(start_rank, start_div)
    end_idx   = rank_index(end_rank,   end_div)

    if end_idx < start_idx or (end_idx == start_idx and end_lp <= start_lp):
        return 0.0, []

    total_price = 0.0
    breakdown   = []
    current_idx = start_idx
    current_lp  = start_lp

    while current_idx <= end_idx:
        rank_name = get_division_rank(current_idx)
        rate      = tier_rates[rank_name]

        # كام LP بنحسبهم في الـ division دي؟
        if current_idx == end_idx:
            lp_in_div = end_lp - current_lp
        else:
            lp_in_div = LP_PER_DIVISION - current_lp

        cost = lp_in_div * rate
        total_price += cost

        if lp_in_div > 0:
            div_name  = DIVISIONS[current_idx % len(DIVISIONS)]
            breakdown.append({
                "Division":    f"{rank_name} {div_name}",
                "LP":          lp_in_div,
                "Rate ($/LP)": rate,
                "Cost ($)":    round(cost, 2),
            })

        current_idx += 1
        current_lp   = 0  # بعد أول division نبدأ من 0

    return round(total_price, 2), breakdown


# -----------------------------------------------------------
# STREAMLIT UI
# -----------------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="MadBoost Rank Boost Calculator", layout="wide")

st.markdown("""
<style>
body {background-color: #0e0e0e; color: #fff;}
.stApp {background-color: #0e0e0e;}
h1,h2,h3,h4,h5,h6,label,p {color: white !important;}
.stButton button {background-color: #ff5a00; color: white; border-radius: 10px; font-weight: bold;}
.stButton button:hover {background-color: #ff7b33; color: black;}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    try:
        st.image("madboost_logo.jpg", width=180)
    except:
        st.write("🔥 **MadBoost**")
with col2:
    st.title("MadBoost Rank Boost Calculator")
    st.caption("Tiered flat pricing — each rank tier has its own fixed LP rate.")

st.markdown("---")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🎯 Current Rank")
    current_rank = st.selectbox("Current Rank", RANKS, index=0)
    current_div  = st.selectbox("Current Division", DIVISIONS, index=0)
    current_lp   = st.number_input("Current LP", min_value=0, max_value=99, value=0, step=1, format="%d")

    st.subheader("🚀 Target Rank")
    target_rank = st.selectbox("Target Rank", RANKS, index=3)
    target_div  = st.selectbox("Target Division", DIVISIONS, index=0)
    target_lp   = st.selectbox("Target LP", [0, 10, 30, 50, 70, 90], index=0)

    st.markdown("### 💵 Tier Rates ($ per LP)")
    st.caption("Set the price per LP for each rank tier. Higher ranks = higher rate.")

    tier_rates = {}
    for rank in RANKS:
        default = DEFAULT_TIER_RATES[rank]
        tier_rates[rank] = st.number_input(
            f"{rank} ($/LP)",
            min_value=0.001,
            value=default,
            step=0.001,
            format="%.3f"
        )

    calc_button = st.button("💰 **Calculate Boost Price**")

with col_right:
    if calc_button:
        total_lp, divs, ranks = calculate_lp_between_ranks(
            current_rank, current_div, current_lp,
            target_rank,  target_div,  target_lp
        )

        if total_lp <= 0:
            st.warning("⚠️ Target rank must be higher than current rank.")
        else:
            total_price, breakdown = calculate_tiered_price(
                current_rank, current_div, current_lp,
                target_rank,  target_div,  target_lp,
                tier_rates
            )

            st.subheader(f"{current_rank} {current_div} → {target_rank} {target_div} ({target_lp} LP)")
            st.info(f"🧮 Total LP: **{total_lp} LP** across {divs} divisions ({ranks} ranks)")

            colA, colB = st.columns(2)
            with colA:
                st.metric("Total Price", f"${total_price:,.2f}")
            with colB:
                st.metric("Avg Rate", f"${total_price/total_lp:.4f} / LP")

            st.markdown("### 📊 Price Breakdown by Division")
            df = pd.DataFrame(breakdown)
            st.dataframe(df, use_container_width=True)

            # Quick sanity check
            st.markdown("### 🔍 Sanity Check")
            iron_to_gold, _, _ = calculate_lp_between_ranks("Iron","IV",0,"Gold","IV",0)
            price_i2g, _ = calculate_tiered_price("Iron","IV",0,"Gold","IV",0, tier_rates)
            iron_to_diamond, _, _ = calculate_lp_between_ranks("Iron","IV",0,"Diamond","I",100)
            price_i2d, _ = calculate_tiered_price("Iron","IV",0,"Diamond","I",100, tier_rates)

            col1s, col2s = st.columns(2)
            with col1s:
                st.metric("Iron IV → Gold IV", f"${price_i2g:,.2f}", f"{iron_to_gold} LP")
            with col2s:
                st.metric("Iron IV → Diamond I", f"${price_i2d:,.2f}", f"{iron_to_diamond} LP")

            st.success("✅ Done!")
    else:
        st.info("👆 Set your ranks and tier rates, then click Calculate.")
