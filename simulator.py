import random
import time
import json
import paho.mqtt.client as mqtt

# Pengaturan koneksi ke broker MQTT lokal (Mosquitto)
BROKER_ALAMAT = "localhost"
BROKER_PORT = 1883
TOPIC = "pabrik/mesin1/data"

# Batas aman untuk masing-masing sensor
BATAS_SUHU = 80
BATAS_ARUS = 9
BATAS_VIBRASI = 0.6

# Bikin "klien" MQTT, semacam identitas simulator ini saat konek ke broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator-mesin1")
client.connect(BROKER_ALAMAT, BROKER_PORT)

def buat_data_sensor():
    suhu = round(random.uniform(60, 90), 2)
    arus = round(random.uniform(5, 10), 2)
    vibrasi = round(random.uniform(0.2, 0.7), 2)
    return suhu, arus, vibrasi

def cek_status(suhu, arus, vibrasi):
    if suhu > BATAS_SUHU or arus > BATAS_ARUS or vibrasi > BATAS_VIBRASI:
        return "KRITIS"
    return "NORMAL"

print(f"Simulator mulai jalan, mengirim data ke topic '{TOPIC}'...")
print("Tekan Ctrl+C untuk berhenti.\n")

while True:
    suhu, arus, vibrasi = buat_data_sensor()
    status = cek_status(suhu, arus, vibrasi)

    # Bungkus data jadi format JSON, supaya gampang dibaca program lain nanti
    payload = json.dumps({
        "suhu": suhu,
        "arus": arus,
        "vibrasi": vibrasi,
        "status": status,
        "timestamp": time.time()
    })

    # Kirim (publish) data ke broker MQTT
    client.publish(TOPIC, payload)

    print(f"Terkirim -> Suhu: {suhu} C | Arus: {arus} A | Vibrasi: {vibrasi} mm/s | Status: {status}")

    time.sleep(2)