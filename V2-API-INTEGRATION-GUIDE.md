# 🚀 Sports Injury AI Studio v2.0 - Guia de Integração com APIs

## 📋 Resumo Executivo

Esta versão transforma a aplicação de protótipo com placeholders em ferramenta profissional com **dados reais** de APIs externas.

### ✅ APIs Integradas:
1. **PubMed** - Artigos científicos (GRATUITO)
2. **NewsAPI** - Notícias de desporto (100 pedidos/dia grátis)
3. **Perplexity/OpenAI** - Geração de conteúdo IA  
4. **Base de dados** - Timelines de recuperação

---

## 🔧 PASSO 1: Configurar API Keys

### 1.1 Registar nas APIs (5 minutos)

**NewsAPI** (opcional mas recomendado):
- Registo: https://newsapi.org/register
- Copia a tua API key

**Perplexity** (opcional):
- Registo: https://www.perplexity.ai/settings/api  
- Ou usa OpenAI: https://platform.openai.com/api-keys

**PubMed**: Não requer registo (API pública)

### 1.2 Adicionar Keys ao Streamlit

**No Streamlit Cloud:**
1. Vai a https://share.streamlit.io/
2. Abre a tua app > ⚙️ Settings > Secrets
3. Adiciona:

```toml
# Streamlit Secrets
NEWSAPI_KEY = "a_tua_newsapi_key_aqui"
PERPLEXITY_API_KEY = "pplx-a_tua_key_aqui"
# ou
OPENAI_API_KEY = "sk-proj-a_tua_key_aqui"
```

**Em desenvolvimento local:**
```bash
mkdir -p .streamlit
echo 'NEWSAPI_KEY = "tua_key"' > .streamlit/secrets.toml
```

---

## 💻 PASSO 2: Código das Funções de API

Adiciona estas funções ao teu `app.py` (antes das funções de geração):

### 2.1 Função PubMed

```python
import requests
from typing import List, Dict

def buscar_pubmed(query: str, max_results: int = 5) -> List[Dict]:
    """
    Busca artigos no PubMed via API pública
    GRATUITO - não requer API key
    """
    try:
        # Passo 1: Buscar IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_data = search_response.json()
        
        ids = search_data.get('esearchresult', {}).get('idlist', [])
        if not ids:
            return []
        
        # Passo 2: Obter detalhes
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'json'
        }
        
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
        
        return artigos
    
    except Exception as e:
        st.error(f"⚠️ Erro ao buscar no PubMed: {str(e)}")
        return []
```

### 2.2 Função NewsAPI

```python
def buscar_noticias(query: str, api_key: str, max_results: int = 5) -> List[Dict]:
    """
    Busca notícias via NewsAPI
    Requer API key (100 pedidos/dia grátis)
    """
    if not api_key:
        return []
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'language': 'pt',
            'sortBy': 'publishedAt',
            'pageSize': max_results,
            'apiKey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') != 'ok':
            return []
        
        return [
            {
                'title': article.get('title', 'N/A'),
                'source': article.get('source', {}).get('name', 'N/A'),
                'description': article.get('description', 'N/A'),
                'url': article.get('url', '#'),
                'publishedAt': article.get('publishedAt', 'N/A')
            }
            for article in data.get('articles', [])
        ]
    
    except Exception as e:
        st.error(f"⚠️ Erro ao buscar notícias: {str(e)}")
        return []
```

### 2.3 Função de Geração com IA

```python
def gerar_conteudo_ia(prompt: str, api_key: str, modelo: str = 'perplexity') -> str:
    """
    Gera conteúdo usando Perplexity ou OpenAI
    """
    if not api_key:
        return "[Configura API key para gerar conteúdo com IA]"
    
    try:
        if modelo == 'perplexity':
            url = "https://api.perplexity.ai/chat/completions"
            model_name = 'llama-3.1-sonar-small-128k-online'
        else:  # OpenAI
            url = "https://api.openai.com/v1/chat/completions"
            model_name = 'gpt-4o-mini'
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model_name,
            'messages': [
                {'role': 'system', 'content': 'És um especialista em fisioterapia desportiva.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 500,
            'temperature': 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return f"[Erro: {result.get('error', {}).get('message', 'Desconhecido')}]"
    
    except Exception as e:
        return f"[Erro: {str(e)}]"
```

### 2.4 Obter API Keys

```python
def get_api_keys():
    """Obtém as API keys do Streamlit secrets"""
    try:
        return {
            'newsapi': st.secrets.get('NEWSAPI_KEY', ''),
            'perplexity': st.secrets.get('PERPLEXITY_API_KEY', ''),
            'openai': st.secrets.get('OPENAI_API_KEY', '')
        }
    except:
        return {'newsapi': '', 'perplexity': '', 'openai': ''}
```

---

## 📦 PASSO 3: Base de Dados de Lesões

Adiciona esta base de dados ao início do ficheiro:

```python
LESIONS_DATABASE = {
    "Rutura do LCA": {
        "categoria": "Ligamentar",
        "tempo_recuperacao": "6-9 meses",
        "timeline": {
            "fase_aguda": "0-2 semanas: controlo dor/edema, mobilização passiva",
            "fase_subaguda": "2-16 semanas: ADM completo, força, propriocepção",
            "fase_retorno": "4-9 meses: treino específico, testes funcionais"
        },
        "criterios_retorno": [
            "Força >90% do lado contralateral",
            "Hop tests >90%",
            "Sem dor ou edema"
        ]
    },
    "Entorse do Tornozelo": {
        "categoria": "Ligamentar",
        "tempo_recuperacao": "2-6 semanas",
        "timeline": {
            "fase_aguda": "0-72h: RICE, mobilização precoce",
            "fase_subaguda": "3-14 dias: fortalecimento, propriocepção",
            "fase_retorno": "2-6 semanas: exercícios específicos"
        }
    },
    "Lesão Muscular Isquiotibiais": {
        "categoria": "Muscular",
        "tempo_recuperacao": "3-12 semanas",
        "timeline": {
            "fase_aguda": "0-5 dias: repouso relativo, crioterapia",
            "fase_subaguda": "5-21 dias: exercícios excêntricos progressivos",
            "fase_retorno": "3-12 semanas: sprint progressivo, gestão carga"
        }
    }
}
```

---

## 🔄 PASSO 4: Modificar Funções de Geração

Modifica `gerar_estrutura_infografico()` para incluir dados reais:

```python
def gerar_estrutura_infografico(fonte, tema, publico, idioma, nivel_detalhe):
    # Obtém API keys
    keys = get_api_keys()
    
    # Busca dados reais
    artigos_pubmed = buscar_pubmed(f"{tema} sports injury", max_results=3)
    noticias = buscar_noticias(tema, keys['newsapi'], max_results=3)
    
    # Obtém timeline da base de dados
    timeline_lesao = LESIONS_DATABASE.get(tema, {}).get('timeline', {})
    
    # Gera resumo com IA (se disponível)
    prompt = f"Cria um resumo de 2 parágrafos sobre {tema} para {publico}."
    api_key = keys.get('perplexity') or keys.get('openai')
    resumo_ia = gerar_conteudo_ia(prompt, api_key) if api_key else ""
    
    estrutura = {
        "metadata": {
            "titulo": f"Infográfico: {tema}",
            "data_criacao": datetime.now().isoformat(),
            "publico_alvo": publico,
            "idioma": idioma
        },
        "conteudo": {
            "titulo_principal": tema,
            "resumo_ia": resumo_ia,
            "timeline_recuperacao": timeline_lesao,
            "fontes_cientificas": artigos_pubmed,
            "noticias_recentes": noticias,
            "secoes": [
                {
                    "id": 1,
                    "tipo": "introducao",
                    "titulo": "O que é?",
                    "conteudo": resumo_ia[:200] if resumo_ia else f"Informação sobre {tema}"
                },
                {
                    "id": 2,
                    "tipo": "timeline",
                    "titulo": "Recuperação",
                    "conteudo": timeline_lesao
                },
                {
                    "id": 3,
                    "tipo": "fontes",
                    "titulo": "Evidência Científica",
                    "conteudo": f"{len(artigos_pubmed)} artigos do PubMed"
                }
            ]
        },
        "integracao": {
            "plataforma_destino": "Canva",
            "fonte_dados": fonte
        }
    }
    
    return estrutura
```

---

## 📝 PASSO 5: Atualizar requirements.txt

Adiciona a dependência:

```
streamlit>=1.28.0
requests>=2.31.0
```

---

## ✅ PASSO 6: Testar

### Teste Local:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Teste no Streamlit Cloud:
1. Faz push das alterações
2. Adiciona API keys em Settings > Secrets
3. App reinicia automaticamente

---

## 🎯 Resultado Esperado

**ANTES:**
```json
{
  "conteudo": "Introdução sobre [tema]"
}
```

**DEPOIS:**
```json
{
  "resumo_ia": "Segundo estudo de 2024...",
  "fontes_cientificas": [
    {
      "pmid": "38234567",
      "title": "ACL reconstruction outcomes...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/38234567/"
    }
  ],
  "timeline_recuperacao": {
    "fase_aguda": "0-2 semanas: controlo dor/edema",
    "fase_subaguda": "2-16 semanas: força",
    "fase_retorno": "4-9 meses: testes funcionais"
  },
  "noticias_recentes": [...]  
}
```

---

## 🔗 Links Úteis

- PubMed API Docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- NewsAPI Docs: https://newsapi.org/docs
- Perplexity API: https://docs.perplexity.ai/
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

---

**Criado por**: Comet (Perplexity AI)  
**Data**: 12 dezembro 2025  
**Versão**: 2.0  

Para dúvidas, consulta o Google Docs: https://docs.google.com/document/d/1ZF80QKkYqWA8f3n9ERxH1EFxpr2fNE4_YEpzvnnt0D0/
