# -*- coding: utf-8 -*-
"""
scrapers/n11.py — N11 fiyat scraper'i
Strateji: Once ana sayfayi ziyaret ederek cookie olustur, sonra arama yap.
CSS class'lari: div.product-text-area (isim), h3.price-currency (fiyat)
"""

import logging
import time
import urllib.parse

from .base_scraper import BaseScraper, ScraperResult

logger = logging.getLogger(__name__)


class N11Scraper(BaseScraper):
    PLATFORM_NAME = "N11"

    def search(self, brand: str, model: str, storage: str) -> ScraperResult:
        if brand.lower() in model.lower():
            query_raw = f"{model} {storage}"
        else:
            query_raw = f"{brand} {model} {storage}"

        query_enc  = urllib.parse.quote(query_raw)
        search_url = f"https://www.n11.com/arama?q={query_enc}"

        # Cookie warm-up: ana sayfayi ziyaret et
        self.session.headers.update({
            "Referer": "https://www.n11.com/",
            "Origin":  "https://www.n11.com",
        })
        self._get_silent("https://www.n11.com/")
        time.sleep(0.4)

        logger.info("[N11] Arama sorgusu: %s", query_raw)
        response = self._get(search_url)

        if response is None:
            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=False,
                url=search_url,
                error="Sunucuya ulasilamadi.",
            )

        soup = self._parse(response.text)

        # Urun adi: div.product-text-area icindeki ilk anlamli metin
        name_tag = soup.find("div", class_="product-text-area")

        # Fiyat: h3.price-currency (sepette fiyati - en dusuk)
        # yoksa div.price (liste fiyati)
        price_tag = (
            soup.find("h3", class_="price-currency")
            or soup.find("div", class_="price")
        )

        # Link: ilk urun karti icindeki <a>
        card = soup.find("div", class_="product-item-image-area")
        link_tag = card.find("a", href=True) if card else None
        product_url = link_tag["href"] if link_tag else search_url
        if product_url.startswith("/"):
            product_url = "https://www.n11.com" + product_url

        if name_tag and price_tag:
            # Isim: ilk satir yeterli (rating/badge karismasi olmadan)
            raw_name = name_tag.get_text(separator=" ", strip=True)
            # Rating/fiyat metni isimden temizle
            for unwanted in ["SÜPER", "TL", "₺"]:
                raw_name = raw_name.split(unwanted)[0].strip()
            clean_name = raw_name[:100]
            clean_price = price_tag.get_text(strip=True)

            return ScraperResult(
                platform=self.PLATFORM_NAME,
                success=True,
                product_name=clean_name,
                price=clean_price,
                url=product_url,
            )

        logger.warning("[N11] Fiyat/isim bulunamadi — sorgu: %s", query_raw)
        return ScraperResult(
            platform=self.PLATFORM_NAME,
            success=False,
            url=search_url,
            error="Urun bulunamadi veya sayfa yapisi degisti.",
        )
