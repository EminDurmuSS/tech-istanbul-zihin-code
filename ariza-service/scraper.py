#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metro İstanbul Arıza Scraper
HTML'den arıza verilerini çeker ve parse eder.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetroArizaScraper:
    """Metro İstanbul arıza sayfasından veri çeken sınıf."""
    
    BASE_URL = "https://www.metro.istanbul"
    ARIZA_ENDPOINT = "/SeferDurumlari/Ariza/2"
    
    # Ekipman türü mapping
    EKIPMAN_MAP = {
        'ASANSOR': 'Asansör',
        'YURYNBANT': 'Yürüyen Bant',
        'YURMERDVEN': 'Yürüyen Merdiven',
        'ISTGIRIS': 'Giriş-Çıkış',
        'WC': 'Tuvalet',
        'MESCID': 'Mescid',
        'BEBEKODASI': 'Bebek Bakım Odası',
        'PLATFORM': 'Dikey Engelli Platformu'
    }
    
    def __init__(self, cache_duration: int = 300):
        """
        Scraper'ı başlatır.
        
        Args:
            cache_duration: Verinin saniye cinsinden bellekte tutulma süresi (default: 300sn / 5dk)
        """
        self.session = requests.Session()
        self._setup_headers()
        
        # Cache ayarları
        self.cache_duration = cache_duration
        self._cached_data = None
        self._last_fetch_time = None
    
    def _setup_headers(self):
        """HTTP request headers'ını ayarlar."""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
    
    def fetch_ariza_page(self) -> Optional[str]:
        """
        Arıza sayfasını çeker.
        """
        url = f"{self.BASE_URL}{self.ARIZA_ENDPOINT}"
        
        try:
            logger.info(f"📡 Canlı siteye istek gönderiliyor: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ İstek hatası: {e}")
            return None
    
    def parse_ariza_html(self, html_content: str) -> List[Dict[str, Any]]:
        """HTML içeriğinden arıza verilerini parse eder."""
        soup = BeautifulSoup(html_content, 'html.parser')
        ariza_rows = soup.find_all('tr', id=lambda x: x and x.startswith('arizaList_'))
        
        arizalar = []
        for row in ariza_rows:
            try:
                ariza = self._parse_ariza_row(row)
                if ariza:
                    arizalar.append(ariza)
            except Exception as e:
                continue
        
        return arizalar

    def _parse_ariza_row(self, row) -> Optional[Dict[str, Any]]:
        """Tek bir arıza satırını parse eder."""
        ariza_id = row.get('id', '').replace('arizaList_', '')
        hat_id = row.get('data-hatid', '')
        istasyon_id = row.get('data-istasyonid', '')
        ariza_neden = row.get('data-arizaneden', '')
        ref_char = row.get('data-refchar', '')
        ref_ekipman = row.get('data-refekipman', '')
        ariza_takip_no = row.get('data-arizaid', '')
        
        cells = row.find_all('td')
        if len(cells) < 4:
            return None
        
        istasyon_adi = cells[0].get_text(strip=True)
        ekipman_aciklama = cells[1].get_text(strip=True)
        durum_span = cells[2].find('span')
        durum = durum_span.get_text(strip=True) if durum_span else cells[2].get_text(strip=True)
        tarih = cells[3].get_text(strip=True)
        
        return {
            'ariza_id': ariza_id,
            'ariza_takip_no': ariza_takip_no,
            'hat_kodu': hat_id,
            'istasyon_id': istasyon_id,
            'istasyon_adi': istasyon_adi,
            'ekipman_turu': ref_ekipman,
            'ekipman_turu_aciklama': self.EKIPMAN_MAP.get(ref_ekipman, ref_ekipman),
            'ekipman_aciklama': ekipman_aciklama,
            'durum': durum,
            'ariza_nedeni': ariza_neden,
            'tarih': tarih,
            'ref_char': ref_char
        }
    
    def get_arizalar(self) -> Dict[str, Any]:
        """
        Arıza verilerini getirir (Cache destekli).
        """
        current_time = datetime.now()
        
        # Cache kontrolü
        if (self._cached_data and self._last_fetch_time and 
            (current_time - self._last_fetch_time).total_seconds() < self.cache_duration):
            logger.info("♻️ Veriler önbellekten (cache) getirildi.")
            return {
                'success': True,
                'error': None,
                'from_cache': True,
                'data': self._cached_data
            }

        # Veriyi çek ve parse et
        html_content = self.fetch_ariza_page()
        if not html_content:
            return {'success': False, 'error': 'Siteye erişilemedi', 'data': None}
        
        arizalar = self.parse_ariza_html(html_content)
        ozet = self._create_summary(arizalar)
        
        # Cache'i güncelle
        self._cached_data = {'ozet': ozet, 'arizalar': arizalar}
        self._last_fetch_time = current_time
        
        logger.info("🆕 Veriler canlı siteden çekildi ve cache güncellendi.")
        
        return {
            'success': True,
            'error': None,
            'from_cache': False,
            'data': self._cached_data
        }
    
    def _create_summary(self, arizalar: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Arıza verilerinin özetini oluşturur."""
        
        # Hat bazında istatistikler
        hat_stats = {}
        for ariza in arizalar:
            hat = ariza['hat_kodu']
            if hat:
                hat_stats[hat] = hat_stats.get(hat, 0) + 1
        
        # Ekipman türü bazında istatistikler
        ekipman_stats = {}
        for ariza in arizalar:
            ekipman = ariza['ekipman_turu_aciklama']
            if ekipman:
                ekipman_stats[ekipman] = ekipman_stats.get(ekipman, 0) + 1
        
        # Durum bazında istatistikler
        durum_stats = {}
        for ariza in arizalar:
            durum = ariza['durum']
            if durum:
                durum_stats[durum] = durum_stats.get(durum, 0) + 1
        
        return {
            'toplam_ariza_sayisi': len(arizalar),
            'cekme_tarihi': datetime.now().isoformat(),
            'hat_bazinda_dagilim': hat_stats,
            'ekipman_bazinda_dagilim': ekipman_stats,
            'durum_bazinda_dagilim': durum_stats
        }


# Test için
if __name__ == '__main__':
    scraper = MetroArizaScraper()
    result = scraper.get_arizalar()
    
    if result['success']:
        data = result['data']
        print(f"\n✅ Başarılı!")
        print(f"📊 Toplam Arıza: {data['ozet']['toplam_ariza_sayisi']}")
        print(f"\n🚇 Hat Bazında Dağılım:")
        for hat, sayi in sorted(data['ozet']['hat_bazinda_dagilim'].items()):
            print(f"   {hat}: {sayi} arıza")
    else:
        print(f"\n❌ Hata: {result['error']}")
