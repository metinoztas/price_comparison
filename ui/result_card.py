# -*- coding: utf-8 -*-
"""
ui/result_card.py — Platform sonuç kartı widget'ı

Her platform (Trendyol, N11, Hepsiburada) için ayrı bir kart gösterir.
Renk kodlaması, ürün adı, fiyat, geçmiş fiyat ve site linki içerir.
"""

import os
from PyQt5 import QtCore, QtGui, QtWidgets

from config import ASSETS_DIR, PLATFORM_COLORS, PLATFORM_BG_COLORS, GITHUB_URL


# Platform gradyan arka planları
PLATFORM_GRADIENTS = {
    "Amazon":       ("rgba(255,153,0,0.15)",  "rgba(255,153,0,0.04)"),
    "N11":          ("rgba(139,50,229,0.15)",  "rgba(139,50,229,0.04)"),
    "Hepsiburada":  ("rgba(255,80,0,0.15)",   "rgba(255,80,0,0.04)"),
}

PLATFORM_ACCENT = {
    "Amazon":       "#FF9900",
    "N11":          "#8B32E5",
    "Hepsiburada":  "#FF5000",
}


class ResultCard(QtWidgets.QFrame):
    """Bir platformun arama sonucunu gösteren kart widget'ı."""

    link_clicked = QtCore.pyqtSignal(str)

    def __init__(self, platform: str, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.product_url = ""
        self._setup_ui()
        self.set_loading()

    def _setup_ui(self):
        self.setObjectName("resultCard")
        self.setMinimumHeight(180)
        self.setMaximumHeight(220)

        accent = PLATFORM_ACCENT.get(self.platform, "#58A6FF")
        g_start, g_end = PLATFORM_GRADIENTS.get(
            self.platform, ("rgba(88,166,255,0.10)", "rgba(88,166,255,0.03)")
        )

        self.setStyleSheet(f"""
            QFrame#resultCard {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {g_start}, stop:1 {g_end}
                );
                border: 1px solid {accent}55;
                border-radius: 14px;
            }}
            QFrame#resultCard:hover {{
                border-color: {accent};
            }}
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        # --- Üst Satır: Platform adı + ikon ---
        top_row = QtWidgets.QHBoxLayout()

        self.platform_label = QtWidgets.QLabel(self.platform)
        self.platform_label.setStyleSheet(
            f"color: {accent}; font-size: 15px; font-weight: 700; "
            "background: transparent; border: none;"
        )

        self.badge = QtWidgets.QLabel()
        self.badge.setFixedSize(60, 22)
        self.badge.setAlignment(QtCore.Qt.AlignCenter)
        self.badge.hide()

        top_row.addWidget(self.platform_label)
        top_row.addStretch()
        top_row.addWidget(self.badge)
        layout.addLayout(top_row)

        # --- Ürün adı ---
        self.name_label = QtWidgets.QLabel("Aranıyor…")
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet(
            "color: #8B949E; font-size: 12px; background: transparent; border: none;"
        )
        layout.addWidget(self.name_label)

        # --- Fiyat ---
        self.price_label = QtWidgets.QLabel("—")
        self.price_label.setStyleSheet(
            "color: #E6EDF3; font-size: 26px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        layout.addWidget(self.price_label)

        # --- Geçmiş fiyat / değişim ---
        self.history_label = QtWidgets.QLabel("")
        self.history_label.setStyleSheet(
            "color: #8B949E; font-size: 11px; font-style: italic; "
            "background: transparent; border: none;"
        )
        layout.addWidget(self.history_label)

        layout.addStretch()

        # --- Alt Satır: Link butonu ---
        bottom_row = QtWidgets.QHBoxLayout()
        self.link_btn = QtWidgets.QPushButton("Siteye Git →")
        self.link_btn.setObjectName("linkButton")
        self.link_btn.setFixedHeight(30)
        self.link_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.link_btn.clicked.connect(self._on_link_clicked)
        self.link_btn.setEnabled(False)

        bottom_row.addStretch()
        bottom_row.addWidget(self.link_btn)
        layout.addLayout(bottom_row)

    def set_loading(self):
        """Yükleniyor durumuna geç."""
        self.name_label.setText("Aranıyor…")
        self.price_label.setText("—")
        self.history_label.setText("")
        self.link_btn.setEnabled(False)
        self.badge.hide()
        self.price_label.setStyleSheet(
            "color: #484F58; font-size: 26px; font-weight: 800; "
            "background: transparent; border: none;"
        )

    def set_result(self, data: dict, prev_price: str = None,
                   is_cheapest: bool = False):
        """
        Scraping sonucunu kartı güncelle.

        Args:
            data:        ScraperResult.to_dict() çıktısı
            prev_price:  Önceki fiyat (varsa)
            is_cheapest: Bu platform en ucuz mu?
        """
        if not data.get("success"):
            self._set_error(data.get("error", "Veri alınamadı."))
            return

        # Ürün adı
        name = data.get("product_name", "")
        if len(name) > 80:
            name = name[:77] + "…"
        self.name_label.setText(name)
        self.name_label.setStyleSheet(
            "color: #C9D1D9; font-size: 12px; background: transparent; border: none;"
        )

        # Fiyat
        price = data.get("price", "")
        price_color = "#3FB950" if is_cheapest else "#E6EDF3"
        self.price_label.setText(price)
        self.price_label.setStyleSheet(
            f"color: {price_color}; font-size: 26px; font-weight: 800; "
            "background: transparent; border: none;"
        )

        # Geçmiş fiyat
        if prev_price and prev_price != price:
            self.history_label.setText(f"Önceki fiyat: {prev_price}")
        else:
            self.history_label.setText("")

        # En ucuz rozeti
        if is_cheapest:
            self.badge.setText("EN UCUZ ✓")
            self.badge.setStyleSheet(
                "background-color: #3FB95022; color: #3FB950; "
                "border: 1px solid #3FB950; border-radius: 10px; "
                "font-size: 10px; font-weight: 700;"
            )
            self.badge.show()
        else:
            self.badge.hide()

        # Link
        self.product_url = data.get("url", "")
        self.link_btn.setEnabled(bool(self.product_url))

    def _set_error(self, message: str):
        self.name_label.setText("Ürün bulunamadı")
        self.price_label.setText("—")
        self.history_label.setText(message[:70])
        self.price_label.setStyleSheet(
            "color: #F85149; font-size: 26px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        self.link_btn.setEnabled(False)
        self.badge.hide()

    def _on_link_clicked(self):
        if self.product_url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.product_url))
