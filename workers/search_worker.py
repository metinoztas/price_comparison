# -*- coding: utf-8 -*-
"""
workers/search_worker.py — Arka plan thread'inde çoklu platform araması

QThread kullanılarak UI'nın donması engellenir.
ThreadPoolExecutor ile 3 platform paralel taranır.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt5.QtCore import QThread, pyqtSignal

from scrapers.amazon      import AmazonScraper
from scrapers.n11         import N11Scraper
from scrapers.hepsiburada import HepsiburadaScraper

logger = logging.getLogger(__name__)

SCRAPERS = [AmazonScraper, N11Scraper, HepsiburadaScraper]


class SearchWorker(QThread):
    """
    Sinyaller:
        result_ready(dict)  — Her platform tamamlandığında bir kez çağrılır
        all_finished()      — Tüm platformlar bitti
        error(str)          — Genel hata mesajı
    """

    result_ready = pyqtSignal(dict)
    all_finished = pyqtSignal()
    error        = pyqtSignal(str)

    def __init__(self, brand: str, model: str, storage: str, parent=None):
        super().__init__(parent)
        self.brand   = brand
        self.model   = model
        self.storage = storage
        self._stopped = False

    def run(self):
        # Gercek arama sorgusunu hesapla (marka tekrari olmadan)
        if self.brand.lower() in self.model.lower():
            query_display = f"{self.model} {self.storage}"
        else:
            query_display = f"{self.brand} {self.model} {self.storage}"

        logger.info("SearchWorker basladi — %s", query_display)
        try:
            with ThreadPoolExecutor(max_workers=3) as pool:
                futures = {
                    pool.submit(self._run_scraper, ScraperClass): ScraperClass
                    for ScraperClass in SCRAPERS
                }
                for future in as_completed(futures):
                    if self._stopped:
                        break
                    result = future.result()
                    if result is not None:
                        self.result_ready.emit(result)
        except Exception as exc:
            logger.exception("SearchWorker genel hata: %s", exc)
            self.error.emit(str(exc))
        finally:
            self.all_finished.emit()
            logger.info("SearchWorker tamamlandı.")

    def _run_scraper(self, ScraperClass) -> dict | None:
        scraper = ScraperClass()
        try:
            result = scraper.search(self.brand, self.model, self.storage)
            return result.to_dict()
        except Exception as exc:
            logger.error(
                "[%s] Scraper hatası: %s",
                ScraperClass.PLATFORM_NAME, exc
            )
            return {
                "platform": ScraperClass.PLATFORM_NAME,
                "success": False,
                "product_name": "",
                "price": "",
                "url": "",
                "error": str(exc),
            }
        finally:
            scraper.close()

    def stop(self):
        self._stopped = True
