import json
import sqlite3
import paho.mqtt.client as mqtt

BROKER_ALAMAT = "localhost"
BROKER_PORT = 1883
TOPIC = "pabrik/mesin1/data"
NAMA_DATABASE = "data_mesin.db"

def siapkan_database():
    """Bikin tabel penyimpanan kalau belum ada. Cuma perlu jalan sekali di awal."""
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
    print(f"Database '{NAMA_DATABASE}' siap dipakai.\n")

def simpan_ke_database(data):
    """Catat satu baris data baru ke database."""
    conn = sqlite3.connect(NAMA_DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO riwayat_sensor (suhu, arus, vibrasi, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (data['suhu'], data['arus'], data['vibrasi'], data['status'], data['timestamp']))
    conn.commit()
    conn.close()

def saat_terhubung(client, userdata, flags, reason_code, properties):
    print(f"Berhasil terhubung ke broker! (kode: {reason_code})")
    client.subscribe(TOPIC)
    print(f"Mendengarkan data di topic '{TOPIC}'...\n")

def saat_ada_pesan_masuk(client, userdata, message):
    data = json.loads(message.payload.decode())

    # Catat ke database
    simpan_ke_database(data)

    print(f"Diterima & disimpan -> Suhu: {data['suhu']} C | Arus: {data['arus']} A | "
          f"Vibrasi: {data['vibrasi']} mm/s | Status: {data['status']}")

# Siapkan database sebelum mulai dengarkan data
siapkan_database()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subscriber-dashboard")
client.on_connect = saat_terhubung
client.on_message = saat_ada_pesan_masuk

client.connect(BROKER_ALAMAT, BROKER_PORT)
client.loop_forever()