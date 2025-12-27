
"""
İBB Metro Agent - Ana Giriş Noktası
"""

import sys
import uvicorn
from src.config import config
from src.utils.logger import setup_logging, get_logger
from src.utils.data_loader import validate_data_files, preload_data

# Logging'i başlat
setup_logging()
logger = get_logger(__name__)


def startup():
    """Uygulama başlangıç kontrolleri"""
    logger.info("Starting Metro Agent application", version=config.APP_VERSION)

    # Data dosyalarını doğrula ve yükle
    logger.info("Validating data files...")
    if not validate_data_files():
        logger.error("Data validation failed! Check data files.")
        sys.exit(1)

    logger.info("Preloading data files...")
    preload_data()

    logger.info("Startup complete, starting server...")


if __name__ == "__main__":
    startup()

    uvicorn.run(
        "src.api.endpoints:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )

