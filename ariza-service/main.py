#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metro İstanbul Arıza API
FastAPI ile arıza verilerini sunan REST API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from scraper import MetroArizaScraper

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="Metro İstanbul Arıza API",
    description="Metro İstanbul'un arıza verilerini sunan REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scraper instance
scraper = MetroArizaScraper()


# Pydantic modeller
class ArizaModel(BaseModel):
    """Arıza veri modeli"""
    ariza_id: str = Field(..., description="Arıza ID")
    ariza_takip_no: str = Field(..., description="Arıza takip numarası")
    hat_kodu: str = Field(..., description="Hat kodu (örn: M1A, M2)")
    istasyon_id: str = Field(..., description="İstasyon ID")
    istasyon_adi: str = Field(..., description="İstasyon adı")
    ekipman_turu: str = Field(..., description="Ekipman türü kodu")
    ekipman_turu_aciklama: str = Field(..., description="Ekipman türü açıklaması")
    ekipman_aciklama: str = Field(..., description="Ekipman detay açıklaması")
    durum: str = Field(..., description="Arıza durumu")
    ariza_nedeni: str = Field(..., description="Arıza nedeni")
    tarih: str = Field(..., description="Arıza tarihi")
    ref_char: str = Field(..., description="Referans karakter")


class OzetModel(BaseModel):
    """Özet bilgi modeli"""
    toplam_ariza_sayisi: int = Field(..., description="Toplam arıza sayısı")
    cekme_tarihi: str = Field(..., description="Veri çekme tarihi")
    hat_bazinda_dagilim: Dict[str, int] = Field(..., description="Hat bazında arıza dağılımı")
    ekipman_bazinda_dagilim: Dict[str, int] = Field(..., description="Ekipman bazında arıza dağılımı")
    durum_bazinda_dagilim: Dict[str, int] = Field(..., description="Durum bazında arıza dağılımı")


class ArizaResponseModel(BaseModel):
    """API response modeli"""
    success: bool = Field(..., description="İşlem başarılı mı?")
    error: Optional[str] = Field(None, description="Hata mesajı")
    data: Optional[Dict[str, Any]] = Field(None, description="Arıza verileri")


@app.get("/", tags=["Genel"])
async def root():
    """API ana endpoint"""
    return {
        "message": "Metro İstanbul Arıza API",
        "version": "1.0.0",
        "endpoints": {
            "arizalar": "/api/arizalar",
            "ozet": "/api/ozet",
            "hat": "/api/hat/{hat_kodu}",
            "istasyon": "/api/istasyon/{istasyon_adi}",
            "docs": "/docs"
        }
    }


@app.get("/health", tags=["Genel"])
async def health_check():
    """Sağlık kontrolü endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/arizalar", response_model=ArizaResponseModel, tags=["Arızalar"])
async def get_arizalar(
    hat: Optional[str] = Query(None, description="Hat kodu filtresi (örn: M1A, M2)"),
    istasyon: Optional[str] = Query(None, description="İstasyon adı filtresi"),
    ekipman: Optional[str] = Query(None, description="Ekipman türü filtresi"),
    durum: Optional[str] = Query(None, description="Durum filtresi")
):
    """
    Tüm arıza verilerini getirir.
    
    Filtreler:
    - hat: Hat koduna göre filtrele (örn: M1A, M2, T1)
    - istasyon: İstasyon adına göre filtrele
    - ekipman: Ekipman türüne göre filtrele
    - durum: Duruma göre filtrele (Arıza, Tasarruf-Güvenlik, vb.)
    """
    try:
        # Arıza verilerini çek
        result = scraper.get_arizalar()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        arizalar = result['data']['arizalar']
        
        # Filtreleme
        if hat:
            arizalar = [a for a in arizalar if a['hat_kodu'].upper() == hat.upper()]
        
        if istasyon:
            arizalar = [a for a in arizalar if istasyon.lower() in a['istasyon_adi'].lower()]
        
        if ekipman:
            arizalar = [a for a in arizalar if ekipman.lower() in a['ekipman_turu_aciklama'].lower()]
        
        if durum:
            arizalar = [a for a in arizalar if durum.lower() in a['durum'].lower()]
        
        # Özet güncelle
        ozet = scraper._create_summary(arizalar)
        
        return {
            "success": True,
            "error": None,
            "data": {
                "ozet": ozet,
                "arizalar": arizalar
            }
        }
        
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ozet", tags=["Arızalar"])
async def get_ozet():
    """Sadece özet bilgileri getirir."""
    try:
        result = scraper.get_arizalar()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "success": True,
            "error": None,
            "data": result['data']['ozet']
        }
        
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hat/{hat_kodu}", tags=["Arızalar"])
async def get_hat_arizalari(hat_kodu: str):
    """Belirli bir hattın arızalarını getirir."""
    try:
        result = scraper.get_arizalar()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        arizalar = result['data']['arizalar']
        hat_arizalari = [a for a in arizalar if a['hat_kodu'].upper() == hat_kodu.upper()]
        
        if not hat_arizalari:
            return {
                "success": True,
                "error": None,
                "data": {
                    "hat_kodu": hat_kodu.upper(),
                    "mesaj": "Bu hatta arıza bulunmamaktadır.",
                    "ariza_sayisi": 0,
                    "arizalar": []
                }
            }
        
        return {
            "success": True,
            "error": None,
            "data": {
                "hat_kodu": hat_kodu.upper(),
                "ariza_sayisi": len(hat_arizalari),
                "arizalar": hat_arizalari
            }
        }
        
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/istasyon/{istasyon_adi}", tags=["Arızalar"])
async def get_istasyon_arizalari(istasyon_adi: str):
    """Belirli bir istasyonun arızalarını getirir."""
    try:
        result = scraper.get_arizalar()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        arizalar = result['data']['arizalar']
        istasyon_arizalari = [
            a for a in arizalar 
            if istasyon_adi.lower() in a['istasyon_adi'].lower()
        ]
        
        if not istasyon_arizalari:
            return {
                "success": True,
                "error": None,
                "data": {
                    "istasyon_adi": istasyon_adi,
                    "mesaj": "Bu istasyonda arıza bulunmamaktadır.",
                    "ariza_sayisi": 0,
                    "arizalar": []
                }
            }
        
        return {
            "success": True,
            "error": None,
            "data": {
                "istasyon_adi": istasyon_adi,
                "ariza_sayisi": len(istasyon_arizalari),
                "arizalar": istasyon_arizalari
            }
        }
        
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hatlar", tags=["Bilgi"])
async def get_hatlar():
    """Sistemdeki tüm hatları listeler."""
    try:
        result = scraper.get_arizalar()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['error'])
        
        hatlar = list(result['data']['ozet']['hat_bazinda_dagilim'].keys())
        
        return {
            "success": True,
            "error": None,
            "data": {
                "hatlar": sorted(hatlar),
                "toplam_hat_sayisi": len(hatlar)
            }
        }
        
    except Exception as e:
        logger.error(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
