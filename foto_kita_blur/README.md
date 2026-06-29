# ✌️ foto_kita_blur

Efek kamera real-time berbasis Python — tunjukkan **peace sign** ke kamera, tampilan langsung **blur**. Cocok buat konten transisi atau intro TikTok.

> Bagian dari [trend_tiktok | raincode26](../README.md)

---

## Cara Kerja

| Kondisi | Hasil |
|---|---|
| Tangan menunjukkan ✌️ peace sign | Kamera **blur** |
| Tangan diturunkan / tidak ada tangan | Kamera **normal** |

- Deteksi tangan otomatis menggunakan MediaPipe
- Musik latar berjalan loop otomatis
- Tekan `ESC` atau `TAB` untuk keluar

---

## Requirements

- Python >= 3.10 (diuji di Python 3.12)
- Webcam lokal **atau** HP sebagai kamera (via IP Webcam / DroidCam)

---

## Setup

### 1. Masuk ke folder ini

```bash
cd trend_tiktok/foto_kita_blur
```

### 2. Buat virtual environment

**WSL / Ubuntu / macOS / Linux:**

```bash
python3 -m venv env
source env/bin/activate
```

**Windows:**

```bash
python -m venv env
./env/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Konfigurasi

Buka `foto_kita_blur.py` dan ubah bagian **Configuration** sesuai kebutuhan.

### Ganti Camera Source

Cari baris ini:

```python
CAMERA_SOURCE: str | int = 0
```

| Situasi | Nilai |
|---|---|
| Webcam bawaan laptop/PC | `0` |
| IP Webcam Android | `"http://192.168.x.x:8080/video"` |
| DroidCam Android | `"http://192.168.x.x:4747/video"` |

Contoh pakai HP sebagai kamera:

```python
CAMERA_SOURCE = "http://192.168.1.5:8080/video"
```

> **Tips WSL:** webcam lokal tidak langsung terbaca di WSL, gunakan IP Webcam / DroidCam dari HP sebagai gantinya.

### Ganti File Musik

Taruh file musik di folder yang sama dengan `foto_kita_blur.py`, lalu ubah baris ini:

```python
MUSIC_FILE: str = "music.mp3"
```

Ganti `"music.mp3"` dengan nama file musik kamu:

```python
MUSIC_FILE: str = "nama_lagu_kamu.mp3"
```

> Format yang didukung: `.mp3`, `.ogg`, `.wav`

---

## Jalankan

Pastikan virtual environment sudah aktif, lalu:

```bash
python foto_kita_blur.py
```

### Kontrol

| Input | Fungsi |
|---|---|
| ✌️ Peace sign ke kamera | Aktifkan blur |
| Turunkan tangan | Nonaktifkan blur |
| `ESC` atau `TAB` | Keluar dari program |

---

## Struktur Folder

```
foto_kita_blur/
├── foto_kita_blur.py   # script utama
├── requirements.txt    # daftar dependencies
├── music.mp3           # file musik (taruh di sini, bisa diganti)
└── README.md
```

---

## Credit

Dibuat oleh **arinmusios**
Repo: [raincode26](https://github.com/arinmusios/raincode26)

---

*Gunakan dengan bijak, jangan dipakai untuk hal-hal yang merugikan orang lain.*
