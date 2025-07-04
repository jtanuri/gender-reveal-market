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
# Page Config & dark theme
# -------------------------
st.set_page_config(page_title="Gender Reveal Prediction Market 🎉", layout="centered")

# Set background and text styles across the app
st.markdown(
    """
    <style>
    .stApp, .block-container {
        background-color: #fff9c4 !important;
        color: #212121 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown p, .stMarkdown ul, .stMarkdown ol,
    .stMarkdown strong, .stMarkdown em {
        color: #212121 !important;
        background-color: transparent !important;
    }
    input, textarea, select, .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #212121 !important;
    }
    label {
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
    """,
    unsafe_allow_html=True
)

# -------------------------
# Handle Pop-out View Mode
# -------------------------
query_params = st.query_params()
popout_mode = query_params.get("view", [None])[0]

# -------------------------
# Header and Description
# -------------------------
if not popout_mode:
    st.image("baby.png", width=1000)
    st.markdown("""
    <h1 style='text-align: center; margin-top: -250px;'>🎉 Gender Reveal Prediction Market (Rupiah)</h1>
    <p style='text-align: center; font-size: 18px;'>
        Place a bet on <strong>Boy</strong> or <strong>Girl</strong>.<br>
        Winners share the pool proportionally. 20% goes to charity.<br><br>
        <strong>📌 Transfer to: <u>6500887786 a/n Joseph Ian Tanuri</u></strong>
    </p>
    """, unsafe_allow_html=True)

# -------------------------
# Odds Calculation
# -------------------------
total_boy = st.session_state.bets[st.session_state.bets['Choice'] == 'Boy']['Bet'].sum()
total_girl = st.session_state.bets[st.session_state.bets['Choice'] == 'Girl']['Bet'].sum()
total_pool = total_boy + total_girl

boy_odds = total_boy / total_pool if total_pool > 0 else 0
girl_odds = total_girl / total_pool if total_pool > 0 else 0

# -------------------------
# Record Odds History
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
# Pop-out chart mode only
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
    st.experimental_rerun()

elif popout_mode == "line" and not st.session_state.odds_history.empty:
    df = st.session_state.odds_history.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    fig = px.line(df, x='Timestamp', y=['Boy', 'Girl'], markers=True, title='Live Odds Over Time')
    fig.update_layout(paper_bgcolor='#fff9c4', plot_bgcolor='#fff9c4')
    st.plotly_chart(fig, use_container_width=True)
    time.sleep(10)
    st.experimental_rerun()

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
    # Display Bets + Delete
    # -------------------------
    st.header("📝 Current Bets")
    if not st.session_state.bets.empty:
        bets_display = st.session_state.bets.copy()
        bets_display['Bet'] = bets_display['Bet'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(bets_display)

        with st.expander("🗑️ Remove a Bet"):
            bet_index = st.number_input("Row index to remove", min_value=0,
                                        max_value=len(st.session_state.bets) - 1, step=1)
            if st.button("Remove Selected Bet"):
                st.session_state.bets = st.session_state.bets.drop(index=bet_index).reset_index(drop=True)
                st.rerun()

    # -------------------------
    # Main Live Market
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
        ### 🔗 Open Charts in New Windows
        [Open Pie Chart](?view=pie) | [Open Line Chart](?view=line)
        """)
