"""Sistema de Logging para Sports Injury AI Studio
Criado: 13 Dezembro 2025
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Criar diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configurar logging
log_filename = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SportsInjuryAI')

def log_api_call(api_name: str, query: str, status: str, duration_ms: float, result_count: int = 0):
    """Log chamada a API externa"""
    logger.info(
        f"API Call | {api_name} | Query: '{query}' | Status: {status} | "
        f"Duration: {duration_ms:.2f}ms | Results: {result_count}"
    )

def log_error(function_name: str, error_message: str, error_type: str = "Exception"):
    """Log erro estruturado"""
    logger.error(f"{error_type} in {function_name}: {error_message}")

def log_user_action(action: str, details: dict = None):
    """Log ação do utilizador"""
    details_str = f" | Details: {details}" if details else ""
    logger.info(f"User Action | {action}{details_str}")

def log_generation(content_type: str, tema: str, success: bool, duration_ms: float = 0):
    """Log geração de conteúdo"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(
        f"Content Generation | Type: {content_type} | Tema: '{tema}' | "
        f"Status: {status} | Duration: {duration_ms:.2f}ms"
    )

# Exportar logger e funções
__all__ = ['logger', 'log_api_call', 'log_error', 'log_user_action', 'log_generation']
