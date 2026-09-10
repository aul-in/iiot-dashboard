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

st.set_page_config(page_title="Plant Monitoring", layout="wide", page_icon="🏭")

# ============ STYLING ============
st.markdown("""
<style>
    .stApp { background-color: #0F1218; }
    #MainMenu, footer, header {visibility: hidden;}

    section[data-testid="stSidebar"] {
        background-color: #161B24;
        border-right: 1px solid #232838;
    }

    .topbar {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 24px;
    }
    .topbar h1 {
        font-family: 'Segoe UI', sans-serif;
        font-size: 26px; font-weight: 700; color: #F2F3F5; margin: 0;
    }
    .topbar-sub { color: #6B7280; font-size: 13px; margin-top: 2px; }

    .badge-live {
        background-color: rgba(0, 230, 118, 0.12);
        color: #00E676; border: 1px solid rgba(0,230,118,0.35);
        padding: 6px 14px; border-radius: 20px;
        font-size: 12px; font-weight: 600; letter-spacing: 0.5px;
    }

    .card {
        background-color: #161B24;
        border: 1px solid #232838;
        border-radius: 16px;
        padding: 20px 22px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    .card-title {
        color: #9AA3B2; font-size: 13px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 2px;
    }

    .alarm-strip {
        border-radius: 14px; padding: 16px 22px; margin-bottom: 22px;
        font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 15px;
        display: flex; align-items: center; gap: 10px;
    }
    .alarm-ok { background: rgba(0,230,118,0.10); border: 1px solid rgba(0,230,118,0.3); color: #00E676; }
    .alarm-bad { background: rgba(255,23,68,0.12); border: 1px solid rgba(255,23,68,0.35); color: #FF5C7A; }

    .side-title { color: #F2F3F5; font-size: 18px; font-weight: 700; margin-bottom: 0px;}
    .side-sub { color: #6B7280; font-size: 12px; margin-bottom: 20px; }
    .side-label { color: #6B7280; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 18px; margin-bottom: 6px;}
    .side-item { color: #C7CBD4; font-size: 13px; padding: 6px 0; border-bottom: 1px solid #1F2430; }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161B24; border: 1px solid #232838;
        border-radius: 10px; color: #9AA3B2; padding: 8px 16px;
        font-family: 'Segoe UI', sans-serif; font-size: 13px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E2A22 !important; color: #00E676 !important;
        border-color: rgba(0,230,118,0.4) !important;
    }

    table.logtable { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif; }
    table.logtable th {
        text-align: left; color: #6B7280; font-size: 11px; text-transform: uppercase;
        padding: 10px 12px; border-bottom: 1px solid #232838;
    }
    table.logtable td {
        color: #D3D7DE; font-size: 13px; padding: 10px 12px; border-bottom: 1px solid #1A1F2B;
    }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; }
    .badge-normal { background: rgba(0,230,118,0.12); color: #00E676; }
    .badge-kritis { background: rgba(255,23,68,0.15); color: #FF5C7A; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def ambil_data():
    supabase = get_supabase_client()
    response = (
        supabase.table("riwayat_sensor").select("*")
        .order("id", desc=True).limit(100).execute()
    )
    df = pd.DataFrame(response.data)
    if not df.empty:
        df = df.iloc[::-1].reset_index(drop=True)
    return df

def buat_gauge(nilai, batas, judul, satuan, warna):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=nilai,
        number={'suffix': f" {satuan}", 'font': {'size': 28, 'color': '#F2F3F5'}},
        title={'text': judul, 'font': {'size': 13, 'color': '#9AA3B2'}},
        gauge={
            'axis': {'range': [0, batas * 1.3], 'tickcolor': '#3A4152', 'tickfont': {'color': '#6B7280', 'size': 9}},
            'bar': {'color': warna, 'thickness': 0.28},
            'bgcolor': '#1A1F2B',
            'borderwidth': 0,
            'steps': [
                {'range': [0, batas], 'color': '#1E2430'},
                {'range': [batas, batas * 1.3], 'color': 'rgba(255,23,68,0.18)'},
            ],
            'threshold': {'line': {'color': '#FF1744', 'width': 3}, 'thickness': 0.8, 'value': batas}
        }
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="#161B24", font={'family': "Segoe UI, sans-serif"}
    )
    return fig

def buat_line_chart(df, kolom, batas, warna, judul, satuan):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df[kolom], mode='lines', name=judul,
        line=dict(color=warna, width=2.5), fill='tozeroy',
        fillcolor=warna.replace('rgb', 'rgba').replace(')', ',0.08)') if 'rgb' in warna else warna
    ))
    fig.add_hline(y=batas, line_dash="dash", line_color="#FF5C7A",
                  annotation_text="BATAS AMAN", annotation_font_color="#FF5C7A")
    fig.update_layout(
        title=f"{judul} ({satuan}) — 100 Data Terakhir",
        height=380, plot_bgcolor="#161B24", paper_bgcolor="#161B24",
        font=dict(family="Segoe UI, sans-serif", color="#D3D7DE"),
        xaxis=dict(gridcolor="#232838, "),
        yaxis=dict(gridcolor="#232838"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown('<div class="side-title">🏭 PlantWatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-sub">Industrial IoT Monitoring</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">Unit Terpantau</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item">⚙️ Mesin 01 — Produksi Utama</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">Ambang Batas Alarm</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="side-item">🌡️ Suhu &nbsp; &gt; {BATAS_SUHU} °C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="side-item">⚡ Arus &nbsp; &gt; {BATAS_ARUS} A</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="side-item">📳 Vibrasi &nbsp; &gt; {BATAS_VIBRASI} mm/s</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-label">Sumber Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item">☁️ Supabase Cloud DB</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-item">📡 Protokol: MQTT</div>', unsafe_allow_html=True)

# ============ TOP BAR ============
col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown(f"""
    <div class="topbar">
        <div>
            <h1>Dashboard Monitoring Mesin</h1>
            <div class="topbar-sub">Update terakhir: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown('<div style="text-align:right; margin-top:8px;"><span class="badge-live">● LIVE</span></div>', unsafe_allow_html=True)

df = ambil_data()

if df.empty:
    st.warning("⚠ Belum ada data. Pastikan simulator.py dan subscriber.py sedang berjalan.")
else:
    data_terbaru = df.iloc[-1]
    kritis = data_terbaru['status'] == "KRITIS"

    if kritis:
        st.markdown('<div class="alarm-strip alarm-bad">🚨 &nbsp; ALARM AKTIF — Indikasi mesin bermasalah, segera periksa unit.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alarm-strip alarm-ok">✅ &nbsp; Seluruh parameter mesin dalam kondisi normal.</div>', unsafe_allow_html=True)

    # --- Gauge cards ---
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(data_terbaru['suhu'], BATAS_SUHU, "SUHU MESIN", "°C", "#00E676"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with g2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(data_terbaru['arus'], BATAS_ARUS, "ARUS LISTRIK", "A", "#FFA726"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with g3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_gauge(data_terbaru['vibrasi'], BATAS_VIBRASI, "VIBRASI", "mm/s", "#7C4DFF"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # --- Tren chart tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Tren Suhu", "⚡ Tren Arus", "📳 Tren Vibrasi", "📋 Log Data"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_line_chart(df, 'suhu', BATAS_SUHU, '#00E676', 'Suhu Mesin', '°C'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_line_chart(df, 'arus', BATAS_ARUS, '#FFA726', 'Arus Listrik', 'A'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(buat_line_chart(df, 'vibrasi', BATAS_VIBRASI, '#7C4DFF', 'Vibrasi', 'mm/s'), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        rows_html = ""
        for _, row in df.iloc[::-1].head(25).iterrows():
            badge_class = "badge-kritis" if row['status'] == "KRITIS" else "badge-normal"
            waktu = datetime.fromtimestamp(row['timestamp']).strftime('%H:%M:%S')
            rows_html += f"""
            <tr>
                <td>{waktu}</td>
                <td>{row['suhu']} °C</td>
                <td>{row['arus']} A</td>
                <td>{row['vibrasi']} mm/s</td>
                <td><span class="badge {badge_class}">{row['status']}</span></td>
            </tr>
            """
        st.markdown(f"""
        <table class="logtable">
            <tr><th>Waktu</th><th>Suhu</th><th>Arus</th><th>Vibrasi</th><th>Status</th></tr>
            {rows_html}
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

time.sleep(3)
st.rerun()