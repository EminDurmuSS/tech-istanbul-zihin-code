
# ============================================================================
# DOSYA: src/api/endpoints.py (FastAPI Application)
# ============================================================================

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from src.config import config
from src.agent.metro_agent import MetroAgent
from src.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

# Global agent instance
_agent: Optional[MetroAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    setup_logging()
    logger.info("Starting IBB Metro Agent", version=config.APP_VERSION)
    
    global _agent
    _agent = MetroAgent()

    yield
    
    # Shutdown
    logger.info("Shutting down IBB Metro Agent")


app = FastAPI(
    title="İBB Metro Agent API",
    description="Metro İstanbul Çağrı Merkezi AI Agent",
    version=config.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class MessageRequest(BaseModel):
    message: str
    channel: str = "api"
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool
    response: str
    intent: str
    confidence: float
    entities: Dict[str, Any]
    report_id: Optional[str] = None
    quick_replies: List[str] = []
    actions: List[str] = []
    processing_time_ms: Optional[int] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


class ServiceStatusResponse(BaseModel):
    success: bool
    statuses: List[Dict[str, Any]]
    timestamp: str


class FaultListResponse(BaseModel):
    success: bool
    faults: List[Dict[str, Any]]
    count: int
    timestamp: str


# ============================================================================
# DEPENDENCY
# ============================================================================

def get_agent() -> MetroAgent:
    """Agent dependency"""
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    return _agent


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """API root / health check"""
    return HealthResponse(
        status="healthy",
        version=config.APP_VERSION,
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        version=config.APP_VERSION,
        timestamp=datetime.now().isoformat()
    )


@app.post("/message", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    agent: MetroAgent = Depends(get_agent)
):
    """
    Ana mesaj işleme endpoint'i
    
    Kullanıcı mesajını alır, işler ve yanıt döner.
    """
    try:
        result = await agent.process_message(
            message=request.message,
            user_id=request.user_id,
            channel=request.channel
        )
        
        report_id = None
        if result.internal_report and result.internal_report.report_id:
            report_id = result.internal_report.report_id
        
        return MessageResponse(
            success=True,
            response=result.response.text,
            intent=result.intent.type.value,
            confidence=result.intent.confidence,
            entities=result.intent.entities,
            report_id=report_id,
            quick_replies=result.response.quick_replies,
            actions=result.actions,
            processing_time_ms=result.processing_time_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error("Message processing error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/service-status", response_model=ServiceStatusResponse)
async def get_service_status(agent: MetroAgent = Depends(get_agent)):
    """Tüm hatların hizmet durumu"""
    try:
        statuses = await agent.metro.get_service_statuses()
        return ServiceStatusResponse(
            success=True,
            statuses=statuses,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/faults", response_model=FaultListResponse)
async def get_active_faults(agent: MetroAgent = Depends(get_agent)):
    """Aktif arızalar"""
    try:
        faults = await agent.metro.get_faulty_equipments()
        return FaultListResponse(
            success=True,
            faults=faults,
            count=len(faults),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lines")
async def get_lines(agent: MetroAgent = Depends(get_agent)):
    """Metro hatları"""
    try:
        lines = await agent.metro.get_lines()
        return {"success": True, "lines": lines, "count": len(lines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stations")
async def get_stations(agent: MetroAgent = Depends(get_agent)):
    """Tüm istasyonlar"""
    try:
        stations = await agent.metro.get_stations()
        return {"success": True, "stations": stations, "count": len(stations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/announcements")
async def get_announcements(
    language: str = "tr",
    agent: MetroAgent = Depends(get_agent)
):
    """Duyurular"""
    try:
        announcements = await agent.metro.get_announcements(language)
        return {"success": True, "announcements": announcements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/faq")
async def get_faq(agent: MetroAgent = Depends(get_agent)):
    """Sıkça sorulan sorular"""
    try:
        faq = await agent.metro.get_faq()
        return {"success": True, "faq": faq}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ticket-prices")
async def get_ticket_prices(
    language: str = "tr",
    agent: MetroAgent = Depends(get_agent)
):
    """Bilet fiyatları"""
    try:
        prices = await agent.metro.get_ticket_prices(language)
        return {"success": True, "prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBHOOK ENDPOINTS
# ============================================================================

class WebhookPayload(BaseModel):
    event_type: str
    report_id: str
    status: str
    details: Optional[Dict] = None


@app.post("/webhook/fault-update")
async def fault_update_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks
):
    """Arıza durumu güncellemesi webhook"""
    logger.info("Webhook received", event=payload.event_type, report_id=payload.report_id)
    
    # TODO: Kullanıcıya bildirim gönder
    # TODO: CRM güncelle
    
    return {"success": True, "message": "Webhook received"}

