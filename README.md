# 🏭 Dashboard Monitoring Mesin Industri (IIoT)

Dashboard real-time untuk memonitor kondisi mesin industri (suhu, arus listrik, dan vibrasi) menggunakan arsitektur IIoT dengan protokol MQTT, dilengkapi sistem alarm otomatis untuk deteksi kondisi kritis.

## 🎯 Latar Belakang

Proyek ini dibuat untuk mensimulasikan sistem monitoring mesin di lingkungan industri, mirip dengan HMI (Human-Machine Interface) yang digunakan di ruang kontrol pabrik. Alih-alih membaca data statis dari file, sistem ini membangun pipeline data real-time menggunakan protokol komunikasi yang benar-benar dipakai di dunia IIoT.

## 🏗️ Arsitektur Sistem

```
[Simulator Sensor] --MQTT--> [Broker Mosquitto] --MQTT--> [Subscriber] --> [SQLite DB] --> [Dashboard Streamlit]
```

1. **Simulator** (`simulator.py`) — menghasilkan data sensor (suhu, arus, vibrasi) secara berkala dan mengirimkannya via protokol MQTT
2. **Broker MQTT** (Mosquitto) — perantara komunikasi data antar komponen, dijalankan secara lokal (self-hosted)
3. **Subscriber** (`subscriber.py`) — mendengarkan data dari broker dan menyimpannya ke database
4. **Database** (SQLite) — menyimpan riwayat data sensor untuk keperluan analisis tren
5. **Dashboard** (`app.py`) — menampilkan data secara visual dengan grafik interaktif dan sistem alarm

## ✨ Fitur

- 📊 Grafik interaktif tren suhu, arus, dan vibrasi (bisa di-zoom dan digeser)
- 🚨 Sistem alarm otomatis — kotak peringatan merah muncul saat data melewati ambang batas aman
- 🔄 Auto-refresh setiap 3 detik untuk simulasi pengalaman real-time
- 💾 Penyimpanan riwayat data menggunakan database SQLite
- 📡 Komunikasi data menggunakan protokol MQTT (standar industri untuk IIoT)

## 🛠️ Teknologi yang Digunakan

| Komponen | Teknologi |
|---|---|
| Bahasa pemrograman | Python |
| Dashboard | Streamlit |
| Visualisasi data | Plotly |
| Komunikasi data | MQTT (Mosquitto) |
| Database | SQLite |
| Pengolahan data | Pandas |

## 🚀 Cara Menjalankan

### Prasyarat
- Python 3.9+
- Mosquitto MQTT Broker sudah terinstall dan berjalan sebagai service

### Instalasi

```bash
# Clone repository ini
git clone https://github.com/aul-in/iiot-dashboard.git
cd iiot-dashboard

# Buat virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install streamlit paho-mqtt plotly pandas
```

### Menjalankan Sistem

Sistem ini terdiri dari 3 program yang perlu dijalankan bersamaan di terminal terpisah:

```bash
# Terminal 1 - Jalankan simulator sensor
python simulator.py

# Terminal 2 - Jalankan subscriber (penyimpan data)
python subscriber.py

# Terminal 3 - Jalankan dashboard
streamlit run app.py
```

Buka browser ke `http://localhost:8501` untuk melihat dashboard.

## 📈 Rencana Pengembangan Selanjutnya

- [ ] Deploy ke Streamlit Community Cloud
- [ ] Implementasi deteksi anomali menggunakan Machine Learning (Isolation Forest)
- [ ] Tambah fitur notifikasi (email/WhatsApp) saat status kritis terdeteksi
- [ ] Migrasi database ke InfluxDB untuk performa time-series yang lebih baik

## 👤 Author

Dibuat sebagai proyek pembelajaran IIoT dan portofolio data engineering.