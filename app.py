import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. PAGE INITIALIZATION (DARK THEME FOCUS)
st.set_page_config(
    page_title="Nordic Combined Elo Live",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. POWERFUL CSS INJECTION FOR PREMIUM DARK INTERFACE
st.markdown("""
    <style>
    /* Force dark background on the main app content */
    .stApp {
        background-color: #0e1117 !important;
        color: #e0e0e0 !important;
    }
    /* Style main headers and descriptions */
    .main-title { font-size: 36px; font-weight: bold; color: #4dadf7; margin-bottom: 20px; }
    .section-desc { font-size: 14px; color: #a0a0a0; margin-bottom: 25px; }
    
    /* Make standard markdown texts look sharp in dark mode */
    h1, h2, h3, h4, p, span, label {
        color: #ffffff !important;
    }
    
    /* Style tabs container for deep integration */
    button[data-baseweb="tab"] {
        color: #a0a0a0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4dadf7 !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# Flags map
FLAG_MAP = {
    "AUT": "🇦🇹 AUT", "GER": "🇩🇪 GER", "FIN": "🇫🇮 FIN", "NOR": "🇳🇴 NOR",
    "USA": "🇺🇸 USA", "JPN": "🇯🇵 JPN", "FRA": "🇫🇷 FRA", "SUI": "🇨🇭 SUI",
    "ITA": "🇮🇹 ITA", "POL": "🇵🇱 POL", "CZE": "🇨🇿 CZE", "SLO": "🇸🇮 SLO",
    "RUS": "🇷🇺 RUS", "EST": "🇪🇪 EST", "UKR": "🇺🇦 UKR", "SVK": "🇸🇰 SVK",
    "KAZ": "🇰🇿 KAZ", "CAN": "🇨🇦 CAN", "SWE": "🇸🇪 SWE", "KOR": "🇰🇷 KOR"
}

@st.cache_data
def load_data():
    df = pd.read_csv("Elo_Results_Final.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

try:
    df = load_data()
    
    st.sidebar.title("Navigation Panel")
    app_mode = st.sidebar.radio(
        "Choose Section:", 
        ["🏆 Live Rankings", "⏳ Historical Time Machine", "📈 Athlete Lifeline Explorer"]
    )

    MIN_STARTY = 30
    DNI_AKTYWNOSCI = 240

    def generate_ranking_table(target_date, active_only=False):
        target_dt = pd.to_datetime(target_date)
        df_temp = df[df["Date"] <= target_dt].copy()
        if df_temp.empty:
            return pd.DataFrame()
        
        df_temp = df_temp.sort_values(by="Date")
        ranking = df_temp.drop_duplicates(subset=["Name"], keep="last").copy()
        
        races_count = df_temp.groupby("Name").size().to_dict()
        ranking["Races"] = ranking["Name"].map(races_count)
        ranking["Days_Inactive"] = (target_dt - ranking["Date"]).dt.days
        
        tabela = ranking[["Nat_Computed", "Name", "Elo_After", "Races", "Date", "Event", "Days_Inactive"]].copy()
        tabela.columns = ["NAT", "NAME", "RATING", "Races", "Last Date", "Last Event", "Days Inactive"]
        
        tabela["RATING"] = tabela["RATING"].round().astype(int)
        tabela["Last Date"] = pd.to_datetime(tabela["Last Date"]).dt.strftime("%Y-%m-%d")
        tabela["NAT"] = tabela["NAT"].map(lambda x: FLAG_MAP.get(str(x).strip(), str(x).strip()))
        
        if active_only:
            tabela = tabela[(tabela["Races"] >= MIN_STARTY) & (tabela["Days Inactive"] <= DNI_AKTYWNOSCI)]
            
        tabela = tabela.sort_values(by=["RATING", "Races"], ascending=[False, False]).reset_index(drop=True)
        tabela.index = tabela.index + 1
        tabela.index.name = "RK"
        return tabela

    # SECTION 1: LIVE RANKINGS
    if app_mode == "🏆 Live Rankings":
        st.markdown('<div class="main-title">🏆 Nordic Combined Real-Time Elo Rankings</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Welcome to the official dashboard.</div>', unsafe_allow_html=True)
        
        latest_date = df["Date"].max()
        tab1, tab2 = st.tabs(["🔒 Official Ranking (Active Only)", "🌍 General Ranking (All-Time Pool)"])
        
        with tab1:
            st.subheader(f"Current Official Standing (as of {latest_date.strftime('%Y-%m-%d')})")
            tbl_official = generate_ranking_table(latest_date, active_only=True)
            st.dataframe(tbl_official, use_container_width=True, height=600)
            
        with tab2:
            st.subheader("All-Time Historical Database View")
            tbl_general = generate_ranking_table(latest_date, active_only=False)
            st.dataframe(tbl_general, use_container_width=True, height=600)

    # SECTION 2: HISTORICAL TIME MACHINE
    elif app_mode == "⏳ Historical Time Machine":
        st.markdown('<div class="main-title">⏳ Historical Ranking Time Machine</div>', unsafe_allow_html=True)
        
        min_date = df["Date"].min().to_pydatetime()
        max_date = df["Date"].max().to_pydatetime()
        selected_date = st.date_input("Select Historical Target Date:", value=datetime(2003, 3, 1), min_value=min_date, max_value=max_date)
        
        st.subheader(f"Reconstructed Standing on: {selected_date.strftime('%Y-%m-%d')}")
        tbl_historic = generate_ranking_table(selected_date, active_only=True)
        
        if not tbl_historic.empty:
            st.dataframe(tbl_historic, use_container_width=True, height=600)
        else:
            st.warning("No athletes matched the activity rules on this date.")

    # SECTION 3: ATHLETE LIFELINE EXPLORER
    elif app_mode == "📈 Athlete Lifeline Explorer":
        st.markdown('<div class="main-title">📈 Athlete Elo Lifeline Career Explorer</div>', unsafe_allow_html=True)
        
        athlete_list = sorted(df["Name"].unique())
        selected_athlete = st.selectbox("Select Athlete Profile Name:", athlete_list, index=0)
        
        df_ath = df[df["Name"] == selected_athlete].sort_values(by="Date").reset_index(drop=True)
        df_ath["Race_No"] = range(1, len(df_ath) + 1)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Career Races", len(df_ath))
        m2.metric("Peak Career Elo", int(round(df_ath["Elo_After"].max())))
        m3.metric("Lowest Career Elo", int(round(df_ath["Elo_After"].min())))
        m4.metric("Last Registered Elo", int(round(df_ath["Elo_After"].iloc[-1])))
        
        race_numbers = df_ath["Race_No"].tolist()
        elo_after_points = df_ath["Elo_After"].tolist()
        events_list = df_ath["Event"].tolist()
        dates_clean = df_ath["Date"].dt.strftime("%Y-%m-%d").tolist()
        ranks_list = df_ath["Rank"].astype(int).tolist()
        elo_before_list = df_ath["Elo_Before"].round().astype(int).tolist()
        delta_list = df_ath["Delta_Elo"].round(1).tolist()
        elo_after_list = df_ath["Elo_After"].round().astype(int).tolist()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=race_numbers, 
            y=elo_after_points, 
            mode="lines+markers",
            name="Elo Points", 
            line=dict(color="#4dadf7", width=3), 
            marker=dict(size=4),
            hovertemplate=(
                "<b>%{text}</b><br><br>"
                "Date: %{customdata[0]}<br>"
                "Rank: <b>%{customdata[1]}</b><br>"
                "Elo Before: %{customdata[2]}<br>"
                "Delta: <b>%{customdata[3]}</b><br>"
                "New Elo: <b>%{customdata[4]}</b>"
                "<extra></extra>"
            ),
            text=events_list,
            customdata=[
                [dates_clean[i], ranks_list[i], elo_before_list[i], delta_list[i], elo_after_list[i]]
                for i in range(len(df_ath))
            ]
        ))
        
        fig.add_shape(
            type="line", x0=1, y0=1500, x1=len(df_ath), y1=1500, 
            line=dict(color="#ff6b6b", width=1.5, dash="dash")
        )
        
        num_ticks = min(6, len(df_ath))
        tick_idx = [int(i * (len(df_ath) - 1) / (num_ticks - 1)) for i in range(num_ticks)]
        
        fig.update_layout(
            xaxis=dict(
                tickmode="array", 
                tickvals=[race_numbers[idx] for idx in tick_idx], 
                ticktext=[f"Race {race_numbers[idx]}<br>({dates_clean[idx]})" for idx in tick_idx],
                gridcolor="#2d3139",
                zerolinecolor="#2d3139"
            ),
            yaxis=dict(
                gridcolor="#2d3139",
                zerolinecolor="#2d3139"
            ),
            xaxis_title="Career Progress Timeline", 
            yaxis_title="Elo Rating Points Scale",
            hovermode="x unified", 
            template="plotly_dark",
            margin=dict(l=40, r=40, t=20, b=40), 
            height=500,
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117"
        )
        
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Critical error loading application state: {e}")
