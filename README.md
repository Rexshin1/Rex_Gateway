


# 🚀 REX GATEWAY

**Rex Gateway** adalah sistem middleware IoT canggih yang menghubungkan berbagai sensor dan controller dengan server via protokol MQTT dan HTTP REST API. Dibangun dengan Flask (Python), aplikasi ini menawarkan dashboard real-time yang cerdas, manajemen device yang mudah, dan visualisasi data yang akurat.

![Dashboard Preview](flask_server/app/static/assets/img/logo.png)

## ✨ Fitur Utama (New Updates)

### 1. Smart Dashboard 📊
- **Real-time Monitoring**: Update data sensor setiap 2 detik tanpa refresh halaman.
- **Intelligent Data Parsing**: Mendeteksi tipe data sensor secara otomatis (Jarak, Suhu, Kelembaban, Gas, dll) meskipun Device ID sama.
- **Unit display**: Menampilkan satuan yang relevan (`cm`, `%`, `°C`, `Watt`, `Lux`) secara otomatis.

### 2. Device Management 📱
- Mendukung berbagai macam sensor dalam satu gateway.
- Status indicator (Online/Offline) berbasis ping response.
- Fitur Add/Edit/Delete device yang user-friendly.

### 3. User System & Security 🔐
- Authentication (Login/Register) dengan password hashing.
- Role-based Access (Admin vs User).
- Profile Management (Upload Avatar, Edit Info).

---

## 📡 Supported Sensors
Aplikasi ini mendukung berbagai parameter sensor, antara lain:
| Tipe Sensor | Satuan | Keterangan |
|-------------|--------|------------|
| Ultrasonic / Distance | `cm` | Mengukur jarak atau level air |
| Humidity | `%` | Kelembaban udara |
| Temperature | `°C` | Suhu ruangan/mesin |
| Power Meter | `Watt` | Konsumsi daya listrik |
| Lux Sensor | `Lux` | Intensitas cahaya |
| Gas Detector | `(Gas)` | Deteksi kebocoran gas |
| Smoke Detector | `(Smoke)` | Deteksi asap kebakaran |
| Water Level | `cm` | Sensor ketinggian air |
| Weather Station | `Raw` | Data cuaca komprehensif |

---

## 🛠 Teknologi

*   **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Paho-MQTT.
*   **Database**: SQLite (Default) / MySQL Compatible.
*   **Frontend**: HTML5, Jinja2 Template, Bootstrap, jQuery (AJAX Realtime).
*   **System**: Threading untuk multi-tasking (Web Server + MQTT Client).

---

## 📥 Instalasi & Penggunaan

### 1. Clone Repository
```bash
git clone https://github.com/Rexshin1/Rex_Gateway.git
cd Rex_Gateway
```

### 2. Setup Environment
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
python main.py
```
Akses di browser: `http://localhost:5000`

---

## 📂 Struktur Project
```
.
├── config/              # Konfigurasi Database & App
├── core/                # Core Logic (MQTT, Sensor, Network)
├── flask_server/
│   ├── app/
│   │   ├── controller/  # Logic Backend (Controller)
│   │   ├── model/       # Database Models
│   │   ├── views/       # HTML Templates
│   │   └── static/      # CSS, JS, Images, Uploads
├── main.py              # Entry Point Aplikasi
└── requirements.txt     # Daftar Library Python
```

---

_Project ini dikembangkan untuk kebutuhan monitoring IoT yang handal dan fleksibel._
**© 2026 Rex Gateway Project**
