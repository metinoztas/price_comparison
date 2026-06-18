# -*- coding: utf-8 -*-
"""
config.py — Uygulama sabitleri ve ürün veritabanı
"""

import os

# --- Uygulama Ayarları ---
APP_NAME    = "NTH Fiyat Takip"
APP_VERSION = "2.0.0"
APP_AUTHOR  = "metinoztas"
GITHUB_URL  = "https://github.com/metinoztas"

# --- Dosya Yolları ---
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH    = os.path.join(BASE_DIR, "database.db")
LOG_PATH   = os.path.join(BASE_DIR, "app.log")

# --- HTTP Ayarları ---
REQUEST_TIMEOUT = 15          # saniye
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Cache-Control": "max-age=0",
}

# --- Platform Renk Kodlari ---
PLATFORM_COLORS = {
    "Amazon":      "#FF9900",   # Turuncu
    "N11":         "#8B32E5",   # Mor
    "Hepsiburada": "#FF6000",   # Kirmizi-turuncu
}

PLATFORM_BG_COLORS = {
    "Amazon":      "#2D1A00",
    "N11":         "#1A0A2E",
    "Hepsiburada": "#2D1000",
}

# --- Ürün Veritabanı ---
# Yapı: { "marka": { "model": [hafıza_seçenekleri] } }
PRODUCTS = {
    "iPhone": {
        "iPhone 8":   ["64 GB", "128 GB", "256 GB"],
        "iPhone X":   ["64 GB", "256 GB"],
        "iPhone 11":  ["64 GB", "128 GB", "256 GB"],
        "iPhone 12":  ["64 GB", "128 GB", "256 GB"],
        "iPhone 13":  ["128 GB", "256 GB", "512 GB"],
        "iPhone 14":  ["128 GB", "256 GB", "512 GB"],
        "iPhone 15":  ["128 GB", "256 GB", "512 GB"],
        "iPhone 16":  ["128 GB", "256 GB", "512 GB"],
    },
    "Samsung": {
        "Galaxy A04e": ["32 GB", "64 GB"],
        "Galaxy A23":  ["64 GB", "128 GB"],
        "Galaxy A54":  ["128 GB", "256 GB"],
        "Galaxy S20 FE": ["128 GB", "256 GB"],
        "Galaxy S21 FE": ["128 GB", "256 GB"],
        "Galaxy S23":    ["128 GB", "256 GB", "512 GB"],
        "Galaxy S24":    ["128 GB", "256 GB", "512 GB"],
    },
    "Xiaomi": {
        "Redmi 9C":         ["32 GB", "64 GB"],
        "Redmi 10":         ["64 GB", "128 GB"],
        "Redmi Note 11 Pro": ["128 GB", "256 GB"],
        "Redmi Note 12":     ["128 GB", "256 GB"],
        "Redmi Note 12 Pro": ["128 GB", "256 GB"],
        "Poco X5":           ["128 GB", "256 GB"],
        "Poco X6 Pro":       ["256 GB", "512 GB"],
    },
}

# Marka ikonları (assets klasöründeki dosya adları)
BRAND_ICONS = {
    "iPhone":  "apple-logo-png-dallas-shootings-don-add-are-speech-zones-used-4.png",
    "Samsung": "Samsung_Logo.svg.png",
    "Xiaomi":  "Xiaomi_logo_(2021-).svg.png",
}
