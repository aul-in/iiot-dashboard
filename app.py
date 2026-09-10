import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from supabase import create_client

# --- Pengaturan koneksi ke Supabase (database cloud) ---
SUPABASE_URL = "https://arkkaenfzsgkfzwmoqpl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFya2thZW5menNna2Z6d21vcXBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMjM5NzUsImV4cCI6MjEwNDU5OTk3NX0.erRS8-0VrgcC7BdUWruutssRmk3e_Z3CMX_LbODLqqk"

BATAS_SUHU = 80
BATAS_ARUS = 9
BATAS_VIBRASI = 0.6

st.set_page_config(page_title="Dashboard Mesin Industri", layout="wide")

@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def ambil_data():
    """Baca 100 data terbaru dari Supabase, urutkan dari lama ke baru."""
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
        df = df.iloc[::-1].reset_index(drop=True)  # balik urutan: lama -> baru
    return df

st.title("🏭 Dashboard Monitoring Mesin Industri")
st.caption("Data diambil real-time dari database cloud (Supabase)")

df = ambil_data()

if df.empty:
    st.warning("Belum ada data. Pastikan simulator.py dan subscriber.py sedang berjalan di laptop sumber data.")
else:
    data_terbaru = df.iloc[-1]

    if data_terbaru['status'] == "KRITIS":
        st.error("🚨 KRITIS: Indikasi Mesin Bermasalah!")
    else:
        st.success("✅ Status Mesin: NORMAL")

    col1, col2, col3 = st.columns(3)
    col1.metric("Suhu Terbaru", f"{data_terbaru['suhu']} °C",
                delta=f"Batas: {BATAS_SUHU} °C")
    col2.metric("Arus Terbaru", f"{data_terbaru['arus']} A",
                delta=f"Batas: {BATAS_ARUS} A")
    col3.metric("Vibrasi Terbaru", f"{data_terbaru['vibrasi']} mm/s",
                delta=f"Batas: {BATAS_VIBRASI} mm/s")

    st.divider()

    fig_suhu = go.Figure()
    fig_suhu.add_trace(go.Scatter(y=df['suhu'], mode='lines+markers', name='Suhu'))
    fig_suhu.add_hline(y=BATAS_SUHU, line_dash="dash", line_color="red",
                        annotation_text="Batas Aman")
    fig_suhu.update_layout(title="Tren Suhu Mesin (°C)", height=350)
    st.plotly_chart(fig_suhu, use_container_width=True)

    fig_arus = go.Figure()
    fig_arus.add_trace(go.Scatter(y=df['arus'], mode='lines+markers',
                                    name='Arus', line=dict(color='orange')))
    fig_arus.add_hline(y=BATAS_ARUS, line_dash="dash", line_color="red",
                        annotation_text="Batas Aman")
    fig_arus.update_layout(title="Tren Arus Listrik (A)", height=350)
    st.plotly_chart(fig_arus, use_container_width=True)

    fig_vibrasi = go.Figure()
    fig_vibrasi.add_trace(go.Scatter(y=df['vibrasi'], mode='lines+markers',
                                       name='Vibrasi', line=dict(color='purple')))
    fig_vibrasi.add_hline(y=BATAS_VIBRASI, line_dash="dash", line_color="red",
                           annotation_text="Batas Aman")
    fig_vibrasi.update_layout(title="Tren Vibrasi (mm/s)", height=350)
    st.plotly_chart(fig_vibrasi, use_container_width=True)

    st.divider()
    st.subheader("Data Mentah (100 terakhir)")
    st.dataframe(df, use_container_width=True)

time.sleep(3)
st.rerun()