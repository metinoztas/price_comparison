# -*- coding: utf-8 -*-
"""
scrapers/base_scraper.py — Tüm scraper'lar için soyut temel sınıf
"""

import logging
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from config import REQUEST_HEADERS, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


class ScraperResult:
    """Bir scraping işleminin sonucunu temsil eder."""

    def __init__(self, platform: str, success: bool,
                 product_name: str = "", price: str = "",
                 url: str = "", error: str = ""):
        self.platform     = platform
        self.success      = success
        self.product_name = product_name
        self.price        = price
        self.url          = url
        self.error        = error

    def to_dict(self) -> dict:
        return {
            "platform":     self.platform,
            "success":      self.success,
            "product_name": self.product_name,
            "price":        self.price,
            "url":          self.url,
            "error":        self.error,
        }

    def __repr__(self):
        return (
            f"<ScraperResult platform={self.platform!r} "
            f"success={self.success} price={self.price!r}>"
        )


class BaseScraper(ABC):
    """Tüm platform scraper'larının türetileceği soyut sınıf."""

    PLATFORM_NAME: str = "Base"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    def _get(self, url: str) -> requests.Response | None:
        """
        Güvenli HTTP GET.
        - 403 gelse bile HTML içeriği varsa kullan (bazı siteler içerik + 403 döndürür)
        - Gerçek ağ/timeout hatalarında None döndür
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            logger.error("[%s] Baglanti hatasi: %s", self.PLATFORM_NAME, exc)
            return None

        # 403 ama sayfa içeriği varsa yine de döndür (Trendyol bazen böyle davranır)
        if response.status_code == 403:
            if len(response.content) > 500:
                logger.warning("[%s] 403 ama icerik mevcut, deneniyor...", self.PLATFORM_NAME)
                return response
            logger.error("[%s] 403 Forbidden - icerik yok: %s", self.PLATFORM_NAME, url)
            return None

        if not response.ok:
            logger.error("[%s] HTTP %s: %s", self.PLATFORM_NAME, response.status_code, url)
            return None

        return response

    def _get_silent(self, url: str) -> requests.Response | None:
        """Cookie warm-up icin sessiz GET — hata durumunda None dondurur, log yazmaz."""
        try:
            response = self.session.get(url, timeout=8)
            return response
        except requests.RequestException:
            return None

    def _parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    @abstractmethod
    def search(self, brand: str, model: str, storage: str) -> ScraperResult:
        """
        Platformda arama yapar ve ScraperResult döndürür.

        Args:
            brand:   Marka adı (ör. "Samsung")
            model:   Model adı (ör. "Galaxy A54")
            storage: Hafıza (ör. "128 GB")
        """
        ...

    def close(self):
        self.session.close()
