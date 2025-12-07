# 🎬 Video XL — Alat Ekstensi & Penggabung Video Profesional  
**Perpanjang durasi video, looping video/audio, gabungkan banyak video dengan transisi fade, dukungan GPU NVENC, dan sistem cache pintar.**

`video-xl.py` adalah script utilitas berbasis Python untuk:
- 🔁 **Memperpanjang durasi video** menggunakan looping video + audio  
- 🎞️ **Menggabungkan banyak file MP4** dengan transisi fade in/out  
- ⚡ **Mendukung GPU NVENC** untuk render super cepat  
- 🧠 Menggunakan **cache pintar** agar proses looping tidak diulang setiap menjalankan script  

Cocok untuk content creator, editor video, developer automasi, atau pengguna umum.

## ✨ Fitur Utama

### 🔁 Extend / Loop Video
- Loop video + audio hingga durasi target tercapai  
- Efek **fade-in / fade-out** otomatis  
- Proses looping hanya dilakukan sekali (cache)  
- Opsi membersihkan cache setelah selesai  

### 🎞️ Gabungkan Banyak Video
- Auto mendeteksi semua file `.mp4` di folder berjalan  
- Menerapkan efek fade antar video  
- Output berupa satu video final  

### ⚡ Akselerasi GPU (NVENC)
- Mendukung encoding via **hevc_nvenc** jika GPU NVIDIA tersedia  
- CPU fallback otomatis bila GPU tidak ada  

### 🧠 Sistem Pintar
- Parse durasi otomatis: `5h`, `30m`, `90s`, atau detik langsung  
- Mode interaktif bila tidak menggunakan argumen  
- Garbage collection dan cleanup otomatis  

## 📦 Persyaratan

### Software
- Python **3.8+**
- **FFmpeg** (wajib)

Cek apakah FFmpeg sudah terpasang:

```bash
ffmpeg -version
```

## Install Lib:
```bash
pip install -r requirements.txt
```
## Cara Makenya

### Perpanjang menjadi 2 jam
```bash
python video-xl.py -i clip.mp4 -o clip_2jam.mp4 -d 2h
```
### Menggunakan GPU NVENC
```bash
python video-xl.py -i input.mp4 -o long.mp4 -d 1h --gpu --quality high
```
### Extend + hapus cache otomatis
```bash
python video-xl.py -i loop.mp4 -o hasil.mp4 -d 600 --clean
```
## ⚙️ Detail Encoding
### CPU Mode (Default)
```bash
codec: libx264
preset: medium/slow
```

### GPU Mode (NVENC)
```bash
codec: hevc_nvenc
preset: fast/high
```
Pastikan:
- GPU NVIDIA tersedia
- FFmpeg mendukung NVENC

Cek dengan CMD:
```bash
ffmpeg -encoders | findstr nvenc
```
