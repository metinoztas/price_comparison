# -*- coding: utf-8 -*-
"""
database/db_manager.py — SQLite veritabanı yönetimi

Özellikler:
  - Parameterized queries (SQL injection önlemi)
  - Fiyat geçmişi takibi
  - Geçmiş aramaların kaydı
  - Context manager desteği
"""

import logging
import sqlite3
from datetime import datetime
from typing import Optional

from config import DB_PATH

logger = logging.getLogger(__name__)


class DatabaseManager:
    """SQLite veritabanı CRUD işlemlerini yöneten sınıf."""

    CREATE_PRICE_HISTORY = """
        CREATE TABLE IF NOT EXISTS price_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            brand       TEXT    NOT NULL,
            model       TEXT    NOT NULL,
            storage     TEXT    NOT NULL,
            platform    TEXT    NOT NULL,
            product_name TEXT,
            price       TEXT    NOT NULL,
            url         TEXT,
            searched_at TEXT    NOT NULL
        )
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        logger.debug("Veritabanı bağlantısı açıldı: %s", self.db_path)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug("Veritabanı bağlantısı kapatıldı.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.executescript(self.CREATE_PRICE_HISTORY)
        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Kayıt & Sorgulama
    # ------------------------------------------------------------------ #

    def save_result(self, brand: str, model: str, storage: str,
                    platform: str, product_name: str, price: str,
                    url: str = "") -> int:
        """Arama sonucunu fiyat geçmişine ekle. Kayıt ID'sini döndürür."""
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO price_history
                (brand, model, storage, platform, product_name, price, url, searched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (brand, model, storage, platform, product_name,
             price, url, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_last_price(self, brand: str, model: str,
                       storage: str, platform: str) -> Optional[dict]:
        """Belirtilen ürün + platform için son kaydı döndürür."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM price_history
            WHERE brand=? AND model=? AND storage=? AND platform=?
            ORDER BY searched_at DESC
            LIMIT 1
            """,
            (brand, model, storage, platform),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_price_history(self, brand: str, model: str,
                          storage: str, platform: str,
                          limit: int = 10) -> list[dict]:
        """Son N kaydı kronolojik sırada döndürür."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM price_history
            WHERE brand=? AND model=? AND storage=? AND platform=?
            ORDER BY searched_at DESC
            LIMIT ?
            """,
            (brand, model, storage, platform, limit),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_recent_searches(self, limit: int = 20) -> list[dict]:
        """En son yapılan aramaları döndürür (tekrarsız)."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT brand, model, storage,
                   MAX(searched_at) as last_searched
            FROM price_history
            GROUP BY brand, model, storage
            ORDER BY last_searched DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def price_changed(self, brand: str, model: str,
                      storage: str, platform: str,
                      new_price: str) -> Optional[str]:
        """
        Fiyat değiştiyse önceki fiyatı döndürür, değişmediyse None.
        """
        last = self.get_last_price(brand, model, storage, platform)
        if last and last["price"] != new_price:
            return last["price"]
        return None
