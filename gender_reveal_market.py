import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import time

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
# Page Config & Styling
# -------------------------
st.set_page_config(page_title="Gender Reveal Prediction Market 🎉", layout="centered")

# Light theme styling
st.markdown("""
<style>
.stApp, .block-container {
    background-color: #fff9c4 !important;
    color: #212121 !important;
}
.stMarkdown h1, h2, h3, p, ul, ol, strong, em {
    color: #212121 !important;
}
input, textarea, select {
    background-color: #ffffff !important;
    color: #212121 !important;
}
.stButton > button {
    background-color: #212121 !important;
    color: #fff9c4 !important;
}
.stDataFrame, .stTable {
    color: #212121 !important;
    background-color: #fffde7 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Handle Pop-out View Mode
# -------------------------
query_params = st.query_params
popout_mode = query_params.get("view", [None])[0]

# -------------------------
# Header & Description (only in main view)
# -------------------------
if not popout_mode:
    st.image("baby.png", width=1000)
    st.markdown("""
    <h1 style='text-align: center; margin-top: -250px;'>🎉 Gender Reveal Prediction Market (Rupiah)</h1>
    <p style='text-align: center; font-size: 18px;'>
        Everyone places a bet on either <strong>'Boy'</strong> or <strong>'Girl'</strong>.<br>
        When the actual gender is revealed, all the money from those who bet incorrectly is pooled and shared among the winners in proportion to how much they bet. 
        The fewer the amount bet correctly, the larger each winner's payout will be.
        <br><br>
        <em>Note:</em> 20% of each winner’s profit is automatically donated to Nathan’s foundation.
        <br><br>
        <strong>📌 Please transfer your bet amount to: <u>6500887786 a/n Joseph Ian Tanuri</u></strong>
        <br><em>“Untuk Kalangan Sendiri”</em>
    </p>
    """, unsafe_allow_html=True)

# -------------------------
# Recalculate totals
# -------------------------
total_boy = st.session_state.bets[st.session_state.bets['Choice'] == 'Boy']['Bet'].sum()
total_girl = st.session_state.bets[st.session_state.bets['Choice'] == 'Girl']['Bet'].sum()
total_pool = total_boy + total_girl
boy_odds = total_boy / total_pool if total_pool > 0 else 0
girl_odds = total_girl / total_pool if total_pool > 0 else 0

# -------------------------
# Save Odds History
# -------------------------
if total_pool > 0:
    if st.session_state.odds_history.empty or (
        boy_odds != st.session_state.odds_history.iloc[-1]['Boy'] or
        girl_odds != st.session_state.odds_history.iloc[-1]['Girl']
    ):
        st.session_state.odds_history = pd.concat([
            st.session_state.odds_history,
            pd.DataFrame([{
                'Timestamp': datetime.now(),
                'Boy': boy_odds,
                'Girl': girl_odds
            }])
        ], ignore_index=True)

# -------------------------
# Pop-out chart modes
# -------------------------
if popout_mode == "pie" and total_pool > 0:
    fig = px.pie(
        names=['Boy', 'Girl'],
        values=[total_boy, total_girl],
        color=['Boy', 'Girl'],
        color_discrete_map={'Boy': '#1f77b4', 'Girl': '#ff69b4'},
        hole=0.3,
        title="Live Bet Distribution"
    )
    fig.update_layout(paper_bgcolor='#fff9c4')
    st.plotly_chart(fig, use_container_width=True)
    time.sleep(10)
    st.rerun()

elif popout_mode == "line" and not st.session_state.odds_history.empty:
    df = st.session_state.odds_history.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    fig = px.line(df, x='Timestamp', y=['Boy', 'Girl'], markers=True, title='Live Odds Over Time')
    fig.update_layout(paper_bgcolor='#fff9c4', plot_bgcolor='#fff9c4')
    st.plotly_chart(fig, use_container_width=True)
    time.sleep(10)
    st.rerun()

elif not popout_mode:
    # -------------------------
    # Bet Form
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
    # Show Bets + Remove Option
    # -------------------------
    st.header("📝 Current Bets")
    if not st.session_state.bets.empty:
        bets_display = st.session_state.bets.copy()
        bets_display['Bet'] = bets_display['Bet'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(bets_display)

        with st.expander("🗑️ Remove a Bet"):
            bet_index = st.number_input("Row index to remove", min_value=0, max_value=len(st.session_state.bets) - 1, step=1)
            if st.button("Remove Selected Bet"):
                st.session_state.bets = st.session_state.bets.drop(index=bet_index).reset_index(drop=True)
                st.rerun()

    # -------------------------
    # Live Charts
    # -------------------------
    if total_pool > 0:
        st.header("📊 Live Market")
        col1, col2 = st.columns(2)
        col1.metric("💙 Boy Odds", f"{boy_odds:.2%}")
        col2.metric("💖 Girl Odds", f"{girl_odds:.2%}")
        st.write(f"**Total Pool:** Rp {total_pool:,.0f}")

        fig1 = px.pie(
            names=['Boy', 'Girl'],
            values=[total_boy, total_girl],
            color=['Boy', 'Girl'],
            color_discrete_map={'Boy': '#1f77b4', 'Girl': '#ff69b4'},
            hole=0.3,
            title="Current Bet Distribution"
        )
        fig1.update_layout(paper_bgcolor='#fff9c4')
        st.plotly_chart(fig1, use_container_width=True)

        if not st.session_state.odds_history.empty:
            st.subheader("📈 Odds Over Time")
            df = st.session_state.odds_history.copy()
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            fig2 = px.line(df, x='Timestamp', y=['Boy', 'Girl'], markers=True, title='Odds History')
            fig2.update_layout(paper_bgcolor='#fff9c4', plot_bgcolor='#fff9c4')
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        ---  
        🔗 **Open Charts in New Windows**  
        [Open Pie Chart](?view=pie) | [Open Line Chart](?view=line)
        """)

    # -------------------------
    # Admin Section
    # -------------------------
    with st.expander("🔒 Admin: Reveal Gender, Payouts & Reset"):
        admin_pass = st.text_input("Enter admin password:", type="password")

        if admin_pass == "mysecret123":
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
                result_display['Bet'] = result_display['Bet'].apply(lambda x: f"Rp {x:,.0f}")
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

            st.header("🗑️ Reset Market")
            if st.button("🔄 Reset Everything"):
                st.session_state.bets = pd.DataFrame(columns=['Name', 'Choice', 'Bet'])
                st.session_state.actual_gender = None
                st.session_state.odds_history = pd.DataFrame(columns=['Timestamp', 'Boy', 'Girl'])
                st.rerun()
        else:
            st.info("🔑 Enter the admin password to access this section.")
