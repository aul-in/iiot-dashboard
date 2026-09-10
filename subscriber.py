import json
import sqlite3
import paho.mqtt.client as mqtt
from supabase import create_client

BROKER_ALAMAT = "localhost"
BROKER_PORT = 1883
TOPIC = "pabrik/mesin1/data"
NAMA_DATABASE = "data_mesin.db"

# --- Pengaturan koneksi ke Supabase (database cloud) ---
SUPABASE_URL = "https://arkkaenfzsgkfzwmoqpl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFya2thZW5menNna2Z6d21vcXBsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwMjM5NzUsImV4cCI6MjEwNDU5OTk3NX0.erRS8-0VrgcC7BdUWruutssRmk3e_Z3CMX_LbODLqqk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def siapkan_database_lokal():
    """Tetap simpan salinan ke SQLite lokal juga, buat cadangan/testing offline."""
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
    """Kirim data ini ke database cloud, supaya dashboard online bisa baca."""
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

    print(f"Diterima & disimpan (lokal + cloud) -> Suhu: {data['suhu']} C | "
          f"Arus: {data['arus']} A | Vibrasi: {data['vibrasi']} mm/s | Status: {data['status']}")

siapkan_database_lokal()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subscriber-dashboard")
client.on_connect = saat_terhubung
client.on_message = saat_ada_pesan_masuk

client.connect(BROKER_ALAMAT, BROKER_PORT)
client.loop_forever()