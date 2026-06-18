# -*- coding: utf-8 -*-
"""
scrapers/hepsiburada.py — Hepsiburada fiyat scraper'i
Strateji: Once ana sayfayi ziyaret ederek cookie olustur, sonra arama yap.
"""

import logging
import time
import urllib.parse

from .base_scraper import BaseScraper, ScraperResult

logger = logging.getLogger(__name__)


class HepsiburadaScraper(BaseScraper):
    PLATFORM_NAME = "Hepsiburada"

    def search(self, brand: str, model: str, storage: str) -> ScraperResult:
        if brand.lower() in model.lower():
            query_raw = f"{model} {storage}"
        else:
            query_raw = f"{brand} {model} {storage}"

        query_enc  = urllib.parse.quote(query_raw)
        search_url = f"https://www.hepsiburada.com/ara?q={query_enc}"

        # Cookie warm-up
        self.session.headers.update({
            "Referer": "https://www.hepsiburada.com/",
            "Origin":  "https://www.hepsiburada.com",
        })
        warmup = self._get_silent("https://www.hepsiburada.com/")
        if warmup:
            time.sleep(0.5)

        logger.info("[Hepsiburada] Arama sorgusu: %s", query_raw)
        response = self._get(search_url)

        if response is None:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=False,
                url=search_url,
                error="Sunucuya ulasilamadi.",
            )

        soup = self._parse(response.text)

        # Hepsiburada urun kartlari
        product_card = (
            soup.find("li", {"data-test-id": "product-item"})
            or soup.find("li", class_=lambda c: c and "productListContent" in c)
            or soup.find("div", {"class": "product-list-item"})
        )

        if not product_card:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=False,
                url=search_url,
                error="Urun bulunamadi veya sayfa yapisi degisti.",
            )

        # Fiyat
        price_tag = (
            product_card.find("div", {"data-test-id": "price-current-price"})
            or product_card.find("span", {"class": "price-value"})
            or product_card.find("span", class_=lambda c: c and "price" in (c or "").lower())
        )
        # Isim
        name_tag = (
            product_card.find("h3", {"data-test-id": "product-item-name"})
            or product_card.find("span", {"class": "product-title"})
            or product_card.find("h3")
        )
        # Link
        link_tag = product_card.find("a", href=True)
        product_url = link_tag["href"] if link_tag else search_url
        if product_url.startswith("/"):
            product_url = "https://www.hepsiburada.com" + product_url

        if price_tag and name_tag:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=True,
                product_name=name_tag.get_text(strip=True),
                price=price_tag.get_text(strip=True),
                url=product_url,
            )

        return ScraperResult(
            platform=self.PLATFORM_NAME,
            success=False,
            url=search_url,
            error="Fiyat/urun adi ayristirilamadi.",
        )
