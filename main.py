from gui_d3 import ScraperWorker  # import ScraperWorker dari file GUI
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor

def mulai_scraping(self):
    url_input = self.input_url.text().strip()  # Ambil URL dari input user
    limit_val = self.limit_spin.value()        # Ambil limit dari GUI
    date_from = self.date_from.date().toPyDate() if self.date_filter_chk.isChecked() else None
    date_to   = self.date_to.date().toPyDate()   if self.date_filter_chk.isChecked() else None

    # 1. Buat instance ScraperWorker
    self.thread = ScraperWorker(url=url_input, date_from=date_from, date_to=date_to, limit=limit_val)

    # 2. Hubungkan Signal (Kurir) ke Slot (Fungsi Penerima di GUI)
    self.thread.article_found.connect(self.tambah_baris_tabel)
    self.thread.progress.connect(self.update_progress_bar)
    self.thread.log_message.connect(self.tampilkan_log)  # ini bisa untuk error/log
    self.thread.finished.connect(self.scraping_selesai)
        
    # 3. Nyalakan Thread (Ini akan memanggil fungsi run() di latar belakang)
    self.thread.start()

# --- FUNGSI SLOT PENERIMA ---
def tambah_baris_tabel(self, data):
    row = self.table.rowCount()
    self.table.insertRow(row)

    self.table.setItem(row, 0, QTableWidgetItem(data.get("judul", "-")))
    self.table.setItem(row, 1, QTableWidgetItem(data.get("tanggal", "-")))
    self.table.setItem(row, 2, QTableWidgetItem(data.get("url", "-")))
    
    isi = data.get("isi", "")
    isi_singkat = isi[:120] + ("..." if len(isi) > 120 else "")
    self.table.setItem(row, 3, QTableWidgetItem(isi_singkat))
    
    self.table.item(row, 2).setForeground(QColor("#63b3ed"))

    self.row_count += 1
    self.lbl_count.setText(f"{self.row_count} artikel ditemukan")
    self.table.scrollToBottom()

def update_progress_bar(self, nilai):
    self.progress_bar.setValue(nilai)

def hentikan_scraping(self):
    if hasattr(self, 'thread'):
        self.thread.stop() # Panggil fungsi stop di dalam thread
