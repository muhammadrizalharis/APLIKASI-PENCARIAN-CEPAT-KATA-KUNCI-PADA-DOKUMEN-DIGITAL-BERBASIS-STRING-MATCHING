# ⚡ PDF Keyword Search Engine (Naive • KMP • Boyer–Moore) — FastAPI Web App

> Aplikasi pencarian cepat **kata kunci pada dokumen PDF** berbasis **String Matching Algorithm**:  
> ✅ Naive String Matching  
> ✅ Knuth–Morris–Pratt (KMP)  
> ✅ Boyer–Moore  
> + Web App modern menggunakan **FastAPI** & benchmark performa algoritma.

---

## ✨ Fitur Utama
- 📄 Upload & baca dokumen **PDF text-based**
- 🔎 Pencarian kata kunci dengan 3 algoritma:
  - Naive
  - KMP
  - Boyer–Moore
- ⏱️ Benchmark performa (repeat & warmup)
- 📊 Menampilkan hasil pencarian + waktu eksekusi
- 🌐 Web App berbasis FastAPI (siap demo)

---

## 🧠 Cara Kerja Singkat
1. Upload PDF
2. Ekstraksi teks PDF
3. Input keyword
4. Pilih algoritma (Naive/KMP/Boyer–Moore)
5. Sistem mencari keyword & menghitung waktu proses
6. Output ditampilkan (hasil + performa)

---

## 🗂️ Struktur Folder Project (Rapi & Standar)
```txt
.
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── routes/                  # Endpoint API
│   ├── services/                # Logika ekstraksi & pencarian
│   └── templates/               # HTML (jika ada)
├── scripts/
│   └── benchmark.py             # Script benchmark performa
├── data/
│   └── sample.pdf               # Contoh PDF (opsional)
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalasi & Setup (Windows / Mac / Linux)

### 1) Buat virtual environment (opsional tapi disarankan)
**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependency
```bash
pip install -r requirements.txt
```

Jika belum ada `requirements.txt`, minimal:
```bash
pip install fastapi uvicorn python-multipart PyPDF2
```

---

## 🚀 Menjalankan WEB APP (FastAPI)

Jalankan server:
```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Akses aplikasi:
- 🌐 `http://127.0.0.1:8000`

Dokumentasi otomatis FastAPI:
- 📌 Swagger UI → `http://127.0.0.1:8000/docs`
- 📌 Redoc → `http://127.0.0.1:8000/redoc`

Stop server:
```txt
Ctrl + C
```

---

## 🧪 Menjalankan BENCHMARK Performa Algoritma

Jalankan benchmark biasa:
```powershell
python scripts\benchmark.py --repeat 5 --warmup 1
```

Keterangan parameter:
- `--repeat 5` → pengujian diulang 5 kali agar hasil stabil
- `--warmup 1` → 1 kali pemanasan untuk stabilisasi performa

Jika ingin output real-time (langsung tampil tanpa delay):
```powershell
python -u scripts\benchmark.py --repeat 5 --warmup 1
```

---

## 📊 Hasil yang Diharapkan (Umum)
Biasanya performa algoritma (tergantung PDF & keyword) akan seperti ini:
1. ⚡ **Boyer–Moore** → paling cepat (baik untuk teks panjang)
2. ✅ **KMP** → stabil, cepat, cocok untuk pencarian berulang
3. 🐢 **Naive** → paling sederhana tetapi relatif paling lambat

> Semua algoritma menghasilkan hasil pencarian yang sama, bedanya pada efisiensi waktu proses.

---

## ✅ Catatan Penting
- Disarankan menggunakan **PDF text-based** (bukan hasil scan gambar).
- Jika PDF berupa gambar/scan, perlu OCR agar teks bisa dicari.

---

## 👨‍💻 Author
Project Praktikum / Tugas: **Aplikasi Pencarian Cepat Kata Kunci pada Dokumen PDF berbasis String Matching**  
Universitas Muhammadiyah Makassar (UNISMUH)

---

## 📄 License
Academic / Educational Use Only
