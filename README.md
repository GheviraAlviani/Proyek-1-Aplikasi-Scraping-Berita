# 📰 Portal Berita Aggregator (News Scraper GUI)

Aplikasi **Portal Berita Aggregator** adalah aplikasi berbasis Python yang digunakan untuk melakukan scraping berita dari portal berita online.  
Aplikasi ini dilengkapi dengan **Graphical User Interface (GUI)** sehingga pengguna dapat mengambil data berita dengan mudah tanpa harus menggunakan command line.

Program ini mengambil informasi berita seperti **judul, tanggal, dan link artikel**, kemudian menampilkannya dalam tabel dan dapat diekspor menjadi file **CSV**.

---

## ✨ Fitur Aplikasi

- Mengambil data berita dari portal berita online
- Menampilkan hasil scraping dalam bentuk tabel
- Progress bar untuk menunjukkan proses scraping
- Log aktivitas scraping
- Pembatas jumlah berita yang diambil (limit)
- Filter berdasarkan rentang tanggal
- Export hasil scraping ke file **CSV**

---

## 🛠️ Teknologi yang Digunakan

Aplikasi ini dibuat menggunakan beberapa library Python:

- **Python**
- **PyQt5** → Untuk membuat GUI
- **Selenium** → Untuk melakukan web scraping
- **Pandas** → Untuk mengolah data dan export CSV

---

## 📂 Struktur Project

portal-berita-aggregator
│
├── main.py # File utama untuk menjalankan aplikasi
├── gui.py # Implementasi tampilan GUI
├── scraper.py # Logika scraping berita
├── requirements.txt # Daftar library yang dibutuhkan
├── .gitignore
│
└── screenshots # Folder dokumentasi tampilan aplikasi
![GUI](screenshots/gui.png)

---

