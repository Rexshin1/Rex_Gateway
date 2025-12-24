# Contoh JSON Per Tab & URL

Berikut adalah detail URL dan format JSON untuk setiap tab.

---

### 1. Tab Power (Listrik)
**Cara Kirim (Trigger di Gateway):**
`POST http://localhost:5001/api/sync/power`

**Tujuan (Target di Cloud):**
`POST {HOST_API}/add_power` (Misal: `http://192.168.1.xxx:5002/api/v1/add_power`)

**JSON Payload:**
```json
[
  {
    "device_id": "ID_018",
    "created_at": "2024-12-16T10:00:00",
    "power": 220.5,
    "voltage": 221.0,
    "current": 1.2,
    "frequency": 50.0,
    "energy": 10.5
  }
]
```

### 2. Tab Water (Air)
**Cara Kirim (Trigger):**
`POST http://localhost:5001/api/sync/water`

**Tujuan (Target):**
`POST {HOST_API}/add_water`

**JSON Payload:**
```json
[
  {
    "device_id": "ID_020",
    "created_at": "2024-12-16T10:00:00",
    "water_level": 80.5,
    "total_volume": 1200.0
  }
]
```

### 3. Tab Gas
**Cara Kirim (Trigger):**
`POST http://localhost:5001/api/sync/gas`

**Tujuan (Target):**
`POST {HOST_API}/add_gas`

**JSON Payload:**
```json
[
  {
    "device_id": "ID_021",
    "created_at": "2024-12-16T10:00:00",
    "gas": 45.2,
    "gas_ppm": 120.5,
    "gas_voltage": 1.5
  }
]
```

### 4. Tab Lux (Cahaya)
**Cara Kirim (Trigger):**
`POST http://localhost:5001/api/sync/lux`

**Tujuan (Target):**
`POST {HOST_API}/add_lux`

**JSON Payload:**
```json
[
  {
    "device_id": "ID_022",
    "created_at": "2024-12-16T10:00:00",
    "lux": 450.0
  }
]
```

### 5. Tab Smoke & Fire
**Cara Kirim (Trigger):**
`POST http://localhost:5001/api/sync/smoke`

**Tujuan (Target):**
`POST {HOST_API}/add_smoke`

**JSON Payload:**
```json
[
  {
    "device_id": "ID_023",
    "created_at": "2024-12-16T10:00:00",
    "smoke": 12.5,
    "fire": 0,
    "temperature": 30.5
  }
]
```

### 6. Tab Weather (Cuaca)
**Cara Kirim (Trigger):**
`POST http://localhost:5001/api/sync/weather`

**Tujuan (Target):**
`POST {HOST_API}/add_weather`

**JSON Payload:**
```json
[
  {
    "device_id": "ID_024",
    "created_at": "2024-12-16T10:00:00",
    "weather": "Cerah",
    "temperature": 32.0
  }
]
```
