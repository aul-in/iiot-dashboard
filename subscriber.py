import json
import sqlite3
import time
import os
import requests
import pandas as pd
import paho.mqtt.client as mqtt
from supabase import create_client
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest

load_dotenv()

BROKER_ALAMAT = "localhost"
BROKER_PORT = 1883
TOPIC = "pabrik/mesin1/data"
NAMA_DATABASE = "data_mesin.db"

# Minimal data historis yang dibutuhkan sebelum model ML mulai dipakai
MINIMAL_DATA_UNTUK_LATIH_MODEL = 30

SUPABASE_URL = "https://arkkaenfzsgkfzwmoqpl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFya2thZW5menNna2Z6d21vcXBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMjM5NzUsImV4cCI6MjEwNDU5OTk3NX0.erRS8-0VrgcC7BdUWruutssRmk3e_Z3CMX_LbODLqqk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
JEDA_MINIMAL_NOTIFIKASI = 3
waktu_notifikasi_terakhir = 0

model_ml = None

def latih_model_anomali():
    """Ambil data historis dari Supabase, lalu latih Isolation Forest dari situ."""
    global model_ml
    try:
        response = (
            supabase.table("riwayat_sensor")
            .select("suhu, arus, vibrasi")
            .order("id", desc=True)
            .limit(500)
            .execute()
        )
        df = pd.DataFrame(response.data)

        if len(df) < MINIMAL_DATA_UNTUK_LATIH_MODEL:
            print(f"⚠ Data historis baru {len(df)} baris, minimal butuh "
                  f"{MINIMAL_DATA_UNTUK_LATIH_MODEL}. Deteksi anomali ML belum aktif dulu.")
            return

        fitur = df[['suhu', 'arus', 'vibrasi']]
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(fitur)
        model_ml = model
        print(f"✅ Model deteksi anomali ML berhasil dilatih dari {len(df)} data historis.\n")
    except Exception as e:
        print(f"Gagal melatih model ML: {e}")

def cek_anomali_ml(data):
    """Kembalikan 'ANOMALI' atau 'NORMAL' berdasarkan prediksi model ML."""
    if model_ml is None:
        return "NORMAL"
    fitur_baru = pd.DataFrame([[data['suhu'], data['arus'], data['vibrasi']]],
                              columns=['suhu', 'arus', 'vibrasi'])
    hasil = model_ml.predict(fitur_baru)
    return "ANOMALI" if hasil[0] == -1 else "NORMAL"

def kirim_notifikasi_telegram(data, alasan):
    global waktu_notifikasi_terakhir
    sekarang = time.time()
    if sekarang - waktu_notifikasi_terakhir < JEDA_MINIMAL_NOTIFIKASI:
        return

    pesan = (
        f"🚨 *ALARM {alasan} - Mesin 01*\n\n"
        f"🌡️ Suhu: {data['suhu']} °C\n"
        f"⚡ Arus: {data['arus']} A\n"
        f"📳 Vibrasi: {data['vibrasi']} mm/s\n\n"
        "Segera periksa kondisi mesin!"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": pesan, "parse_mode": "Markdown"})
        waktu_notifikasi_terakhir = sekarang
        print("📩 Notifikasi Telegram terkirim!")
    except Exception as e:
        print(f"Gagal kirim notifikasi Telegram: {e}")

def siapkan_database_lokal():
    conn = sqlite3.connect(NAMA_DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_sensor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suhu REAL, arus REAL, vibrasi REAL,
            status TEXT, timestamp REAL
        )
    """)
    # Kalau tabel sudah ada dari sebelumnya (tanpa kolom anomali), tambahkan kolomnya di sini.
    # Dibungkus try/except karena akan error kalau kolomnya sudah pernah ditambahkan.
    try:
        cursor.execute("ALTER TABLE riwayat_sensor ADD COLUMN anomali TEXT DEFAULT 'NORMAL'")
        print("Kolom 'anomali' berhasil ditambahkan ke tabel lokal.")
    except sqlite3.OperationalError:
        pass  # kolom sudah ada, tidak masalah

    conn.commit()
    conn.close()
    print(f"Database lokal '{NAMA_DATABASE}' siap dipakai.")

def simpan_ke_database_lokal(data):
    conn = sqlite3.connect(NAMA_DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO riwayat_sensor (suhu, arus, vibrasi, status, timestamp, anomali)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data['suhu'], data['arus'], data['vibrasi'], data['status'],
          data['timestamp'], data['anomali']))
    conn.commit()
    conn.close()

def simpan_ke_supabase(data):
    try:
        supabase.table("riwayat_sensor").insert({
            "suhu": data['suhu'], "arus": data['arus'], "vibrasi": data['vibrasi'],
            "status": data['status'], "timestamp": data['timestamp'],
            "anomali": data['anomali']
        }).execute()
    except Exception as e:
        print(f"Gagal kirim ke Supabase: {e}")

def saat_terhubung(client, userdata, flags, reason_code, properties):
    print(f"Berhasil terhubung ke broker MQTT! (kode: {reason_code})")
    client.subscribe(TOPIC)
    print(f"Mendengarkan data di topic '{TOPIC}'...\n")

def saat_ada_pesan_masuk(client, userdata, message):
    data = json.loads(message.payload.decode())

    data['anomali'] = cek_anomali_ml(data)

    simpan_ke_database_lokal(data)
    simpan_ke_supabase(data)

    if data['status'] == "KRITIS":
        kirim_notifikasi_telegram(data, "KRITIS (Batas Terlampaui)")
    elif data['anomali'] == "ANOMALI":
        kirim_notifikasi_telegram(data, "ANOMALI (Terdeteksi ML)")

    tanda_ml = " 🤖ANOMALI" if data['anomali'] == "ANOMALI" else ""
    print(f"Diterima & disimpan -> Suhu: {data['suhu']} C | Arus: {data['arus']} A | "
          f"Vibrasi: {data['vibrasi']} mm/s | Status: {data['status']}{tanda_ml}")

siapkan_database_lokal()
latih_model_anomali()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subscriber-dashboard")
client.on_connect = saat_terhubung
client.on_message = saat_ada_pesan_masuk

client.connect(BROKER_ALAMAT, BROKER_PORT)
client.loop_forever()