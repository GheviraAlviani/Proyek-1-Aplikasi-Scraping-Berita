import sys
from PyQt5.QtWidgets import QApplication
import gui            
from scraper import scrape  

# =================================================================
# Fungsi Jembatan & Anti-Freeze
# =================================================================
def logika_thread_zahra(self):
    self.log_message.emit("[INFO] Menjalankan robot Selenium...")
    
    # Kurir penerima dari scraper.py
    def on_data_diterima(data_dari_scraper):
        if not self._running:
            return False # Suruh scraper berhenti
        
        # Samakan format kunci dictionary
        data_gui = {
            'judul': data_dari_scraper.get('judul', '-'),
            'tanggal': data_dari_scraper.get('tanggal', '-'),
            'link': data_dari_scraper.get('url', '-'), 
            'isi': data_dari_scraper.get('isi', '-')
        }
        
        # Lempar data ke Tabel GUI
        self.article_found.emit(data_gui)
        return True 

    # Jalankan Selenium
    try:
        scrape(url_utama=self.url, callback=on_data_diterima, limit=self.limit)
        
        if self._running:
            self.log_message.emit("[INFO] Scraping selesai dengan normal.")
        else:
            self.log_message.emit("[WARNING] Scraping dihentikan paksa.")
            
    except Exception as e:
        self.log_message.emit(f"[ERROR] Terjadi kesalahan: {e}")

    self.finished.emit()

# =================================================================
# INJEKSI KODE 
# =================================================================
gui.ScraperWorker.run = logika_thread_zahra

# =================================================================
# SAKLAR UTAMA APLIKASI
# =================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = gui.NewsScraperApp()
    window.show()
    sys.exit(app.exec_())