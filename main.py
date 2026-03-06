def mulai_scraping(self):
    url_input = self.input_url.text() # Ambil URL dari kolom input
        
    # 1. Buat instance dari Thread yang kamu buat di Langkah 2
    self.thread = ScraperThread(url=url_input)
        
    # 2. Hubungkan Signal (Kurir) ke Slot (Fungsi Penerima di GUI)
    self.thread.data_fetched.connect(self.tambah_baris_tabel)
    self.thread.progress_updated.connect(self.update_progress_bar)
    self.thread.error_occurred.connect(self.tampilkan_error)
    self.thread.finished_scraping.connect(self.scraping_selesai)
        
    # 3. Nyalakan Thread (Ini akan memanggil fungsi run() di latar belakang)
    self.thread.start()

# --- FUNGSI SLOT PENERIMA ---
def tambah_baris_tabel(self, data):
    # Tambahkan data['judul'], data['tanggal'], dll ke QTableWidget
    # Ini dikerjakan bersama Anggota 2
    print("Data diterima di GUI:", data['judul']) 

def update_progress_bar(self, nilai):
    self.progress_bar.setValue(nilai)

def hentikan_scraping(self):
    if hasattr(self, 'thread'):
        self.thread.stop() # Panggil fungsi stop di dalam thread
