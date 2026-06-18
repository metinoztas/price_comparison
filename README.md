# Fiyat Karşılaştırma Aracı / Price Comparison Tool

[🇹🇷 Türkçe (Turkish)](#türkçe) | [🇬🇧 English](#english)

<h2 id="english">🇬🇧 English</h2>

This project is a desktop application that concurrently queries and compares the prices of selected technological products (such as smartphones) on **Amazon.com.tr**, **N11**, and **Hepsiburada**.

### Features
- **Concurrent Querying:** Thanks to the threading infrastructure, it performs price searches across three different platforms simultaneously without freezing the UI.
- **Bypassing Bot Protections:** It heavily mitigates platform bot-blocking mechanisms by utilizing advanced browser headers (User-Agent, Accept, Referer, etc.) and cookie warm-up techniques.
- **Price History:** Uses an SQLite database to save the lowest prices of queried products and visually notifies the user of price changes (drop, increase).
- **Modern UI:** Offers a sleek and user-friendly interface built with PyQt5, featuring a custom dark theme.
- **Secure Database Operations:** Protected against SQL Injection attacks through parameterized queries.

### Installation and Usage

1. Make sure you have Python 3.10 or higher installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### Disclaimer
This project is developed for educational and personal use. Web scraping policies of the targeted platforms (Amazon, N11, Hepsiburada) may vary and are subject to change. It should not be used for official commercial purposes. Avoid violating the terms of service of the e-commerce platforms.


---

<h2 id="türkçe">🇹🇷 Türkçe</h2>

Bu proje, seçilen teknolojik ürünlerin (telefon vb.) fiyatlarını **Amazon.com.tr**, **N11** ve **Hepsiburada** üzerinde eşzamanlı olarak sorgulayan ve karşılaştıran bir masaüstü uygulamasıdır.

### Özellikler
- **Eşzamanlı Sorgulama:** Threading altyapısı sayesinde üç farklı platformda aynı anda fiyat araması yapar ve UI'ın donmasını engeller.
- **Bot Korumasını Aşma:** Gelişmiş tarayıcı başlıkları (User-Agent, Accept, Referer vb.) ve çerez oluşturma (cookie warm-up) teknikleri ile platformların bot engelleme sistemlerini büyük ölçüde atlatır.
- **Fiyat Geçmişi:** SQLite veritabanı kullanarak sorgulanan ürünlerin en düşük fiyatlarını kaydeder ve fiyat değişimlerini (düşüş, yükseliş) kullanıcıya görsel olarak bildirir.
- **Modern Arayüz:** PyQt5 ile geliştirilmiş, karanlık tema (dark theme) tabanlı kullanıcı dostu ve şık bir arayüz sunar.
- **Güvenli Veritabanı İşlemleri:** Parameterized sorgular ile SQL Injection ataklarına karşı korumalıdır.

### Kurulum ve Çalıştırma

1. Python 3.10 veya üzeri bir sürümün yüklü olduğundan emin olun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı çalıştırın:
   ```bash
   python main.py
   ```

### Sorumluluk Reddi (Disclaimer)
Bu proje eğitim ve kişisel kullanım amacıyla geliştirilmiştir. Kullanılan platformların (Amazon, N11, Hepsiburada) web scraping politikaları değişiklik gösterebilir. Resmi bir ticari amaçla kullanılmamalıdır. E-ticaret platformlarının hizmet koşullarını ihlal etmekten kaçının.

---
