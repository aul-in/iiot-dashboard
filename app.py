import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import time

NAMA_DATABASE = "data_mesin.db"
BATAS_SUHU = 80
BATAS_ARUS = 9
BATAS_VIBRASI = 0.6

st.set_page_config(page_title="Dashboard Mesin Industri", layout="wide")

def ambil_data():
    """Baca semua data dari database, urutkan dari yang terbaru."""
    conn = sqlite3.connect(NAMA_DATABASE)
    df = pd.read_sql_query(
        "SELECT * FROM riwayat_sensor ORDER BY id DESC LIMIT 100", conn
    )
    conn.close()
    # Balik urutan lagi supaya grafik dibaca dari kiri (lama) ke kanan (baru)
    return df.iloc[::-1].reset_index(drop=True)

st.title("🏭 Dashboard Monitoring Mesin Industri")
st.caption("Data diperbarui otomatis tiap 3 detik dari sensor (simulasi)")

df = ambil_data()

if df.empty:
    st.warning("Belum ada data. Pastikan simulator.py dan subscriber.py sedang berjalan.")
else:
    # Ambil data paling baru untuk dicek statusnya
    data_terbaru = df.iloc[-1]

    # ALARM: kalau data terbaru berstatus KRITIS, tampilkan kotak merah
    if data_terbaru['status'] == "KRITIS":
        st.error("🚨 KRITIS: Indikasi Mesin Bermasalah!")
    else:
        st.success("✅ Status Mesin: NORMAL")

    # Tampilkan angka terbaru dalam 3 kotak sejajar
    col1, col2, col3 = st.columns(3)
    col1.metric("Suhu Terbaru", f"{data_terbaru['suhu']} °C",
                delta=f"Batas: {BATAS_SUHU} °C")
    col2.metric("Arus Terbaru", f"{data_terbaru['arus']} A",
                delta=f"Batas: {BATAS_ARUS} A")
    col3.metric("Vibrasi Terbaru", f"{data_terbaru['vibrasi']} mm/s",
                delta=f"Batas: {BATAS_VIBRASI} mm/s")

    st.divider()

    # Grafik tren suhu
    fig_suhu = go.Figure()
    fig_suhu.add_trace(go.Scatter(y=df['suhu'], mode='lines+markers', name='Suhu'))
    fig_suhu.add_hline(y=BATAS_SUHU, line_dash="dash", line_color="red",
                        annotation_text="Batas Aman")
    fig_suhu.update_layout(title="Tren Suhu Mesin (°C)", height=350)
    st.plotly_chart(fig_suhu, use_container_width=True)

    # Grafik tren arus
    fig_arus = go.Figure()
    fig_arus.add_trace(go.Scatter(y=df['arus'], mode='lines+markers',
                                    name='Arus', line=dict(color='orange')))
    fig_arus.add_hline(y=BATAS_ARUS, line_dash="dash", line_color="red",
                        annotation_text="Batas Aman")
    fig_arus.update_layout(title="Tren Arus Listrik (A)", height=350)
    st.plotly_chart(fig_arus, use_container_width=True)

    # Grafik tren vibrasi
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

# Tunggu 3 detik, lalu refresh otomatis seluruh halaman
time.sleep(3)
st.rerun()