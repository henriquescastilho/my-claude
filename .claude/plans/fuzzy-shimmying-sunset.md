# Plano: Central de Disparos WhatsApp Multi-Número

## Contexto

O SDE WPP atualmente é um sistema de **disparo em massa unidirecional** — envia mensagens mas não recebe respostas. O objetivo é transformá-lo numa **central de WhatsApp multi-número** onde:
- Vários números WhatsApp conectados funcionam como um só
- Todas as respostas dos contatos aparecem numa caixa de entrada unificada
- Operadores podem responder por dentro do sistema
- Disparos em massa continuam funcionando com anti-ban

O bloqueio recente reforça a necessidade de multi-número: distribuir carga entre 3-5 números reduz drasticamente o risco.

---

## Fase 1: Webhook + Recebimento de Mensagens
**Objetivo:** Receber mensagens e atualizações de status da Evolution API

### Backend

**1.1 — Novos models (`models.py`)**
- `Conversation`: id, contact_id (FK), instance_id (FK), last_message_at, unread_count, status (active/archived), created_at
- `ChatMessage`: id, conversation_id (FK), direction (inbound/outbound), content, media_url, media_type, whatsapp_msg_id, status (pending/sent/delivered/read/failed), error_message, created_at
- Migrar dados existentes: cada Message da campanha vira ChatMessage com direction=outbound

**1.2 — Webhook router (`routers/webhooks.py`)**
- `POST /api/webhooks/evolution` — endpoint que a Evolution API chama
- Processar eventos:
  - `MESSAGES_UPSERT` / `messages.upsert` — mensagem recebida → criar ChatMessage(direction=inbound), atualizar Conversation.last_message_at e unread_count
  - `MESSAGES_UPDATE` / `messages.update` — status atualizado (delivered/read) → atualizar ChatMessage.status
  - `CONNECTION_UPDATE` — instância conectou/desconectou → atualizar WhatsAppInstance.status
- Extrair telefone do `remoteJid` (formato: `5521999999999@s.whatsapp.net`)
- Criar Contact automaticamente se não existir (source=whatsapp)
- Criar Conversation automaticamente se não existir para o par contact+instance

**1.3 — Configurar webhook na Evolution API**
- `docker-compose.yml`: adicionar `WEBHOOK_URL=http://host.docker.internal:8000/api/webhooks/evolution`
- `evolution.py`: adicionar método `set_webhook(instance, url, events)` para configurar por instância
- Chamar `set_webhook` automaticamente ao criar instância no router

**1.4 — Verificação de número (`evolution.py`)**
- Adicionar método `check_number(instance, phone)` que chama `POST /chat/whatsappNumbers/{instance}`
- Usar antes de enviar para evitar falhas com números sem WhatsApp

### Arquivos modificados:
- `models.py` — adicionar Conversation, ChatMessage
- `routers/webhooks.py` — novo
- `routers/instances.py` — registrar webhook ao criar instância
- `evolution.py` — set_webhook(), check_number()
- `docker-compose.yml` — WEBHOOK_URL
- `main.py` — registrar webhook router

---

## Fase 2: Caixa de Entrada Unificada
**Objetivo:** Ver todas as conversas de todos os números num único lugar

### Backend

**2.1 — Router de conversas (`routers/conversations.py`)**
- `GET /api/conversations` — lista conversas com: contact_name, contact_phone, last_message, unread_count, instance_name, updated_at. Ordenado por last_message_at DESC. Filtros: search, status(active/archived), instance_id
- `GET /api/conversations/{id}/messages` — histórico da conversa (inbound+outbound), paginado, ordem cronológica
- `POST /api/conversations/{id}/messages` — enviar mensagem (texto ou mídia) pelo número da conversa
- `PUT /api/conversations/{id}/read` — marcar como lida (unread_count=0)
- `POST /api/conversations/{id}/archive` — arquivar

### Frontend

**2.2 — Página Inbox (`pages/Inbox.tsx`)**
- Layout split-pane: lista de conversas à esquerda, chat à direita
- Lista: avatar com iniciais, nome, preview da última mensagem, badge de não-lidas, horário
- Busca por nome/telefone
- Filtro por número WhatsApp (dropdown de instâncias)
- Mobile: lista full-width, clica e abre chat full-screen

**2.3 — Componentes novos**
- `ConversationItem.tsx` — item da lista (nome, preview, badge, horário)
- `ChatBubble.tsx` — bolha de mensagem (inbound=esquerda cinza, outbound=direita verde)
- `MessageInput.tsx` — textarea + botão enviar + anexar arquivo
- `ContactHeader.tsx` — topo do chat (nome, telefone, status do número, ações)

**2.4 — Atualização em tempo real**
- Polling a cada 3s nas conversas ativas (simples e funciona)
- Quando conversa está aberta, polling a cada 2s nas mensagens
- Badge de não-lidas no sidebar (total)

### Arquivos:
- `routers/conversations.py` — novo
- `main.py` — registrar router
- `pages/Inbox.tsx` — novo
- `components/ConversationItem.tsx` — novo
- `components/ChatBubble.tsx` — novo
- `components/MessageInput.tsx` — novo
- `components/ContactHeader.tsx` — novo
- `components/Layout.tsx` — adicionar "Inbox" no sidebar com badge
- `App.tsx` — adicionar rota /inbox

---

## Fase 3: Chat Individual + Envio de Respostas
**Objetivo:** Responder contatos por dentro do sistema como se fosse WhatsApp Web

### Backend

**3.1 — Enviar mensagem individual**
- Endpoint `POST /api/conversations/{id}/messages` já criado na Fase 2
- Lógica: buscar instância da conversa, enviar via Evolution API, criar ChatMessage(direction=outbound)
- Suportar texto e mídia (upload + base64)

**3.2 — Roteamento inteligente de instância**
- Se contato já tem conversa com um número → responder pelo mesmo número
- Se contato novo → atribuir ao número com menos conversas ativas
- Manter consistência: contato X sempre fala com número Y

### Frontend

**3.3 — Interface de chat na Inbox**
- Área de mensagens com scroll infinito (carregar mais antigos ao subir)
- Bolhas com status (enviada ✓, entregue ✓✓, lida ✓✓ azul)
- Preview de mídia (imagem inline, vídeo player, doc com ícone)
- Indicador "digitando..." (opcional, fase futura)
- Textarea com Enter=enviar, Shift+Enter=nova linha

---

## Fase 4: Melhorias no Disparo em Massa
**Objetivo:** Integrar campanhas com o novo sistema de conversas

### Backend

**4.1 — Verificação pré-envio**
- Antes de disparar campanha, verificar quais números têm WhatsApp
- Marcar contatos sem WhatsApp como `whatsapp_valid=false`
- Não incluir em campanhas futuras

**4.2 — Campanhas criam conversas**
- Ao enviar mensagem de campanha, criar/atualizar Conversation
- Resposta do contato aparece na caixa de entrada vinculada à campanha

**4.3 — Rotação de números nas campanhas**
- Distribuir contatos entre instâncias de forma fixa (contato 1→instância A, contato 2→instância B)
- Manter mapa de afinidade: se contato já conversou com um número, usar o mesmo

### Frontend

**4.4 — Dashboard de números**
- Mostrar saúde de cada número: msgs enviadas hoje, status, tempo de warmup
- Alerta se número está próximo do limite
- Botão de reconectar QR direto no dashboard

---

## Ordem de Execução

| Etapa | O que | Tempo estimado | Dependência |
|-------|-------|----------------|-------------|
| 1.1 | Models (Conversation, ChatMessage) | - | - |
| 1.2 | Webhook router | - | 1.1 |
| 1.3 | Config webhook no Docker + Evolution | - | 1.2 |
| 1.4 | Verificação de número | - | - |
| 2.1 | Router de conversas | - | 1.1 |
| 2.2 | Página Inbox (frontend) | - | 2.1 |
| 2.3 | Componentes de chat | - | 2.2 |
| 2.4 | Polling tempo real | - | 2.3 |
| 3.1 | Envio de resposta individual | - | 2.1 |
| 3.2 | Roteamento de instância | - | 3.1 |
| 3.3 | Interface de chat completa | - | 3.1, 2.3 |
| 4.1 | Verificação pré-envio | - | 1.4 |
| 4.2 | Campanhas → Conversas | - | 1.1 |
| 4.3 | Rotação fixa de números | - | 3.2 |
| 4.4 | Dashboard de números | - | - |

---

## Verificação

### Fase 1 (Webhook)
- Enviar mensagem do celular para o número conectado → deve aparecer no banco (ChatMessage inbound)
- Enviar campanha → status deve atualizar para delivered/read via webhook
- Desconectar WhatsApp → status da instância deve atualizar automaticamente

### Fase 2 (Inbox)
- Abrir /inbox → ver lista de conversas ordenada por última mensagem
- Clicar numa conversa → ver histórico completo (enviadas + recebidas)
- Badge de não-lidas no sidebar deve mostrar total correto

### Fase 3 (Chat)
- Digitar e enviar mensagem no chat → contato recebe no WhatsApp
- Contato responde → mensagem aparece no chat em tempo real
- Mídia: enviar imagem pelo chat → contato recebe

### Fase 4 (Disparo melhorado)
- Criar campanha → números sem WhatsApp não são incluídos
- Enviar campanha com 3 números → mensagens distribuídas igualmente
- Contato responde campanha → aparece na inbox vinculado

---

## Arquivos Críticos

**Backend (modificar):**
- `backend/src/sde_wpp/models.py`
- `backend/src/sde_wpp/evolution.py`
- `backend/src/sde_wpp/main.py`
- `backend/src/sde_wpp/routers/instances.py`
- `backend/src/sde_wpp/workers/tasks.py`
- `docker-compose.yml`

**Backend (criar):**
- `backend/src/sde_wpp/routers/webhooks.py`
- `backend/src/sde_wpp/routers/conversations.py`

**Frontend (modificar):**
- `dashboard/src/App.tsx`
- `dashboard/src/components/Layout.tsx`

**Frontend (criar):**
- `dashboard/src/pages/Inbox.tsx`
- `dashboard/src/components/ConversationItem.tsx`
- `dashboard/src/components/ChatBubble.tsx`
- `dashboard/src/components/MessageInput.tsx`
- `dashboard/src/components/ContactHeader.tsx`
