"""
News Scraper Desktop App
PyQt5 Frontend
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QProgressBar, QDateEdit,
    QCheckBox, QTextEdit, QSplitter, QGroupBox,
    QHeaderView, QStatusBar, QSpinBox, QFrame,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor


# =============================================================
#  SCRAPER WORKER
# =============================================================
class ScraperWorker(QThread):
    article_found = pyqtSignal(dict)
    progress      = pyqtSignal(int)
    log_message   = pyqtSignal(str)
    finished      = pyqtSignal()

    def __init__(self, url, date_from=None, date_to=None, limit=0):
        super().__init__()
        self.url       = url
        self.date_from = date_from
        self.date_to   = date_to
        self.limit     = limit
        self._running  = True

    def stop(self):
        self._running = False

    def run(self):
        self.log_message.emit("[INFO] Worker thread dimulai.")
        self.log_message.emit(f"[INFO] Target URL : {self.url}")
        if self.date_from:
            self.log_message.emit(f"[INFO] Filter: {self.date_from} s/d {self.date_to}")
        if self.limit:
            self.log_message.emit(f"[INFO] Limit: {self.limit} berita")
        self.finished.emit()


# =============================================================
#  MAIN WINDOW
# =============================================================
class NewsScraperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker    = None
        self.row_count = 0
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("News Scraper")
        self.setMinimumSize(1100, 720)
        self._apply_stylesheet()

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(10)

        root.addWidget(self._build_header())
        root.addWidget(self._build_control_panel())

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._build_table_panel())
        splitter.addWidget(self._build_log_panel())
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        root.addWidget(self._build_progress_section())
        self._build_status_bar()

    # ----------------------------------------------------------
    #  HEADER
    # ----------------------------------------------------------
    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("headerFrame")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("News Scraper")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setObjectName("headerTitle")

        subtitle = QLabel("Portal Berita Aggregator")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setObjectName("headerSubtitle")

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(subtitle)
        return frame

    # ----------------------------------------------------------
    #  PANEL KONTROL
    # ----------------------------------------------------------
    def _build_control_panel(self):
        group = QGroupBox("Pengaturan Scraping")
        group.setFont(QFont("Arial", 10, QFont.Bold))

        outer = QVBoxLayout(group)
        outer.setSpacing(10)

        # Baris 1: URL
        url_row = QHBoxLayout()

        lbl_url = QLabel("URL Portal Berita:")
        lbl_url.setFixedWidth(140)
        lbl_url.setFont(QFont("Arial", 10))

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://www.contoh-portal-berita.com/kategori/"
        )
        self.url_input.setFont(QFont("Arial", 10))
        self.url_input.setMinimumHeight(34)

        url_row.addWidget(lbl_url)
        url_row.addWidget(self.url_input)
        outer.addLayout(url_row)

        # Baris 2: Filter Tanggal + Limit
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self.date_filter_chk = QCheckBox("Filter Tanggal")
        self.date_filter_chk.setFont(QFont("Arial", 10))
        self.date_filter_chk.stateChanged.connect(self._toggle_date_filter)

        lbl_dari = QLabel("Dari:")
        lbl_dari.setFont(QFont("Arial", 10))

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setMinimumHeight(32)
        self.date_from.setEnabled(False)
        self.date_from.setFont(QFont("Arial", 10))

        lbl_sampai = QLabel("Sampai:")
        lbl_sampai.setFont(QFont("Arial", 10))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setMinimumHeight(32)
        self.date_to.setEnabled(False)
        self.date_to.setFont(QFont("Arial", 10))

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)

        lbl_limit = QLabel("Maks. Berita:")
        lbl_limit.setFont(QFont("Arial", 10))

        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(0, 10000)
        self.limit_spin.setValue(0)
        self.limit_spin.setSpecialValueText("Tanpa Batas")
        self.limit_spin.setMinimumHeight(32)
        self.limit_spin.setFont(QFont("Arial", 10))
        self.limit_spin.setToolTip("0 = Tidak ada batas jumlah berita")

        filter_row.addWidget(self.date_filter_chk)
        filter_row.addWidget(lbl_dari)
        filter_row.addWidget(self.date_from)
        filter_row.addWidget(lbl_sampai)
        filter_row.addWidget(self.date_to)
        filter_row.addWidget(sep)
        filter_row.addWidget(lbl_limit)
        filter_row.addWidget(self.limit_spin)
        filter_row.addStretch()
        outer.addLayout(filter_row)

        # Baris 3: Tombol
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_start = QPushButton("Mulai Scraping")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setMinimumHeight(38)
        self.btn_start.setFont(QFont("Arial", 10, QFont.Bold))
        self.btn_start.clicked.connect(self.start_scraping)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setMinimumHeight(38)
        self.btn_stop.setFont(QFont("Arial", 10, QFont.Bold))
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_scraping)

        self.btn_clear = QPushButton("Bersihkan Tabel")
        self.btn_clear.setMinimumHeight(38)
        self.btn_clear.setFont(QFont("Arial", 10))
        self.btn_clear.clicked.connect(self.clear_table)

        self.btn_export = QPushButton("Ekspor CSV")
        self.btn_export.setMinimumHeight(38)
        self.btn_export.setFont(QFont("Arial", 10))
        self.btn_export.clicked.connect(self.export_csv)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_export)
        outer.addLayout(btn_row)

        return group

    # ----------------------------------------------------------
    #  TABEL HASIL
    # ----------------------------------------------------------
    def _build_table_panel(self):
        group = QGroupBox("Hasil Berita")
        group.setFont(QFont("Arial", 10, QFont.Bold))

        layout = QVBoxLayout(group)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Judul", "Tanggal", "Link", "Isi Singkat"]
        )
        self.table.setFont(QFont("Arial", 9))
        self.table.horizontalHeader().setFont(QFont("Arial", 9, QFont.Bold))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setWordWrap(False)

        layout.addWidget(self.table)
        return group

    # ----------------------------------------------------------
    #  LOG AREA
    # ----------------------------------------------------------
    def _build_log_panel(self):
        group = QGroupBox("Log Aktivitas")
        group.setFont(QFont("Arial", 10, QFont.Bold))

        layout = QVBoxLayout(group)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Courier", 9))
        self.log_area.setMaximumHeight(140)
        self.log_area.setPlaceholderText("Log scraping akan muncul di sini...")

        layout.addWidget(self.log_area)
        return group

    # ----------------------------------------------------------
    #  PROGRESS BAR
    # ----------------------------------------------------------
    def _build_progress_section(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel("Progress:")
        lbl.setFont(QFont("Arial", 9))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")

        self.lbl_count = QLabel("0 artikel ditemukan")
        self.lbl_count.setFont(QFont("Arial", 9))
        self.lbl_count.setFixedWidth(160)
        self.lbl_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(lbl)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.lbl_count)
        return frame

    # ----------------------------------------------------------
    #  STATUS BAR
    # ----------------------------------------------------------
    def _build_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(
            "Siap. Masukkan URL dan klik 'Mulai Scraping'."
        )

    # ----------------------------------------------------------
    #  STYLESHEET
    # ----------------------------------------------------------
    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0f1117;
                color: #e2e8f0;
            }
            #headerFrame {
                background: #1a1f2e;
                border: 1px solid #2d3748;
                border-radius: 8px;
            }
            #headerTitle    { color: #63b3ed; border: none; }
            #headerSubtitle { color: #718096; border: none; }

            QGroupBox {
                border: 1px solid #2d3748;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px 8px 8px 8px;
                color: #a0aec0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #90cdf4;
            }

            QLabel { color: #e2e8f0; }

            QLineEdit, QSpinBox, QDateEdit {
                background-color: #1a202c;
                border: 1px solid #2d3748;
                border-radius: 4px;
                padding: 4px 8px;
                color: #e2e8f0;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus {
                border-color: #4299e1;
            }

            QCheckBox { color: #a0aec0; }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1px solid #4a5568;
                border-radius: 3px;
                background: #1a202c;
            }
            QCheckBox::indicator:checked {
                background-color: #4299e1;
                border-color: #4299e1;
            }

            QPushButton {
                background-color: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 5px;
                padding: 6px 18px;
                color: #e2e8f0;
            }
            QPushButton:hover   { background-color: #4a5568; }
            QPushButton:pressed { background-color: #2b6cb0; }
            QPushButton:disabled { color: #4a5568; border-color: #2d3748; }

            #btnStart {
                background-color: #2b6cb0;
                border-color: #3182ce;
                color: #ffffff;
            }
            #btnStart:hover   { background-color: #3182ce; }
            #btnStart:pressed { background-color: #2c5282; }

            #btnStop {
                background-color: #742a2a;
                border-color: #c53030;
                color: #ffffff;
            }
            #btnStop:hover   { background-color: #c53030; }
            #btnStop:pressed { background-color: #63171b; }

            QTableWidget {
                background-color: #1a202c;
                alternate-background-color: #171e2b;
                gridline-color: #2d3748;
                border: 1px solid #2d3748;
                border-radius: 4px;
                color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #2d3748;
                color: #90cdf4;
                padding: 6px;
                border: none;
                border-right: 1px solid #4a5568;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #2b6cb0;
                color: #ffffff;
            }

            QTextEdit {
                background-color: #111827;
                border: 1px solid #2d3748;
                border-radius: 4px;
                color: #68d391;
            }

            QProgressBar {
                border: 1px solid #2d3748;
                border-radius: 4px;
                background-color: #1a202c;
                text-align: center;
                color: #e2e8f0;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2b6cb0, stop:1 #4299e1
                );
                border-radius: 3px;
            }

            QStatusBar { background: #0f1117; color: #718096; }
            QSplitter::handle { background: #2d3748; height: 2px; }

            QCalendarWidget QWidget {
                background-color: #1a202c;
                color: #e2e8f0;
            }
        """)

    # ==========================================================
    #  LOGIKA TOMBOL & SLOT
    # ==========================================================

    def _toggle_date_filter(self, state):
        enabled = (state == Qt.Checked)
        self.date_from.setEnabled(enabled)
        self.date_to.setEnabled(enabled)

    def start_scraping(self):
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "URL Kosong",
                                "Masukkan URL portal berita terlebih dahulu.")
            return
        if not url.startswith("http"):
            QMessageBox.warning(self, "URL Tidak Valid",
                                "URL harus diawali dengan http:// atau https://")
            return

        date_from = None
        date_to   = None
        if self.date_filter_chk.isChecked():
            date_from = self.date_from.date().toPyDate()
            date_to   = self.date_to.date().toPyDate()
            if date_from > date_to:
                QMessageBox.warning(self, "Tanggal Tidak Valid",
                                    "'Dari' tidak boleh lebih besar dari 'Sampai'.")
                return

        limit = self.limit_spin.value()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"Scraping dimulai: {url}")
        self._log(f"[START] URL: {url}")

        self.worker = ScraperWorker(url, date_from, date_to, limit)
        self.worker.article_found.connect(self._on_article_found)
        self.worker.progress.connect(self._on_progress)
        self.worker.log_message.connect(self._log)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def stop_scraping(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._log("[STOP] Permintaan berhenti dikirim ke worker.")
            self.status_bar.showMessage("Menghentikan proses...")

    @pyqtSlot(dict)
    def _on_article_found(self, data: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)

        judul       = data.get("judul",   "-")
        tanggal     = data.get("tanggal", "-")
        link        = data.get("link",    "-")
        isi         = data.get("isi",     "")
        isi_singkat = isi[:120] + ("..." if len(isi) > 120 else "")

        self.table.setItem(row, 0, QTableWidgetItem(judul))
        self.table.setItem(row, 1, QTableWidgetItem(tanggal))
        self.table.setItem(row, 2, QTableWidgetItem(link))
        self.table.setItem(row, 3, QTableWidgetItem(isi_singkat))

        self.table.item(row, 2).setForeground(QColor("#63b3ed"))

        self.row_count = row + 1
        self.lbl_count.setText(f"{self.row_count} artikel ditemukan")
        self.table.scrollToBottom()

    @pyqtSlot(int)
    def _on_progress(self, value: int):
        self.progress_bar.setValue(value)

    @pyqtSlot()
    def _on_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)
        msg = f"Selesai. Total {self.row_count} artikel ditemukan."
        self.status_bar.showMessage(msg)
        self._log(f"[DONE] {msg}")

    def _log(self, text: str):
        self.log_area.append(text)

    def clear_table(self):
        self.table.setRowCount(0)
        self.row_count = 0
        self.lbl_count.setText("0 artikel ditemukan")
        self.progress_bar.setValue(0)
        self._log("[CLEAR] Tabel dibersihkan.")
        self.status_bar.showMessage("Tabel dibersihkan.")

    def export_csv(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Tidak Ada Data",
                                    "Belum ada data untuk diekspor.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", "hasil_berita.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return

        import csv
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Judul", "Tanggal", "Link", "Isi Singkat"])
            for r in range(self.table.rowCount()):
                row_data = [
                    self.table.item(r, c).text()
                    for c in range(self.table.columnCount())
                ]
                writer.writerow(row_data)

        self._log(f"[EXPORT] Data berhasil disimpan ke: {path}")
        self.status_bar.showMessage(f"Ekspor selesai: {path}")
        QMessageBox.information(self, "Ekspor Berhasil",
                                f"Data berhasil disimpan ke:\n{path}")


# =============================================================
#  ENTRY POINT
# =============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = NewsScraperApp()
    window.show()
    sys.exit(app.exec_())
