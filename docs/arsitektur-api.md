# Arsitektur dan Implementasi API

## Ringkasan

Tahap akhir dari metodologi ini adalah mengemas training pipeline yang telah optimal ke dalam sebuah API (Application Programming Interface) tingkat produksi. Model akhir diserialisasi ke dalam format biner `.pkl` menggunakan `joblib` agar dapat dimuat secara efisien oleh framework backend **Flask**. Arsitektur implementasi API ini dirancang dengan alur kerja sebagai berikut:

---

## Teknologi dan Framework API

| Komponen | Teknologi |
|----------|-----------|
| Web framework | **Flask 3.1.x** — WSGI framework ringan, eksplisit sebagai requirement proyek |
| Runtime server | **Flask dev server** (`flask run`) — digunakan untuk development lokal dan container Docker |
| Serialisasi model | **joblib 1.5.3** — format baku scikit-learn untuk pipeline persisten |
| Kontainerisasi | **Docker** — `python:3.13-slim` sebagai base image |

---

## Mekanisme Pemuatan Model (Model Loading)

Pipeline yang sudah dilatih (`TfidfVectorizer` + `LGBMClassifier`) disimpan ke `model.pkl` melalui `joblib.dump()`. Saat server dijalankan, mekanisme pemuatan dilakukan dalam dua skema:

### Warm Start (model.pkl sudah ada)

```
app.py startup
  └─ model.py: load_model()
       └─ joblib.load("model.pkl")
            └─ Pipeline([TfidfVectorizer, LGBMClassifier]) siap di memori
```

Model langsung dimuat dalam hitungan detik. Tidak perlu training ulang.

### Cold Start (model.pkl belum ada)

```
app.py startup
  └─ model.py: load_model() → return None
       └─ app.py: panggil train()
            └─ train.py: load dataset → train pipeline → RandomizedSearchCV
                 └─ joblib.dump("model.pkl")
                      └─ load_model() ulang → pipeline siap
```

Skema cold start memungkinkan API langsung berfungsi di lingkungan baru (misalnya container Docker pertama kali) tanpa perlu build stage terpisah.

---

## Endpoint API

### `POST /predict`

Endpoint utama untuk klasifikasi berita.

**Request:**

| Bagian | Tipe | Wajib | Deskripsi |
|--------|------|-------|-----------|
| `title` | `string` | Tidak | Judul berita |
| `text` | `string` | Ya | Isi/konten berita |

```
POST /predict
Content-Type: application/json

{
  "title": "Breaking News",
  "text": "Article content here"
}
```

**Response (200):**

```json
{
  "status": "ok",
  "label": "fake"
}
```

Nilai `label`: `"fake"` atau `"true"`.

**Kode Status HTTP:**

| Status | Kondisi |
|--------|---------|
| `200` | Prediksi berhasil |
| `400` | Input kosong setelah pembersihan |
| `503` | Model belum termuat di memori |
| `500` | Error saat inferensi |

### `GET /`

Menampilkan dokumentasi API dalam format HTML.

### `GET /info`

Mengembalikan metadata API dalam format JSON, termasuk daftar endpoint dan struktur request/response.

---

## Alur Kerja Pengolahan Request

Berikut adalah langkah-langkah dari teks mentah masuk hingga hasil prediksi keluar:

```
┌──────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│Client│────>│  Flask   │────>│ clean_text│────>│ Pipeline │────>│  JSON    │
│HTTP  │     │  Route   │     │(preproses)│     │ (memory) │     │ Response │
└──────┘     └──────────┘     └───────────┘     └──────────┘     └──────────┘
```

1. **Client mengirim request** — Klien mengirim HTTP POST ke `/predict` dengan body JSON berisi `title` dan `text`.

2. **Validasi input** — Flask mengekstrak JSON payload. Jika payload tidak valid, dikembalikan error 400.

3. **Pembersihan teks** — Fungsi `clean_text()` dari `preprocess.py` melakukan:
   - Normalisasi huruf kecil (*lowercasing*)
   - Hapus karakter non-alfabetik
   - Hapus *stop words* bahasa Inggris
   - Deduplikasi token
   - Normalisasi spasi

4. **Inferensi otomatis** — Teks yang sudah bersih langsung dimasukkan ke objek `Pipeline([TfidfVectorizer, LGBMClassifier])` yang telah dimuat di memori server. Karena TF-IDF dan LightGBM sudah terintegrasi dalam satu pipeline, proses vektorisasi dan klasifikasi terjadi secara sekuensial dalam satu panggilan `model.predict()`.

5. **Interpretasi hasil** — Nilai numerik hasil prediksi (`1` = true, `0` = fake) dikonversi ke label string.

6. **Response** — API mengembalikan JSON `{"status": "ok", "label": "fake|true"}` dengan status HTTP 200.

---

## Deployment Production-Ready

### Kontainerisasi dengan Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dataset/ ./dataset/
COPY app.py model.py preprocess.py train.py ./
EXPOSE 5000
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
```

Arsitektur Docker:
- Model **tidak dibake** ke dalam image — dilatih saat pertama kali container berjalan
- Dataset disertakan dalam image untuk keperluan cold-start training
- Container port 5000 di-*expose* untuk diakses dari host

---



## Diagram Arsitektur Lengkap

```
┌─────────────────────────────────────────────────┐
│                   Docker Container              │
│                                                 │
│  ┌────────────┐   ┌────────────┐  │
│  │    Flask   │──>│ model.pkl  │  │
│  │ (dev server│   │ (Pipeline) │  │
│  │  atau CMD) │   │            │  │
│  └────────────┘   └────────────┘  │
│                      │                          │
│                      ▼                          │
│               ┌──────────────┐                  │
│               │ preprocess.py│                  │
│               │ clean_text() │                  │
│               └──────────────┘                  │
│                                                 │
│  ┌──────────┐   ┌───────────────┐               │
│  │ dataset/ │──>│ train.py      │               │
│  │(CSV)     │   │(cold start)   │               │
│  └──────────┘   └───────────────┘               │
└─────────────────────────────────────────────────┘
         │
         │ port 5000
         ▼
┌──────────────────┐
│    Client / curl │
│  (pengguna akhir)│
└──────────────────┘
```

---

## Ringkasan

Arsitektur API ini menjembatani model machine learning (LightGBM + TF-IDF Pipeline) dengan pengguna akhir melalui REST API yang ringan, mudah digunakan, dan siap dijalankan di lingkungan lokal maupun container Docker. Dengan mekanisme cold-start yang otomatis, API dapat berjalan tanpa memerlukan proses build atau training manual — cukup jalankan, dan API siap menerima prediksi.
