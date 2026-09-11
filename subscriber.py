import json
import sqlite3
import time
import requests
import paho.mqtt.client as mqtt
from supabase import create_client

BROKER_ALAMAT = "localhost"
BROKER_PORT = 1883
TOPIC = "pabrik/mesin1/data"
NAMA_DATABASE = "data_mesin.db"

# --- Supabase (database cloud) ---
SUPABASE_URL = "https://arkkaenfzsgkfzwmoqpl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFya2thZW5menNna2Z6d21vcXBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMjM5NzUsImV4cCI6MjEwNDU5OTk3NX0.erRS8-0VrgcC7BdUWruutssRmk3e_Z3CMX_LbODLqqk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Telegram Bot ---
TELEGRAM_TOKEN = "7709393541:AAE0xvGz4bQj655L13ZO5ywOZSYiHiuDw6k"
TELEGRAM_CHAT_ID = "8795412428"

# Supaya tidak spam notifikasi tiap 2 detik, kasih jeda minimal antar notifikasi
JEDA_MINIMAL_NOTIFIKASI = 60  # detik
waktu_notifikasi_terakhir = 0

def kirim_notifikasi_telegram(data):
    """Kirim pesan ke Telegram saat status KRITIS terdeteksi."""
    global waktu_notifikasi_terakhir
    sekarang = time.time()

    # Cek jeda, biar tidak spam notifikasi tiap 2 detik terus-terusan
    if sekarang - waktu_notifikasi_terakhir < JEDA_MINIMAL_NOTIFIKASI:
        return

    pesan = (
        "🚨 *ALARM KRITIS - Mesin 01*\n\n"
        f"🌡️ Suhu: {data['suhu']} °C\n"
        f"⚡ Arus: {data['arus']} A\n"
        f"📳 Vibrasi: {data['vibrasi']} mm/s\n\n"
        "Segera periksa kondisi mesin!"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": pesan,
            "parse_mode": "Markdown"
        })
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
            suhu REAL,
            arus REAL,
            vibrasi REAL,
            status TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database lokal '{NAMA_DATABASE}' siap dipakai.")

def simpan_ke_database_lokal(data):
    conn = sqlite3.connect(NAMA_DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO riwayat_sensor (suhu, arus, vibrasi, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (data['suhu'], data['arus'], data['vibrasi'], data['status'], data['timestamp']))
    conn.commit()
    conn.close()

def simpan_ke_supabase(data):
    try:
        supabase.table("riwayat_sensor").insert({
            "suhu": data['suhu'],
            "arus": data['arus'],
            "vibrasi": data['vibrasi'],
            "status": data['status'],
            "timestamp": data['timestamp']
        }).execute()
    except Exception as e:
        print(f"Gagal kirim ke Supabase: {e}")

def saat_terhubung(client, userdata, flags, reason_code, properties):
    print(f"Berhasil terhubung ke broker MQTT! (kode: {reason_code})")
    client.subscribe(TOPIC)
    print(f"Mendengarkan data di topic '{TOPIC}'...\n")

def saat_ada_pesan_masuk(client, userdata, message):
    data = json.loads(message.payload.decode())

    simpan_ke_database_lokal(data)
    simpan_ke_supabase(data)

    if data['status'] == "KRITIS":
        kirim_notifikasi_telegram(data)

    print(f"Diterima & disimpan (lokal + cloud) -> Suhu: {data['suhu']} C | "
          f"Arus: {data['arus']} A | Vibrasi: {data['vibrasi']} mm/s | Status: {data['status']}")

siapkan_database_lokal()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subscriber-dashboard")
client.on_connect = saat_terhubung
client.on_message = saat_ada_pesan_masuk

client.connect(BROKER_ALAMAT, BROKER_PORT)
client.loop_forever()