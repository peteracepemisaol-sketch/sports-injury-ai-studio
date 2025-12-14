"""Rate Limiter para Sports Injury AI Studio
Criado: 13 Dezembro 2025
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
import streamlit as st

class RateLimiter:
    def __init__(self):
        # Inicializar no session state para persistir entre reruns
        if 'rate_limiter_calls' not in st.session_state:
            st.session_state.rate_limiter_calls = defaultdict(list)
        
        self.limits = {
            'pubmed': {'calls': 3, 'period': 1},  # 3 calls/segundo
            'newsapi': {'calls': 100, 'period': 86400},  # 100 calls/dia  
            'perplexity': {'calls': 50, 'period': 3600}  # 50 calls/hora
        }
    
    def check_limit(self, api_name: str) -> tuple[bool, str]:
        """Verifica se pode fazer chamada à API
        Retorna: (pode_chamar, mensagem)
        """
        now = datetime.now()
        limit_config = self.limits.get(api_name)
        
        if not limit_config:
            return True, "OK"
        
        # Limpar chamadas antigas
        cutoff = now - timedelta(seconds=limit_config['period'])
        st.session_state.rate_limiter_calls[api_name] = [
            call_time for call_time in st.session_state.rate_limiter_calls[api_name] 
            if call_time > cutoff
        ]
        
        # Verificar limite
        current_calls = len(st.session_state.rate_limiter_calls[api_name])
        if current_calls >= limit_config['calls']:
            wait_time = (st.session_state.rate_limiter_calls[api_name][0] + 
                        timedelta(seconds=limit_config['period']) - now).total_seconds()
            return False, f"Limite atingido. Aguarde {int(wait_time)}s"
        
        # Registrar chamada
        st.session_state.rate_limiter_calls[api_name].append(now)
        return True, "OK"
    
    def get_usage_stats(self, api_name: str) -> dict:
        """Retorna estatísticas de uso da API"""
        limit_config = self.limits.get(api_name, {})
        current_calls = len(st.session_state.rate_limiter_calls.get(api_name, []))
        max_calls = limit_config.get('calls', 0)
        
        return {
            'current': current_calls,
            'max': max_calls,
            'percentage': (current_calls / max_calls * 100) if max_calls > 0 else 0
        }

# Instância global
rate_limiter = RateLimiter()
