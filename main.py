# -*- coding: utf-8 -*-
"""
main.py — NTH Fiyat Takip Uygulaması — Giriş Noktası
"""

import sys
import io
import logging
import traceback

# Windows konsolunu UTF-8'e zorunlu al (cp1252 Türkçe karakter sorununu çözer)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from PyQt5 import QtWidgets, QtCore

from config import LOG_PATH, APP_NAME
from ui.main_window import MainWindow


def setup_logging():
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
    )
    # Konsola UTF-8 akışıyla yaz
    try:
        utf8_stream = io.TextIOWrapper(
            sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
        )
    except AttributeError:
        utf8_stream = sys.stdout
    console = logging.StreamHandler(utf8_stream)
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logging.getLogger().addHandler(console)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Yakalanmamış istisnaları logla ve kullanıcıya bildir."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical(
        "Yakalanmamış istisna:",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    QtWidgets.QMessageBox.critical(
        None,
        "Beklenmeyen Hata",
        f"Bir hata oluştu:\n{exc_type.__name__}: {exc_value}\n\n"
        f"Detaylar için '{LOG_PATH}' dosyasına bakın.",
    )


def main():
    setup_logging()
    sys.excepthook = handle_exception

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("metinz42")

    # Yüksek DPI desteği
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()
    logging.info("Uygulama başlatıldı.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
