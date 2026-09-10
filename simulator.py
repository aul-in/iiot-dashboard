import random
import time

# Batas aman untuk masing-masing sensor (dipakai nanti buat alarm)
BATAS_SUHU = 80        # derajat Celcius
BATAS_ARUS = 9          # Ampere
BATAS_VIBRASI = 0.6     # mm/s

def buat_data_sensor():
    """Menghasilkan satu set data sensor palsu (pura-pura dari mesin asli)."""
    suhu = round(random.uniform(60, 90), 2)
    arus = round(random.uniform(5, 10), 2)
    vibrasi = round(random.uniform(0.2, 0.7), 2)
    return suhu, arus, vibrasi

def cek_status(suhu, arus, vibrasi):
    """Cek apakah ada angka yang melewati batas aman."""
    if suhu > BATAS_SUHU or arus > BATAS_ARUS or vibrasi > BATAS_VIBRASI:
        return "KRITIS"
    return "NORMAL"

# Loop utama: jalan terus-menerus tiap 2 detik
while True:
    suhu, arus, vibrasi = buat_data_sensor()
    status = cek_status(suhu, arus, vibrasi)

    print(f"Suhu: {suhu} C | Arus: {arus} A | Vibrasi: {vibrasi} mm/s | Status: {status}")

    time.sleep(2)  # jeda 2 detik sebelum generate data berikutnya