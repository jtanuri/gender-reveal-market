import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import BytesIO

# -------------------------
# Session State Initialization
# -------------------------
if 'bets' not in st.session_state:
    st.session_state.bets = pd.DataFrame(columns=['Name', 'Choice', 'Bet'])

if 'actual_gender' not in st.session_state:
    st.session_state.actual_gender = None

if 'odds_history' not in st.session_state:
    st.session_state.odds_history = pd.DataFrame(columns=['Timestamp', 'Boy', 'Girl'])

# -------------------------
# Page Config & dark theme
# -------------------------
st.set_page_config(page_title="Gender Reveal Prediction Market 🎉", layout="centered")
sns.set_theme(style="darkgrid")

# Optional: Logo
st.image("baby.png", width=1000)
st.markdown(
    """
    <h1 style='text-align: center; margin-top: -500px;'>🎉 Gender Reveal Prediction Market </h1>
    """,
    unsafe_allow_html=True
)

# -------------------------
# Recalculate totals every run
# -------------------------
total_boy = st.session_state.bets[st.session_state.bets['Choice'] == 'Boy']['Bet'].sum()
total_girl = st.session_state.bets[st.session_state.bets['Choice'] == 'Girl']['Bet'].sum()
total_pool = total_boy + total_girl

boy_odds = total_boy / total_pool if total_pool > 0 else 0
girl_odds = total_girl / total_pool if total_pool > 0 else 0

# -------------------------
# Place Bet Form
# -------------------------
with st.expander("📌 Place Your Bet"):
    with st.form("bet_form"):
        name = st.text_input("Your Name")
        choice = st.selectbox("Your Prediction", ["Boy", "Girl"])
        bet = st.number_input("Bet Amount (Rupiah)", min_value=10000, step=10000)
        submitted = st.form_submit_button("Place Bet")
        if submitted:
            new_bet = pd.DataFrame([[name, choice, bet]], columns=['Name', 'Choice', 'Bet'])
            st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)
            st.rerun()

# -------------------------
# Show Bets + Remove Bet
# -------------------------
st.header("📝 Current Bets")

if not st.session_state.bets.empty:
    st.dataframe(st.session_state.bets)

    with st.expander("🗑️ Remove a Bet"):
        bet_index = st.number_input(
            "Row index to remove (starts at 0)",
            min_value=0,
            max_value=len(st.session_state.bets) - 1,
            step=1
        )
        if st.button("Remove Selected Bet"):
            st.session_state.bets = st.session_state.bets.drop(index=bet_index).reset_index(drop=True)
            st.rerun()

# -------------------------
# Save Odds History
# -------------------------
if total_pool > 0:
    if st.session_state.odds_history.empty or \
       (boy_odds != st.session_state.odds_history.iloc[-1]['Boy'] or \
        girl_odds != st.session_state.odds_history.iloc[-1]['Girl']):
        st.session_state.odds_history = pd.concat([
            st.session_state.odds_history,
            pd.DataFrame([{
                'Timestamp': datetime.now(),
                'Boy': boy_odds,
                'Girl': girl_odds
            }])
        ], ignore_index=True)

# -------------------------
# Live Market (Fully Dark Graphs)
# -------------------------
if total_pool > 0:
    st.header("📊 Live Market")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💙 Boy Odds", f"{boy_odds:.2%}")
    with col2:
        st.metric("💖 Girl Odds", f"{girl_odds:.2%}")

    st.write(f"**Total Pool:** Rp {total_pool:,.0f}")

    # ✅ Pie Chart — smaller & dark
    fig1, ax1 = plt.subplots(figsize=(4, 4), facecolor='#121212')
    ax1.set_facecolor('#121212')
    explode = (0.05, 0.05)
    wedges, texts, autotexts = ax1.pie(
        [total_boy, total_girl],
        labels=['Boy', 'Girl'],
        colors=['#1f77b4', '#ff69b4'],
        autopct='%1.1f%%',
        shadow=True,
        startangle=90,
        explode=explode,
        textprops={'color': 'white'}
    )
    ax1.set_title('Current Bet Distribution', color='white')
    fig1.patch.set_facecolor('#121212')
    st.pyplot(fig1)

    # ✅ Line Chart — fully dark
    if not st.session_state.odds_history.empty:
        st.subheader("📈 Odds Over Time")
        fig2, ax2 = plt.subplots(figsize=(8, 4), facecolor='#121212')
        ax2.set_facecolor('#121212')
        ax2.plot(
            st.session_state.odds_history['Timestamp'],
            st.session_state.odds_history['Boy'],
            label='Boy',
            color='#1f77b4',
            marker='o',
            markersize=6,
            linewidth=2
        )
        ax2.plot(
            st.session_state.odds_history['Timestamp'],
            st.session_state.odds_history['Girl'],
            label='Girl',
            color='#ff69b4',
            marker='o',
            markersize=6,
            linewidth=2
        )
        ax2.set_xlabel("Time", color='white')
        ax2.set_ylabel("Probability", color='white')
        ax2.set_title("Market Probability History", color='white')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.6)
        ax2.tick_params(colors='white')
        fig2.patch.set_facecolor('#121212')
        fig2.autofmt_xdate()
        st.pyplot(fig2)

# -------------------------
# Reveal Gender + Payouts
# -------------------------
st.header("🎁 Reveal the Actual Gender")

gender = st.selectbox("Actual Gender", ["-- Select --", "Boy", "Girl"])
if gender != "-- Select --":
    st.session_state.actual_gender = gender
    st.success(f"🎉 Actual Gender: {gender}")

if st.session_state.actual_gender:
    winners = st.session_state.bets[st.session_state.bets['Choice'] == st.session_state.actual_gender]
    total_winner_bets = winners['Bet'].sum()

    payouts = []
    for _, row in st.session_state.bets.iterrows():
        if row['Choice'] == st.session_state.actual_gender and total_winner_bets > 0:
            payout = row['Bet'] * total_pool / total_winner_bets
            payout = round(payout / 100000) * 100000
        else:
            payout = 0
        payouts.append(payout)

    result = st.session_state.bets.copy()
    result['Payout (Rupiah)'] = payouts

    st.header("💰 Final Payouts")

    result_display = result.copy()
    result_display['Payout (Rupiah)'] = result_display['Payout (Rupiah)'].apply(lambda x: f"Rp {x:,.0f}")
    st.dataframe(result_display)

    st.write(f"🏆 Total Pool: Rp {total_pool:,.0f} distributed to winners.")

    towrite = BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        result.to_excel(writer, index=False, sheet_name='Payouts')
    towrite.seek(0)

    st.download_button(
        label="📥 Download Payouts as Excel",
        data=towrite,
        file_name="GenderReveal_Payouts.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------------
# Reset Button
# -------------------------
st.header("🗑️ Reset Market")

if st.button("🔄 Reset Everything"):
    st.session_state.bets = pd.DataFrame(columns=['Name', 'Choice', 'Bet'])
    st.session_state.actual_gender = None
    st.session_state.odds_history = pd.DataFrame(columns=['Timestamp', 'Boy', 'Girl'])
    st.rerun()
