# -*- coding: utf-8 -*-
"""
scrapers/amazon.py — Amazon.com.tr fiyat scraper'i

CSS selektorler (dogrulanmis):
  - Urun karti : div[data-component-type='s-search-result']
  - Urun adi   : h2.a-size-base-plus (veya span.a-size-medium icindeki a-text-normal)
  - Fiyat      : span.a-price-whole + span.a-price-fraction
  - Link       : karti icindeki ilk <a href>
"""

import logging
import time
import urllib.parse

from .base_scraper import BaseScraper, ScraperResult

logger = logging.getLogger(__name__)

BASE_URL = "https://www.amazon.com.tr"


class AmazonScraper(BaseScraper):
    PLATFORM_NAME = "Amazon"

    def search(self, brand: str, model: str, storage: str) -> ScraperResult:
        # Model zaten marka iceriyorsa tekrarlama
        if brand.lower() in model.lower():
            query_raw = f"{model} {storage}"
        else:
            query_raw = f"{brand} {model} {storage}"

        query_enc  = urllib.parse.quote(query_raw)
        search_url = f"{BASE_URL}/s?k={query_enc}"

        # Amazon warm-up: cookie + session olustur
        self.session.headers.update({
            "Referer":  BASE_URL + "/",
            "Origin":   BASE_URL,
            "Accept":   "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        })
        self._get_silent(BASE_URL + "/")
        time.sleep(0.3)

        logger.info("[Amazon] Arama sorgusu: %s", query_raw)
        response = self._get(search_url)

        if response is None:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=False,
                url=search_url,
                error="Sunucuya ulasilamadi.",
            )

        soup = self._parse(response.text)

        # Ilk urun kartini bul
        card = soup.find("div", {"data-component-type": "s-search-result"})
        if not card:
            logger.warning("[Amazon] Urun karti bulunamadi — sorgu: %s", query_raw)
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=False,
                url=search_url,
                error="Urun bulunamadi veya sayfa yapisi degisti.",
            )

        # --- Urun adi ---
        name_tag = (
            card.find("h2", class_="a-size-base-plus")
            or card.find("span", class_="a-size-medium")
            or card.find("h2")
        )

        # --- Fiyat (tam sayi + kesir) ---
        price_whole = card.find("span", class_="a-price-whole")
        price_frac  = card.find("span", class_="a-price-fraction")

        if price_whole:
            # "7.849," -> "7.849,00 TL" formatina cevir
            raw_whole = price_whole.get_text(strip=True).rstrip(",")
            frac  = price_frac.get_text(strip=True) if price_frac else "00"
            price = f"{raw_whole},{frac} TL"
        else:
            price = None

        # --- Urun linki ---
        link_tag = card.find("a", href=True)
        product_url = search_url
        if link_tag:
            href = link_tag["href"]
            product_url = (BASE_URL + href) if href.startswith("/") else href

        if name_tag and price:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=True,
                product_name=name_tag.get_text(strip=True)[:120],
                price=price,
                url=product_url,
            )

        logger.warning("[Amazon] Fiyat/isim ayristirilamadi — sorgu: %s", query_raw)
        return ScraperResult(
            platform=self.PLATFORM_NAME,
            success=False,
            url=search_url,
            error="Fiyat veya urun adi alinamadi.",
        )
