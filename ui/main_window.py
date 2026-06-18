# -*- coding: utf-8 -*-
"""
ui/main_window.py — NTH Fiyat Takip Ana Penceresi

Özellikler:
  - Modern dark theme
  - Yeniden boyutlandırılabilir pencere
  - QThread tabanlı arka plan arama (UI donmaz)
  - 3 platform kart görünümü (Trendyol, N11, Hepsiburada)
  - Fiyat geçmişi paneli
  - Geçmiş aramalar listesi (tıkla tekrar ara)
"""

import os
import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QPixmap

from config import (
    APP_NAME, APP_VERSION, APP_AUTHOR, GITHUB_URL,
    ASSETS_DIR, PRODUCTS, BRAND_ICONS,
)
from database.db_manager import DatabaseManager
from workers.search_worker import SearchWorker
from ui.result_card import ResultCard

logger = logging.getLogger(__name__)


def load_qss(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.connect()
        self.worker: SearchWorker | None = None
        self.result_cards: dict[str, ResultCard] = {}
        self.current_results: dict[str, dict] = {}

        self._setup_window()
        self._setup_ui()
        self._apply_style()
        self._populate_brands()
        self._load_recent_searches()

    # ------------------------------------------------------------------ #
    #  Pencere Ayarları
    # ------------------------------------------------------------------ #

    def _setup_window(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        icon_path = os.path.join(ASSETS_DIR, "ico.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setMinimumSize(960, 680)
        self.resize(1100, 720)

    def _apply_style(self):
        qss_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        qss = load_qss(qss_path)
        if qss:
            self.setStyleSheet(qss)

    # ------------------------------------------------------------------ #
    #  UI Oluşturma
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QtWidgets.QVBoxLayout(central)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(0)

        # --- Başlık Çubuğu ---
        root_layout.addWidget(self._build_header())
        root_layout.addSpacing(14)

        # --- Ana İçerik (splitter: sol filtreler | sağ sonuçlar) ---
        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #30363D; }")

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 800])

        root_layout.addWidget(splitter, stretch=1)

        # --- Durum Çubuğu ---
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet(
            "QStatusBar { background: #161B22; color: #8B949E; "
            "font-size: 11px; border-top: 1px solid #30363D; }"
        )
        self._set_status("Hazır.")

    # --- Başlık Çubuğu ---
    def _build_header(self) -> QtWidgets.QWidget:
        header = QtWidgets.QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(
            "background-color: #161B22; border-radius: 12px; "
            "border: 1px solid #30363D;"
        )
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 12, 0)

        # Logo + başlık
        title_col = QtWidgets.QVBoxLayout()
        title_col.setSpacing(2)

        title = QtWidgets.QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        sub = QtWidgets.QLabel("N11 · Amazon · Hepsiburada — Fiyat Karşılaştırma")
        sub.setObjectName("subtitleLabel")

        title_col.addWidget(title)
        title_col.addWidget(sub)
        layout.addLayout(title_col)
        layout.addStretch()

        # GitHub butonu
        self.github_btn = QtWidgets.QPushButton()
        self.github_btn.setObjectName("githubButton")
        self.github_btn.setFixedSize(44, 44)
        self.github_btn.setToolTip(f"GitHub: @{APP_AUTHOR}")
        self.github_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        gh_icon = os.path.join(ASSETS_DIR, "25231.png")
        if os.path.exists(gh_icon):
            self.github_btn.setIcon(QtGui.QIcon(gh_icon))
            self.github_btn.setIconSize(QtCore.QSize(28, 28))
        self.github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL))
        )
        layout.addWidget(self.github_btn)
        return header

    # --- Sol Panel: Filtreler + Geçmiş ---
    def _build_left_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        panel.setFixedWidth(270)
        panel.setStyleSheet("background: transparent;")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(12)

        # Filtre grubu
        filter_group = QtWidgets.QGroupBox("Filtreler")
        fg_layout = QtWidgets.QVBoxLayout(filter_group)
        fg_layout.setSpacing(10)

        # Marka
        fg_layout.addWidget(self._label("Marka"))
        self.combo_brand = QtWidgets.QComboBox()
        self.combo_brand.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.combo_brand.currentTextChanged.connect(self._on_brand_changed)
        fg_layout.addWidget(self.combo_brand)

        # Model
        fg_layout.addWidget(self._label("Model"))
        self.combo_model = QtWidgets.QComboBox()
        self.combo_model.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        fg_layout.addWidget(self.combo_model)

        # Hafıza
        fg_layout.addWidget(self._label("Hafıza"))
        self.combo_storage = QtWidgets.QComboBox()
        self.combo_storage.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        fg_layout.addWidget(self.combo_storage)

        fg_layout.addSpacing(6)

        # Ara Butonu
        self.search_btn = QtWidgets.QPushButton("🔍  Ara")
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setFixedHeight(44)
        self.search_btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.search_btn.clicked.connect(self._on_search)
        fg_layout.addWidget(self.search_btn)

        layout.addWidget(filter_group)

        # Progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 0)       # sonsuz döngü
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.hide()
        layout.addWidget(self.progress)

        # Geçmiş aramalar
        history_group = QtWidgets.QGroupBox("Son Aramalar")
        hg_layout = QtWidgets.QVBoxLayout(history_group)
        hg_layout.setContentsMargins(6, 6, 6, 6)

        self.history_list = QtWidgets.QListWidget()
        self.history_list.setMaximumHeight(220)
        self.history_list.setAlternatingRowColors(False)
        self.history_list.itemDoubleClicked.connect(self._on_history_double_click)
        self.history_list.setToolTip("Çift tıklayarak tekrar ara")
        hg_layout.addWidget(self.history_list)

        layout.addWidget(history_group)
        layout.addStretch()

        return panel

    # --- Sağ Panel: Kart Sonuçları ---
    def _build_right_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Bilgi etiketi
        self.info_label = QtWidgets.QLabel(
            "Soldaki filtrelerden marka, model ve hafıza seçin, ardından Ara butonuna basın."
        )
        self.info_label.setObjectName("statusLabel")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Kartlar
        cards_layout = QtWidgets.QVBoxLayout()
        cards_layout.setSpacing(12)

        for platform in ["Amazon", "N11", "Hepsiburada"]:
            card = ResultCard(platform)
            self.result_cards[platform] = card
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        layout.addStretch()
        return panel

    # ------------------------------------------------------------------ #
    #  Yardımcı Metodlar
    # ------------------------------------------------------------------ #

    @staticmethod
    def _label(text: str) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet(
            "color: #8B949E; font-size: 11px; font-weight: 600; "
            "text-transform: uppercase; letter-spacing: 0.5px;"
        )
        return lbl

    def _set_status(self, message: str):
        self.status_bar.showMessage(f"  {message}")

    # ------------------------------------------------------------------ #
    #  ComboBox Doldurma
    # ------------------------------------------------------------------ #

    def _populate_brands(self):
        self.combo_brand.blockSignals(True)
        for brand in PRODUCTS:
            icon_file = BRAND_ICONS.get(brand, "")
            icon_path = os.path.join(ASSETS_DIR, icon_file)
            if os.path.exists(icon_path):
                self.combo_brand.addItem(QtGui.QIcon(icon_path), brand)
            else:
                self.combo_brand.addItem(brand)
        self.combo_brand.blockSignals(False)
        self._on_brand_changed(self.combo_brand.currentText())

    def _on_brand_changed(self, brand: str):
        self.combo_model.blockSignals(True)
        self.combo_model.clear()
        models = list(PRODUCTS.get(brand, {}).keys())
        self.combo_model.addItems(models)
        self.combo_model.blockSignals(False)
        self._on_model_changed(self.combo_model.currentText())

    def _on_model_changed(self, model: str):
        brand = self.combo_brand.currentText()
        self.combo_storage.clear()
        storages = PRODUCTS.get(brand, {}).get(model, [])
        self.combo_storage.addItems(storages)

    # ------------------------------------------------------------------ #
    #  Arama
    # ------------------------------------------------------------------ #

    def _on_search(self):
        brand   = self.combo_brand.currentText().strip()
        model   = self.combo_model.currentText().strip()
        storage = self.combo_storage.currentText().strip()

        if not all([brand, model, storage]):
            QtWidgets.QMessageBox.warning(
                self, "Eksik Bilgi", "Lütfen marka, model ve hafıza seçiniz."
            )
            return

        # Önceki worker'ı durdur
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(500)

        # Kartları yükleniyor durumuna geçir
        for card in self.result_cards.values():
            card.set_loading()
        self.current_results.clear()
        self.info_label.setText(
            f"🔍  {brand} {model} {storage} aranıyor…"
        )

        # UI kilitle
        self.search_btn.setEnabled(False)
        self.progress.show()
        self._set_status(f"Aranıyor: {brand} {model} {storage}…")

        # Worker başlat
        self.worker = SearchWorker(brand, model, storage, parent=self)
        self.worker.result_ready.connect(
            lambda data: self._on_result(brand, model, storage, data)
        )
        self.worker.all_finished.connect(
            lambda: self._on_search_finished(brand, model, storage)
        )
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()

    @QtCore.pyqtSlot(dict)
    def _on_result(self, brand: str, model: str, storage: str, data: dict):
        platform = data.get("platform", "")
        self.current_results[platform] = data

        # DB'ye kaydet
        if data.get("success"):
            prev_price = self.db.price_changed(
                brand, model, storage, platform, data["price"]
            )
            self.db.save_result(
                brand, model, storage, platform,
                data.get("product_name", ""),
                data["price"],
                data.get("url", ""),
            )
        else:
            prev_price = None

        # Kartı güncelle (henüz en ucuz bilgisi yok, sonra güncellenecek)
        card = self.result_cards.get(platform)
        if card:
            card.set_result(data, prev_price=prev_price, is_cheapest=False)

    @QtCore.pyqtSlot()
    def _on_search_finished(self, brand: str, model: str, storage: str):
        self.progress.hide()
        self.search_btn.setEnabled(True)
        self._highlight_cheapest()
        self._load_recent_searches()

        success_count = sum(
            1 for d in self.current_results.values() if d.get("success")
        )
        self.info_label.setText(
            f"✅  {brand} {model} {storage} — {success_count}/3 platform sonucu bulundu."
        )
        self._set_status(
            f"Arama tamamlandı — {success_count}/3 platform başarılı."
        )

    @QtCore.pyqtSlot(str)
    def _on_worker_error(self, msg: str):
        self.progress.hide()
        self.search_btn.setEnabled(True)
        self._set_status(f"Hata: {msg}")

    def _highlight_cheapest(self):
        """Başarılı sonuçlar arasında en düşük fiyatlı platforma rozet ekle."""
        prices = {}
        for platform, data in self.current_results.items():
            if data.get("success") and data.get("price"):
                try:
                    raw = data["price"].replace(".", "").replace(",", ".").split()[0]
                    prices[platform] = float(raw)
                except (ValueError, IndexError):
                    pass

        if not prices:
            return

        cheapest = min(prices, key=prices.get)
        for platform, card in self.result_cards.items():
            if self.current_results.get(platform, {}).get("success"):
                is_cheapest = (platform == cheapest)
                data = self.current_results[platform]
                card.set_result(data, is_cheapest=is_cheapest)

    # ------------------------------------------------------------------ #
    #  Geçmiş Aramalar
    # ------------------------------------------------------------------ #

    def _load_recent_searches(self):
        self.history_list.clear()
        searches = self.db.get_recent_searches(limit=15)
        for s in searches:
            text = f"{s['brand']} {s['model']} {s['storage']}"
            item = QtWidgets.QListWidgetItem(text)
            item.setData(Qt.UserRole, s)
            self.history_list.addItem(item)

    def _on_history_double_click(self, item: QtWidgets.QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return
        brand   = data.get("brand", "")
        model   = data.get("model", "")
        storage = data.get("storage", "")

        # Combo'ları ayarla
        idx = self.combo_brand.findText(brand)
        if idx >= 0:
            self.combo_brand.setCurrentIndex(idx)

        QtWidgets.QApplication.processEvents()

        idx = self.combo_model.findText(model)
        if idx >= 0:
            self.combo_model.setCurrentIndex(idx)

        idx = self.combo_storage.findText(storage)
        if idx >= 0:
            self.combo_storage.setCurrentIndex(idx)

        self._on_search()

    # ------------------------------------------------------------------ #
    #  Temizlik
    # ------------------------------------------------------------------ #

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
        self.db.close()
        logger.info("Uygulama kapatıldı.")
        super().closeEvent(event)
