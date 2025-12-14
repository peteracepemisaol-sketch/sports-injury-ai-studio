import streamlit as st
import json
from datetime import datetime
import re
import requests
from typing import List, Dict, Optional
import time
from utils.logger import logger, log_api_call, log_error, log_user_action, log_generation
from utils.rate_limiter import rate_limiter

# Configuração da página
st.set_page_config(
    page_title="Sports Injury AI Studio",
    page_icon="🏥",
    layout="wide"
)


# ==== FUNÇÕES DE INTEGRAÇÃO COM APIs ====

@st.cache_data(ttl=3600)
def get_api_keys():
    """Obtém as API keys do Streamlit secrets"""
    try:
        return {
            'newsapi': st.secrets.get('NEWSAPI_KEY', ''),
            'perplexity': st.secrets.get('PERPLEXITY_API_KEY', ''),
            'openai': st.secrets.get('OPENAI_API_KEY', '')
        }
    except:
                log_error('get_api_keys', Exception('Erro ao carregar API keys'))
                return {'newsapi': '', 'perplexity': '', 'openai': ''}

@st.cache_data(ttl=1800)
def buscar_pubmed(query: str, max_results: int = 5) -> List[Dict]:
    """Busca artigos no PubMed via API pública - GRATUITO"""
    try:
                # Rate limiting check
        if not rate_limiter.check_limit('pubmed'):
            st.warning('⚠️ Muitas requisições. Aguarde um momento.')
            return []
        
        start_time = time.time()
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {'db': 'pubmed', 'term': query, 'retmax': max_results, 'retmode': 'json', 'sort': 'relevance'}
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_data = search_response.json()
        ids = search_data.get('esearchresult', {}).get('idlist', [])
        if not ids:
            return []
        
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        fetch_params = {'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'json'}
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_data = fetch_response.json()
        
        artigos = []
        for pmid in ids:
            if pmid in fetch_data.get('result', {}):
                article = fetch_data['result'][pmid]
                artigos.append({
                    'pmid': pmid,
                    'title': article.get('title', 'N/A'),
                    'authors': ', '.join([a.get('name', '') for a in article.get('authors', [])[:3]]),
                    'journal': article.get('source', 'N/A'),
                    'pubdate': article.get('pubdate', 'N/A'),
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        log_api_call('buscar_pubmed', time.time() - start_time, True, len(artigos))
                return artigos
    except Exception as e:
        st.error(f"⚠️ Erro ao buscar no PubMed: {str(e)}")
        log_error('buscar_pubmed', e)
        return []

@st.cache_data(ttl=1800)
def buscar_noticias(query: str, api_key: str, max_results: int = 5) -> List[Dict]:
    """Busca notícias via NewsAPI"""
    if not api_key:
        return []
    try:
                # Rate limiting check
        if not rate_limiter.check_limit('newsapi'):
            st.warning('⚠️ Muitas requisições. Aguarde um momento.')
            return []
        
        start_time = time.time()
        
        url = "https://newsapi.org/v2/everything"
        params = {'q': query, 'language': 'pt', 'sortBy': 'publishedAt', 'pageSize': max_results, 'apiKey': api_key}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') != 'ok':
            return []
        noticias = [{'title': article.get('title', 'N/A'), 'source': article.get('source', {}).get('name', ''), 'description': article.get('description', 'N/A'), 'url': article.get('url', ''), 'publishedAt': article.get('publishedAt', 'N/A')} for article in data.get('articles', [])]
        log_api_call('buscar_noticias', time.time() - start_time, True, len(noticias))
        return noticias
        pt Exception as e:
        st.error(f"⚠️ Erro ao buscar notícias: {str(e)}")
        log_error('buscar_noticias', e)
        return []

# Título principal

# Funções auxiliares
def validar_pubmed_id(texto):
    """Valida se o texto contém um PubMed ID válido (8 dígitos)"""
    if not texto:
        return False
    padrao = r'\b\d{8}\b'
    return re.search(padrao, texto) is not None

def extrair_tipo_fonte(texto):
    """Identifica o tipo de fonte fornecida"""
    if not texto:
        return "Texto livre", "📝"
    if validar_pubmed_id(texto):
        return "PubMed ID", "🔬"
    elif texto.startswith('http'):
        return "URL", "🌐"
    elif 'doi' in texto.lower():
        return "DOI", "📄"
    else:
        return "Texto livre", "📝"

def gerar_lesoes_comuns():
    """Retorna lista de lesões desportivas comuns para quick selection"""
    return [
        "Entorse do Tornozelo",
        "Rutura do LCA (Ligamento Cruzado Anterior)",
        "Tendinite Patelar (Joelho do Saltador)",
        "Fascite Plantar",
        "Pubalgia",
        "Lesão Muscular Isquiotibial",
        "Síndrome do Impacto no Ombro",
        "Epicondilite Lateral (Cotovelo do Tenista)",
        "Fratura de Stress",
        "Concussão Cerebral"
    ]

st.title("🏥 Sports Injury AI Studio")
st.markdown("*Gere infográficos e vídeos profissionais sobre lesões desportivas*")

# Função para gerar estrutura de infográfico
def gerar_estrutura_infografico(fonte, tema, publico, idioma, nivel_detalhe):
    """Gera estrutura JSON para infográfico"""
        
    # Detect tipo de fonte
    tipo_fonte, emoji = extrair_tipo_fonte(fonte)
    
    estrutura = {
        "metadata": {
            "titulo": f"Infográfico: {tema}",
            "data_criacao": datetime.now().isoformat(),
            "publico_alvo": publico,
            "idioma": idioma,
            "nivel_detalhe": nivel_detalhe
        },
        "conteudo": {
            "titulo_principal": tema,
            "subtitulo": f"Informação para {publico}",
            "secoes": [
                {
                    "id": 1,
                    "tipo": "introducao",
                    "titulo": "O que é?",
                    "conteudo": f"Introdução sobre {tema}",
                    "visual_hint": "ícone anatômico"
                },
                {
                    "id": 2,
                    "tipo": "sintomas",
                    "titulo": "Sintomas",
                    "conteudo": "Lista de sintomas principais",
                    "visual_hint": "ícones de sintomas"
                },
                {
                    "id": 3,
                    "tipo": "tratamento",
                    "titulo": "Tratamento",
                    "conteudo": "Opções de tratamento",
                    "visual_hint": "fluxograma"
                },
                {
                    "id": 4,
                    "tipo": "prevencao",
                    "titulo": "Prevenção",
                    "conteudo": "Dicas de prevenção",
                    "visual_hint": "checklist visual"
                }
            ],
            "layout": {
                "tipo": "vertical",
                "cores_principais": ["#2E86AB", "#A23B72", "#F18F01"],
                "fonte_titulo": "Montserrat Bold",
                "fonte_corpo": "Open Sans"
            }
        },
        "integracao": {
            "plataforma_destino": "Canva",
            "fonte_dados": fonte
        }
    }
    return estrutura

# Função para gerar roteiro de vídeo
def gerar_roteiro_video(fonte, tema, publico, idioma, duracao, tom):
    """Gera roteiro JSON para vídeo"""
    roteiro = {
        "metadata": {
            "titulo": f"Vídeo: {tema}",
            "data_criacao": datetime.now().isoformat(),
            "publico_alvo": publico,
            "idioma": idioma,
            "duracao_alvo": duracao,
            "tom": tom
        },
        "cenas": [
            {
                "id": 1,
                "duracao": int(duracao * 0.15),
                "tipo": "abertura",
                "narrador": {
                    "role": "especialista",
                    "texto": f"Bem-vindo! Hoje vamos falar sobre {tema}",
                    "tom_voz": tom
                },
                "visual": {
                    "tipo": "título animado",
                    "elementos": ["logo", "título", "subtítulo"]
                }
            },
            {
                "id": 2,
                "duracao": int(duracao * 0.25),
                "tipo": "contexto",
                "narrador": {
                    "role": "especialista",
                    "texto": "Contextualização da lesão",
                    "tom_voz": tom
                },
                "visual": {
                    "tipo": "animação anatômica",
                    "elementos": ["diagrama", "setas", "legendas"]
                }
            },
            {
                "id": 3,
                "duracao": int(duracao * 0.30),
                "tipo": "explicacao",
                "narrador": {
                    "role": "especialista",
                    "texto": "Explicação detalhada dos sintomas e diagnóstico",
                    "tom_voz": tom
                },
                "visual": {
                    "tipo": "infográfico animado",
                    "elementos": ["lista", "ícones", "transições"]
                }
            },
            {
                "id": 4,
                "duracao": int(duracao * 0.20),
                "tipo": "solucao",
                "narrador": {
                    "role": "especialista",
                    "texto": "Tratamentos e reabilitação",
                    "tom_voz": tom
                },
                "visual": {
                    "tipo": "demonstração",
                    "elementos": ["exercícios", "técnicas", "equipamento"]
                }
            },
            {
                "id": 5,
                "duracao": int(duracao * 0.10),
                "tipo": "encerramento",
                "narrador": {
                    "role": "especialista",
                    "texto": "Conclusão e call-to-action",
                    "tom_voz": tom
                },
                "visual": {
                    "tipo": "tela final",
                    "elementos": ["resumo", "contatos", "redes sociais"]
                }
            }
        ],
        "audio": {
            "narrador_voz": "Português nativo profissional" if idioma == "Português" else "Native speaker",
            "musica_fundo": "corporativa suave",
            "efeitos_sonoros": ["transições", "highlights"]
        },
        "integracao": {
            "plataforma_video": "HeyGen/Synthesia",
            "plataforma_audio": "ElevenLabs",
            "fonte_dados": fonte
        }
    }
    return roteiro

# Tabs principais
tab1, tab2 = st.tabs(["📊 Infográfico", "🎬 Vídeo"])

# TAB 1: INFOGRÁFICO
with tab1:
    st.header("📊 Gerador de Infográfico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fonte_info = st.text_area(
            "Fonte / Tema",
            placeholder="Cole texto, URL, PubMed ID ou descreva o tema da lesão...",
            height=100
        )
        
        publico_info = st.selectbox(
            "Público-alvo",
            ["Fisioterapeuta", "Atleta", "Treinador", "Paciente leigo"]
        )
    
    with col2:
        idioma_info = st.selectbox(
            "Idioma",
            ["Português", "English", "Español"]
        )
        
        nivel_detalhe = st.select_slider(
            "Nível de detalhe",
            options=["Conciso", "Standard", "Detalhado"]
        )
    
    if st.button("🎨 Gerar Estrutura de Infográfico", type="primary", use_container_width=True):
        if fonte_info:
            with st.spinner("Gerando estrutura..."):
                estrutura = gerar_estrutura_infografico(
                    fonte_info,
                    fonte_info[:50] + "..." if len(fonte_info) > 50 else fonte_info,
                    publico_info,
                    idioma_info,
                    nivel_detalhe
                )
                
                st.success("✅ Estrutura gerada com sucesso!")
                
                # Mostra preview
                st.json(estrutura)
                
                # Download JSON
                json_str = json.dumps(estrutura, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download JSON para Make.com",
                    data=json_str,
                    file_name=f"infografico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        else:
            st.warning("⚠️ Por favor, insira a fonte ou tema")

# TAB 2: VÍDEO
with tab2:
    st.header("🎬 Gerador de Roteiro de Vídeo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fonte_video = st.text_area(
            "Fonte / Tema",
            placeholder="Cole texto, URL, PubMed ID ou descreva o tema da lesão...",
            height=100,
            key="fonte_video"
        )
        
        publico_video = st.selectbox(
            "Público-alvo",
            ["Fisioterapeuta", "Atleta", "Treinador", "Paciente leigo"],
            key="publico_video"
        )
        
        idioma_video = st.selectbox(
            "Idioma",
            ["Português", "English", "Español"],
            key="idioma_video"
        )
    
    with col2:
        duracao = st.slider(
            "Duração do vídeo (segundos)",
            min_value=30,
            max_value=180,
            value=90,
            step=15
        )
        
        tom = st.select_slider(
            "Tom",
            options=["Explicativo", "Motivacional", "Técnico"]
        )
    
    if st.button("🎬 Gerar Roteiro de Vídeo", type="primary", use_container_width=True, key="btn_video"):
        if fonte_video:
            with st.spinner("Gerando roteiro..."):
                roteiro = gerar_roteiro_video(
                    fonte_video,
                    fonte_video[:50] + "..." if len(fonte_video) > 50 else fonte_video,
                    publico_video,
                    idioma_video,
                    duracao,
                    tom
                )
                
                st.success("✅ Roteiro gerado com sucesso!")
                
                # Mostra preview
                st.json(roteiro)
                
                # Download JSON
                json_str = json.dumps(roteiro, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download JSON para Make.com",
                    data=json_str,
                    file_name=f"roteiro_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_video"
                )
        else:
            st.warning("⚠️ Por favor, insira a fonte ou tema")

    
    # Seção de visualização de vídeo integrado
    st.markdown("---")
    st.subheader("🎥 Visualizar Vídeo")
    
    video_url = st.text_input(
        "URL do Vídeo",
        placeholder="Cole URL do YouTube, link direto para MP4, ou caminho de ficheiro local...",
        help="Suporta YouTube, Vimeo, e links diretos para ficheiros de vídeo",
        key="video_url_input"
    )
    
    if video_url:
        try:
            st.video(video_url)
            st.caption(f"📍 Fonte: {video_url}")
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar vídeo: {str(e)}")
            st.info("💡 Dica: Certifica-te que o URL é válido e acessível. Para YouTube, usa o formato: https://youtu.be/VIDEO_ID")

# Rodapé
st.markdown("---")
st.markdown(
    """
    **Próximos passos:**
    1. Baixe o JSON gerado
    2. Importe no Make.com ou Activepieces
    3. Conecte com Canva (infográficos) ou HeyGen/ElevenLabs (vídeos)
    4. Automatize a geração de conteúdo!
    """
)
