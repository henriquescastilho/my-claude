# Plano: Finalizar Growth AI OS -- Producao Real, Zero Mocks

## Contexto

O Growth AI OS tem 111 PRs mergeadas cobrindo toda a casca do produto: UI, config, persistencia, infra, logging, performance. O que falta e ligar os **runtimes reais** para que o produto funcione de ponta a ponta em producao. O usuario quer sincronia total, zero mocks, e um teste final ao encerrar.

### Estado atual mapeado

| Sistema | Status | Detalhe |
|---------|--------|---------|
| LLM Bridge | FUNCIONAL | Groq + Anthropic fallback, retry, system prompts |
| CEO Orchestrator | FUNCIONAL | Kickoff, research, synthesis, approval, hire |
| Squad Research + Head Growth | FUNCIONAL | LLM-based generation via orchestrator |
| Conversation Handoffs | IMPLEMENTADO | Schema + service na PR #110 |
| Company Memory Facts/Edges | IMPLEMENTADO | Schema + service na PR #110 |
| Product Stacks | IMPLEMENTADO | Manifesto + tipos na PR #110 |
| CRM GHL Config | PERSISTIDO | Config save/load, sem API real do GHL |
| Email (SendGrid) | FUNCIONAL | Provider real em server/src/services/email/ |
| WhatsApp Gateway | MISSING | Zero runtime, so UI de config |
| Telegram Gateway | MISSING | Nada |
| Instagram Gateway | MISSING | Nada |
| Voice Gateway | MISSING | Nada |
| WebChat Widget | MISSING | Nada |
| Human Escalation | MISSING | Nada |
| PDF/Report Export | MISSING | Nada |
| Agent Auto-Execution | PARCIAL | heartbeat + agent-executor existem, LLM bridge funciona |

## Estrategia: 6 fases paralelas com dependencias minimas

### Fase 1 -- Merge PR #110 + Sync Main (prerequisito)
**Agente:** Manual (Henrique aprova)
- Merge PR #110 (CEO + Memoria + Templates + Stacks)
- Pull main atualizado
- Rodar `pnpm db:generate` se necessario

### Fase 2 -- Gateway Runtime Engine (critico)
**Agentes:** 2 implementers em paralelo
**Branch:** `feat/gateway-runtime`
**Arquivos novos:**
- `server/src/services/gateway-engine.ts` -- runtime core: receive inbound, route to agent, send outbound
- `server/src/services/gateway-providers/whatsapp-zapi.ts` -- Z-API provider
- `server/src/services/gateway-providers/whatsapp-evolution.ts` -- Evolution API provider (alternativa)
- `server/src/services/gateway-providers/telegram-bot.ts` -- Telegram Bot API
- `server/src/services/gateway-providers/instagram-meta.ts` -- Meta Graph API (DM + publish)
- `server/src/services/gateway-providers/webchat-ws.ts` -- WebSocket inbound/outbound
- `server/src/routes/gateway-webhooks.ts` -- webhooks de inbound (WhatsApp, Telegram, Instagram)
- `server/src/routes/webchat.ts` -- WebSocket endpoint para widget

**Arquivos modificados:**
- `server/src/app.ts` -- registrar novas rotas
- `server/src/services/index.ts` -- exportar novos services
- `packages/db/src/schema/` -- tabela `channel_messages` para log de mensagens
- `packages/shared/src/types/` -- tipos de gateway

**Logica core:**
```
Inbound webhook → normalize message → find company by channel config
  → find assigned agent → build context (company + handoff + facts)
  → call LLM bridge with agent system prompt + context + message
  → send response via outbound provider
  → save to channel_messages + update conversation
```

**Providers por prioridade:**
1. WhatsApp (Z-API -- mais simples, webhook + REST)
2. Email (SendGrid -- JA EXISTE, so conectar ao engine)
3. Telegram (Bot API -- simples, webhook + REST)
4. Instagram DM (Meta Graph API -- OAuth flow)
5. WebChat (WebSocket -- sem dependencia externa)
6. Voice (Vapi -- complexo, ultima prioridade)

### Fase 3 -- Agent Auto-Execution Real (critico)
**Agente:** 1 implementer
**Branch:** `feat/agent-auto-execution`
**Arquivos modificados:**
- `server/src/services/agent-executor.ts` -- garantir que execucao real via LLM funciona
- `server/src/services/heartbeat.ts` -- verificar ciclo de execucao
- `server/src/services/conversations.ts` -- CEO usa retrieval pack real

**Logica:**
- Agent recebe issue → monta contexto (instructions + company data + handoff) → chama LLM bridge → processa resposta → cria work product → atualiza issue
- CEO recebe mensagem → monta retrieval pack (snapshot + handoff + facts + agents map) → chama LLM → responde com acoes reais (criar issue, delegar, reportar)
- Heartbeat verifica agents com issues pendentes e executa ciclo

### Fase 4 -- CRM GHL Real + Human Escalation
**Agente:** 1 implementer
**Branch:** `feat/crm-ghl-real`
**Arquivos novos:**
- `server/src/services/crm-ghl-api.ts` -- client HTTP para GHL API real
- `server/src/services/human-escalation.ts` -- logica de handover

**Arquivos modificados:**
- `server/src/services/crm-ghl.ts` -- adicionar metodos que chamam API real
- `server/src/routes/crm-ghl.ts` -- endpoints de sync bidirecional

**Logica GHL:**
- Sync contacts: GHL → Growth AI OS e vice-versa
- Create/update opportunities no pipeline
- Webhook receiver para eventos GHL (novo lead, stage change)
- Tags automaticas baseadas em eventos do gateway

**Logica Escalation:**
- Agent detecta trigger de escalacao (keyword, sentiment, pedido explicito)
- Cria notificacao para humano
- Pausa resposta automatica no canal
- Humano assume via UI ou notificacao externa
- Ao encerrar, devolve para agent

### Fase 5 -- Report/PDF + Relatorio Publico
**Agente:** 1 implementer
**Branch:** `feat/intelligence-report`
**Arquivos novos:**
- `server/src/services/report-generator.ts` -- gera HTML/PDF do relatorio
- `server/src/routes/public-reports.ts` -- rota publica para link compartilhavel

**Arquivos modificados:**
- `server/src/routes/documents.ts` -- endpoint de export PDF
- `ui/src/pages/IntelligenceReport.tsx` -- pagina de visualizacao do relatorio

**Logica:**
- Pega documentos de research + strategic document
- Gera HTML formatado com branding da empresa
- Converte para PDF via puppeteer/playwright ou html-pdf
- Gera link publico com token unico (expiravel)
- Advisor usa para prospectar clientes

### Fase 6 -- Teste Final E2E + Smoke
**Agente:** 1 tester
**Branch:** `feat/e2e-final`
**Arquivos:**
- `tests/e2e/production-flow.spec.ts` -- teste completo do fluxo

**Cenarios de teste:**
1. Criar empresa via wizard com product stack
2. CEO responde mensagem do dono (via DM)
3. Template aplicado cria agents esperados
4. Agent recebe issue e executa via LLM
5. Gateway WhatsApp recebe mensagem inbound e responde (mock de webhook, resposta real do LLM)
6. CRM GHL sync bidirecional (se API key configurada, senao skip)
7. Relatorio de inteligencia gerado e acessivel via link publico
8. Handoff e memory facts persistidos e usados no contexto
9. Typecheck + lint + build passam
10. Smoke test via `./start.sh`

## Ordem de execucao e paralelismo

```
Fase 1 (merge #110) ──────────────────────────────┐
                                                    │
Fase 2 (Gateway Runtime) ─────────────────────────►│
                                                    ├──► Fase 6 (Teste Final)
Fase 3 (Agent Execution) ─────────────────────────►│
                                                    │
Fase 4 (CRM GHL + Escalation) ───────────────────►│
                                                    │
Fase 5 (Report/PDF) ──────────────────────────────►│
```

Fases 2, 3, 4 e 5 rodam em **paralelo** apos Fase 1.
Fase 6 roda apos todas as anteriores.

## Verificacao

Ao final de cada fase:
1. `npx tsc --noEmit` em todos os pacotes afetados
2. `pnpm test:run` para testes unitarios
3. Build completo `pnpm build`
4. Smoke test: `./start.sh` e verificar endpoints no browser

Ao final do plano completo:
1. Todos os testes passam
2. Build limpo
3. E2E do fluxo completo passa
4. PR final com tudo integrado

## Arquivos criticos a nao quebrar
- `server/src/app.ts` -- registro de rotas
- `server/src/services/conversations.ts` -- CEO + retrieval pack
- `server/src/services/heartbeat.ts` -- ciclo de execucao
- `packages/db/src/schema/index.ts` -- exports de schema
- `ui/src/App.tsx` -- rotas UI
- `ui/src/components/Sidebar.tsx` -- navegacao
