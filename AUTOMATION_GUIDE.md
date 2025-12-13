# 🤖 Guia Completo de Automação
## Sports Injury AI Studio v2.2 - Workflow Automatizado

---

## 🎯 Visão Geral

Este guia mostra como automatizar completamente o processo de geração de infográficos e vídeos sobre lesões esportivas, eliminando os passos manuais.

### ❌ **ANTES (Manual - 4 passos)**
1. Baixe o JSON gerado
2. Importe no Make.com ou Activepieces
3. Conecte com Canva (infográficos) ou HeyGen/ElevenLabs (vídeos)  
4. Automatize a geração de conteúdo!

### ✅ **AGORA (Automatizado - 1 clique)**
1. Clique em "🚀 Enviar & Gerar Automaticamente"

---

## 🔧 Setup Inicial (5 minutos)

### **Passo 1: Configurar Webhook no Make.com**

1. **Criar Novo Cenário no Make.com**
   - Acesse: https://make.com/scenarios
   - Clique em "Create a new scenario"
   - Nome: "Sports Injury - Infográfico Automático"

2. **Adicionar Webhook**
   - Módulo inicial: **Webhooks > Custom Webhook**
   - Clique em "Create a webhook"
   - Nome: `sports-injury-webhook`
   - **Copie a URL gerada** (ex: `https://hook.eu1.make.com/abc123xyz`)

3. **Adicionar Módulos**

   ```
   [Webhook] → [Parse JSON] → [Canva] → [Google Drive] → [Instagram/Email]
   ```

   **Módulo 2 - Canva:**
   - App: **Canva > Create Design from Template**
   - Template: Selecione template de infográfico
   - Mapeamento:
     - `Title` → `{{1.conteudo.titulo_principal}}`
     - `Subtitle` → `{{1.conteudo.subtitulo}}`
     - `Sections` → `{{1.conteudo.secoes}}`

   **Módulo 3 - Google Drive:**
   - App: **Google Drive > Upload a File**
   - File: `{{2.design_url}}`
   - Folder: "Infográficos Gerados"

4. **Ativar o Cenário**
   - Toggle ON no canto superior direito

---

### **Passo 2: Adicionar Webhook URL nos Secrets do Streamlit**

1. Acesse: https://share.streamlit.io/
2. Selecione **sports-injury-ai-studio**
3. Clique em ⚙️ **Settings > Secrets**
4. Adicione:

```toml
# Webhooks para Automação
MAKE_WEBHOOK_INFOGRAPHIC = "https://hook.eu1.make.com/SEU_WEBHOOK_AQUI"
MAKE_WEBHOOK_VIDEO = "https://hook.eu1.make.com/SEU_WEBHOOK_VIDEO_AQUI"
ACTIVEPIECES_WEBHOOK = "https://cloud.activepieces.com/api/v1/webhooks/SEU_ID"
```

5. Clique em **Save**

---

### **Passo 3: Configurar Canva API (Opcional - mas recomendado)**

1. Acesse: https://www.canva.com/developers/
2. Crie uma **Developer App**
3. Obtenha **API Key** e **Client Secret**
4. Adicione aos Secrets:

```toml
CANVA_API_KEY = "sua_chave_aqui"
CANVA_CLIENT_SECRET = "seu_secret_aqui"
```

---

## 🚀 Como Usar (Após Setup)

### **Cenário 1: Gerar Infográfico Automaticamente**

1. Abra a app: https://gi25qmq3ffwuvnwirqpxuz.streamlit.app/
2. Aba "Infográfico"
3. Insira o tema: `Ruptura do LCA em futebolistas`
4. Clique em **"🚀 Gerar & Enviar Automaticamente"**

**O que acontece nos bastidores:**
```
1. Busca artigos no PubMed ✓
2. Busca notícias no NewsAPI ✓
3. Gera conteúdo com Perplexity AI ✓
4. Cria JSON estruturado ✓
5. Envia para Make.com webhook ✓
6. Make.com cria design no Canva ✓
7. Salva no Google Drive ✓
8. (Opcional) Publica no Instagram ✓
```

⏱️ **Tempo total: 2-3 minutos**

---

### **Cenário 2: Gerar Vídeo Automaticamente**

1. Aba "Vídeo"
2. Insira o tema
3. Configure duração e tom
4. Clique em **"🎥 Gerar Vídeo & Enviar"**

**Workflow:**
```
Streamlit → Make.com → HeyGen (Avatar) → ElevenLabs (Voz) → Google Drive
```

---

## 📚 Templates de Cenários Make.com

### **Template 1: Infográfico Básico**
```json
{
  "name": "Sports Injury - Infographic Generator",
  "modules": [
    {"id": 1, "module": "webhook"},
    {"id": 2, "module": "canva:create_design"},
    {"id": 3, "module": "google_drive:upload"}
  ]
}
```

### **Template 2: Infográfico + Publicação Instagram**
```json
{
  "name": "Sports Injury - Auto Post Instagram",
  "modules": [
    {"id": 1, "module": "webhook"},
    {"id": 2, "module": "canva:create_design"},
    {"id": 3, "module": "image_optimizer"},
    {"id": 4, "module": "instagram:create_post"},
    {"id": 5, "module": "slack:notify"}
  ]
}
```

### **Template 3: Vídeo Completo**
```json
{
  "name": "Sports Injury - Video Generator",
  "modules": [
    {"id": 1, "module": "webhook"},
    {"id": 2, "module": "heygen:create_video"},
    {"id": 3, "module": "elevenlabs:generate_voice"},
    {"id": 4, "module": "video_composer"},
    {"id": 5, "module": "youtube:upload"}
  ]
}
```

---

## ⚙️ Configurações Avançadas

### **Activepieces (Alternativa ao Make.com)**

1. Crie workflow em: https://cloud.activepieces.com/
2. Trigger: **Webhook**
3. Actions:
   - Parse JSON
   - HTTP Request para Canva
   - Save to Cloud Storage

### **Canva API Direct Integration**

Se preferir integração direta (sem Make.com):

```python
# No Streamlit Secrets, adicione:
CANVA_DIRECT_API = "true"
CANVA_TEMPLATE_ID = "seu_template_id"
```

A app vai usar a Canva API diretamente.


---

## 📄 Exemplo de JSON Enviado

```json
{
  "type": "infographic",
  "timestamp": "2025-12-13T19:00:00Z",
  "metadata": {
    "titulo": "Ruptura do LCA em Futebolistas",
    "publico_alvo": "Fisioterapeuta",
    "idioma": "Português",
    "fontes_cientificas": [
      {"pmid": "12345678", "titulo": "ACL tears in soccer..."},
      {"pmid": "87654321", "titulo": "Prevention strategies..."}
    ],
    "noticias_recentes": [
      {"title": "Neymar sofre nova lesão no LCA", "source": "ESPN"}
    ]
  },
  "conteudo": {
    "titulo_principal": "Ruptura do LCA",
    "secoes": [
      {"tipo": "intro", "conteudo": "Texto gerado por IA..."},
      {"tipo": "sintomas", "conteudo": "Lista de sintomas..."}
    ]
  },
  "integracao": {
    "plataforma_destino": "Canva",
    "template_id": "ABC123",
    "callback_url": "https://app.streamlit.io/callback"
  }
}
```

---

## ⚙️ Código para Adicionar na App (app.py)

Adicione esta função ao `app.py`:

```python
import requests

def enviar_para_webhook(json_data, tipo="infographic"):
    """
    Envia JSON para webhook do Make.com/Activepieces
    """
    try:
        # Obter webhook URL dos secrets
        if tipo == "infographic":
            webhook_url = st.secrets.get('MAKE_WEBHOOK_INFOGRAPHIC', '')
        else:
            webhook_url = st.secrets.get('MAKE_WEBHOOK_VIDEO', '')
        
        if not webhook_url:
            st.warning("⚠️ Webhook não configurado. Configure em Settings > Secrets")
            return False
        
        # Enviar POST request
        response = requests.post(
            webhook_url,
            json=json_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"❌ Erro ao enviar: {response.status_code}")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
        return False
```

### Botões na Interface:

```python
# Após gerar a estrutura
col1, col2 = st.columns(2)

with col1:
    # Botão Download (existente)
    st.download_button(...)

with col2:
    # NOVO: Botão de envio automático
    if st.button("🚀 Enviar & Gerar Automaticamente", type="primary"):
        with st.spinner("Enviando para Make.com..."):
            sucesso = enviar_para_webhook(estrutura, "infographic")
            
            if sucesso:
                st.success("✅ Enviado com sucesso!")
                st.info("⏱️ Seu infográfico estará pronto em ~2 minutos")
                st.balloons()
            else:
                st.error("❌ Falha no envio. Baixe o JSON manualmente.")
```

---

## 📊 Monitoramento & Logs

### Ver Status das Automações:

1. **Make.com Dashboard**
   - https://make.com/scenarios
   - Ver "History" do cenário
   - Logs detalhados de cada execução

2. **Activepieces Dashboard**
   - https://cloud.activepieces.com/runs
   - Timeline de execuções

### Notificações:

Configure notificações no Make.com:
- Email quando infográfico estiver pronto
- Slack quando houver erro
- Discord para resumo diário

---

## 🚫 Troubleshooting

### Problema: Webhook não recebe dados
**Solução:**
1. Verifique se URL está correta nos Secrets
2. Teste webhook com Postman/Insomnia
3. Confira logs do Make.com

### Problema: Canva não gera design
**Solução:**
1. Verifique se template ID está correto
2. Confira permissões da API Key
3. Veja se campos estão mapeados corretamente

### Problema: Timeout na geração
**Solução:**
1. Aumente timeout no Make.com (Settings > Timeout)
2. Divida processo em múltiplos cenários
3. Use filas (Queue) para processos longos

---

## 🎉 Próximas Features (Roadmap)

- [ ] **Agendamento**: Geração automática diária
- [ ] **Batch Processing**: Múltiplos infográficos de uma vez
- [ ] **A/B Testing**: Variações automáticas de design
- [ ] **Analytics Integration**: Métricas de performance
- [ ] **Multi-idioma**: Geração simultânea em PT/EN/ES

---

**Criado por:** Sports Injury AI Studio Team  
**Última atualização:** 13 Dezembro 2025  
**Versão:** v2.2-automation  

👉 **Dúvidas?** Consulte o [guia completo](./V2-API-INTEGRATION-GUIDE.md) ou abra uma issue no GitHub.
