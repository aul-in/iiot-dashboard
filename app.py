import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
from supabase import create_client

SUPABASE_URL = "https://arkkaenfzsgkfzwmoqpl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFya2thZW5menNna2Z6d21vcXBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMjM5NzUsImV4cCI6MjEwNDU5OTk3NX0.erRS8-0VrgcC7BdUWruutssRmk3e_Z3CMX_LbODLqqk"

BATAS_SUHU = 80
BATAS_ARUS = 9
BATAS_VIBRASI = 0.6

st.set_page_config(page_title="Dashboard Mesin Industri", layout="wide", page_icon="🏭")

# --- Styling custom ala panel kontrol pabrik ---
st.markdown("""
<style>
    /* Font teknikal & background dasar gelap */
    .stApp { background-color: #0E1117; }

    /* Judul utama, model HMI header */
    .plant-header {
        background: linear-gradient(90deg, #1A1F2B 0%, #0E1117 100%);
        border-left: 6px solid #00E676;
        padding: 18px 24px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .plant-header h1 {
        margin: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        color: #E6E6E6;
    }
    .plant-header p {
        margin: 4px 0 0 0;
        color: #6E7681;
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }

    /* Kotak status besar */
    .status-box {
        padding: 16px 24px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 20px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .status-normal {
        background-color: rgba(0, 230, 118, 0.1);
        border: 1px solid #00E676;
        color: #00E676;
    }
    .status-kritis {
        background-color: rgba(255, 23, 68, 0.12);
        border: 1px solid #FF1744;
        color: #FF1744;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 23, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0); }
    }

    /* Kartu metrik ala panel indikator */
    .metric-card {
        background-color: #1A1F2B;
        border: 1px solid #2D3340;
        border-radius: 6px;
        padding: 16px 20px;
        font-family: 'Courier New', monospace;
    }
    .metric-label {
        color: #6E7681;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #E6E6E6;
    }
    .metric-value.danger { color: #FF1744; }
    .metric-value.safe { color: #00E676; }
    .metric-limit {
        color: #4A5063;
        font-size: 11px;
        margin-top: 4px;
    }

    /* Rapikan tab jadi lebih tegas ala menu panel */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #1A1F2B;
        padding: 4px;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Courier New', monospace;
        color: #6E7681;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def ambil_data():
    supabase = get_supabase_client()
    response = (
        supabase.table("riwayat_sensor")
        .select("*")
        .order("id", desc=True)
        .limit(100)
        .execute()
    )
    df = pd.DataFrame(response.data)
    if not df.empty:
        df = df.iloc[::-1].reset_index(drop=True)
    return df

def buat_grafik(df, kolom, batas, warna, judul, satuan):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df[kolom], mode='lines+markers', name=judul,
        line=dict(color=warna, width=2), marker=dict(size=5)
    ))
    fig.add_hline(y=batas, line_dash="dash", line_color="#FF1744",
                  annotation_text="BATAS AMAN", annotation_font_color="#FF1744")
    fig.update_layout(
        title=f"{judul} ({satuan})",
        height=450,
        plot_bgcolor="#0E1117",
        paper_bgcolor="#1A1F2B",
        font=dict(family="Courier New, monospace", color="#E6E6E6"),
        xaxis=dict(gridcolor="#2D3340"),
        yaxis=dict(gridcolor="#2D3340"),
    )
    return fig

# --- HEADER ---
st.markdown(f"""
<div class="plant-header">
    <h1>🏭 PLANT MONITORING SYSTEM — MESIN 01</h1>
    <p>DATA SOURCE: SUPABASE CLOUD DB &nbsp;|&nbsp; LAST SYNC: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} &nbsp;|&nbsp; AUTO-REFRESH: 3s</p>
</div>
""", unsafe_allow_html=True)

df = ambil_data()

if df.empty:
    st.warning("⚠ NO DATA STREAM DETECTED — pastikan simulator.py dan subscriber.py berjalan.")
else:
    data_terbaru = df.iloc[-1]
    kritis = data_terbaru['status'] == "KRITIS"

    if kritis:
        st.markdown("""
        <div class="status-box status-kritis">
            🚨 ALARM STATUS: KRITIS — INDIKASI MESIN BERMASALAH
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-box status-normal">
            ✅ SYSTEM STATUS: NORMAL — SELURUH PARAMETER DALAM BATAS AMAN
        </div>
        """, unsafe_allow_html=True)

    # --- Kartu metrik custom ---
    col1, col2, col3 = st.columns(3)
    with col1:
        cls = "danger" if data_terbaru['suhu'] > BATAS_SUHU else "safe"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌡️ Suhu Mesin</div>
            <div class="metric-value {cls}">{data_terbaru['suhu']} °C</div>
            <div class="metric-limit">BATAS: {BATAS_SUHU} °C</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        cls = "danger" if data_terbaru['arus'] > BATAS_ARUS else "safe"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Arus Listrik</div>
            <div class="metric-value {cls}">{data_terbaru['arus']} A</div>
            <div class="metric-limit">BATAS: {BATAS_ARUS} A</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        cls = "danger" if data_terbaru['vibrasi'] > BATAS_VIBRASI else "safe"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📳 Vibrasi</div>
            <div class="metric-value {cls}">{data_terbaru['vibrasi']} mm/s</div>
            <div class="metric-limit">BATAS: {BATAS_VIBRASI} mm/s</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")  # spasi kecil
    st.write("")

    tab_suhu, tab_arus, tab_vibrasi, tab_data = st.tabs(
        ["🌡️ SUHU", "⚡ ARUS", "📳 VIBRASI", "📋 DATA LOG"]
    )

    with tab_suhu:
        st.plotly_chart(buat_grafik(df, 'suhu', BATAS_SUHU, '#00E676', 'Tren Suhu Mesin', '°C'),
                         use_container_width=True)
    with tab_arus:
        st.plotly_chart(buat_grafik(df, 'arus', BATAS_ARUS, '#FFA726', 'Tren Arus Listrik', 'A'),
                         use_container_width=True)
    with tab_vibrasi:
        st.plotly_chart(buat_grafik(df, 'vibrasi', BATAS_VIBRASI, '#7C4DFF', 'Tren Vibrasi', 'mm/s'),
                         use_container_width=True)
    with tab_data:
        st.dataframe(df, use_container_width=True, height=450)

time.sleep(3)
st.rerun()