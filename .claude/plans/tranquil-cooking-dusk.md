# Plano de Execucao — Co-Pilot: Security + Bug Fixes + Performance

## Contexto

O pentest agressivo (5 agentes) e o trace de features (2 agentes) revelaram:
- **35 vulnerabilidades de seguranca** (5 CRITICAL, 14 HIGH)
- **Scheduler desconectado** — alertas e reports agendados nunca executam
- **20+ bugs** across insights, recommendations, alerts, reports
- **Latencia alta** — queries N+1, zero caching, geracão sincrona de reports

O plano esta organizado em 3 ondas com dependencias claras.

---

## ONDA 1 — Seguranca (Urgente)

### 1.1 XSS no MarkdownRenderer
- **Arquivo**: `src/components/ui/markdown-renderer.tsx:64-72`
- **Fix**: Sanitizar `href` no componente `a` — rejeitar qualquer URI que nao comece com `http://` ou `https://` (ou path relativo `/`)
- **Tambem**: `src/app/agendar/page.tsx:414` — validar `meetLink` contra `https://meet.google.com/`

### 1.2 Rate Limits Ausentes
- **Arquivo**: `backend/app/security/rate_limiter.py:41-51`
- **Adicionar regras**:
  - `("/api/v1/auth/refresh", "ip", "RATE_LIMIT_LOGIN")`
  - `("/api/v1/auth/change-password", "ip", "RATE_LIMIT_LOGIN")`
  - `("/api/v1/billing", "user", "RATE_LIMIT_CHAT")`
  - `("/api/v1/kpis", "user", "RATE_LIMIT_CONNECTIONS")`
  - `("/api/v1/insights", "user", "RATE_LIMIT_CONNECTIONS")`
  - `("/api/v1/dashboards", "user", "RATE_LIMIT_CONNECTIONS")`
  - `("/api/v1/webhooks", "ip", "RATE_LIMIT_LOGIN")`
- **Arquivo**: `backend/app/core/settings/settings.py` — adicionar `RATE_LIMIT_ADMIN: str = "60/minute"`

### 1.3 IDOR em DashboardKPI
- **Arquivo**: `backend/app/api/routes/dashboards.py:248-307`
- **Fix**: Adicionar `DashboardKPI.company_id == user.company_id` (ou join via Dashboard) em update_kpi, delete_kpi, update_layout

### 1.4 JWT Claims (iss/aud)
- **Arquivo**: `backend/app/security/auth.py:26-50, 102-112`
- **Fix**: Adicionar `iss="copilot-api"` e `aud="copilot-client"` ao payload; validar no decode

### 1.5 Password no Frontend Admin
- **Arquivo**: `src/app/(admin)/admin/accounts/page.tsx:47-53, 97`
- **Fix**: Remover `password` do state React e do DOM. Remover do template WhatsApp.

### 1.6 Health Endpoints Abertos
- **Arquivo**: `backend/app/api/routes/metrics.py:98-291`
- **Fix**: Proteger `/health/detailed` e `/health/workers` com `verify_metrics_api_key`
- **Fix**: Substituir `str(e)` por status generico nos error bodies

### 1.7 Proxy Header Injection
- **Arquivo**: `src/app/api/proxy/[...path]/route.ts:39-43`
- **Fix**: Allowlist explicita de headers: `content-type`, `accept`, `x-request-id`, `accept-language`

### 1.8 Identifier Injection (SQL)
- **Arquivos**:
  - `backend/app/services/schema_context_builder.py:280,295,317,330,357,383`
  - `backend/app/services/connection_profiler.py:159,185,216`
  - `backend/app/workers/schema_refresh_worker.py:188,204`
  - `backend/app/services/dashboard_generator.py:139`
- **Fix**: Chamar `connector._validate_identifier(name)` antes de cada interpolacao f-string

### 1.9 API Key Delete sem Role Check
- **Arquivo**: `backend/app/api/routes/api_keys.py:101-115`
- **Fix**: Adicionar `require_role([UserRole.OWNER, UserRole.ADMIN])` no delete endpoint

### 1.10 npm audit fix
- **Fix**: Rodar `npm audit fix` para resolver protobufjs RCE, Next.js DoS, vite path traversal, dompurify XSS bypass

---

## ONDA 2 — Funcionalidade Quebrada

### 2.1 Wiring do Scheduler (CRITICAL)
**Problema**: `process_scheduled_alerts()` e `ReportSchedule.next_run_at` existem mas nada os chama.

**Abordagem**: Adicionar execucao de alertas e reports pendentes diretamente no scheduler tick.

- **Arquivo**: `backend/app/api/routes/scheduler.py:62-127`
- **Adicionar apos o loop de orchestrate()**:
  1. Chamar `AlertEngine.process_scheduled_alerts(session)` 
  2. Query `ReportSchedule WHERE next_run_at <= now() AND is_active = true`
  3. Para cada schedule pendente: chamar `ReportEngine.generate_report()`
  4. Atualizar `last_run_at`, `next_run_at`, `run_count`
- **Tambem**: Registrar AlertWorker no lifespan do FastAPI (`backend/app/api/main.py:82-172`) como fallback

### 2.2 Alert Trigger retorna 200 em falha
- **Arquivo**: `backend/app/api/routes/alerts.py:329-334`
- **Fix**: Retornar HTTP 500 ou 422 quando `engine.execute_alert` falha

### 2.3 Alert `"from"` keyword misclassifica NL como SQL
- **Arquivo**: `backend/app/core/alert_engine.py:237`
- **Fix**: Remover `"from"` da lista de keywords SQL, ou usar heuristica mais robusta (ex: regex `^\s*SELECT\b`)

### 2.4 Retry sleep dentro do HTTP request
- **Arquivo**: `backend/app/core/alert_engine.py:402-409`
- **Fix**: Remover retry no path sincrono (trigger manual). Retry so para execucao background.

### 2.5 Report sempre MONTHLY via chat
- **Arquivo**: `backend/app/agents/chat_tools.py:341`
- **Fix**: Usar o `report_type` parameter para determinar o period

### 2.6 Report `formatted_report` descartado
- **Arquivo**: `backend/app/api/routes/reports.py:167`
- **Fix**: Atribuir a variavel e usar no response

### 2.7 Insight notifications para lista vazia
- **Arquivo**: `backend/app/workers/vigilant_worker.py:186`
- **Fix**: Buscar email do user/company owner antes de enviar; skip se nenhum destinatario

### 2.8 `metrics_analyzed` sempre 0
- **Arquivo**: `backend/app/api/routes/insights.py:201`
- **Fix**: Contar candidatos realmente analisados e retornar no response

### 2.9 `updated_at` nunca atualiza em recommendations
- **Arquivo**: `backend/app/api/routes/recommendations.py:129`
- **Fix**: Adicionar `recommendation.updated_at = datetime.now(UTC)` no update path
- **Tambem**: Adicionar `onupdate=func.now()` no model

### 2.10 Validate role como @field_validator
- **Arquivos**: `backend/app/api/routes/team.py:44-49`
- **Fix**: Mover `validate_role()` para `@field_validator` no Pydantic schema

---

## ONDA 3 — Performance / Latencia

### 3.1 Report Generation Async
- **Arquivo**: `backend/app/api/routes/reports.py:112-165`
- **Fix**: POST /generate retorna 202 Accepted com `execution_id`. Executa em background task. Frontend poll via GET /reports/{id} ate `status != "running"`.
- **Tambem**: Adicionar timeout no `team.arun()` em `report_workflow.py`

### 3.2 Connection Pooling no Anomaly Scan
- **Arquivo**: `backend/app/services/anomaly_detection_service.py:494`
- **Fix**: Abrir connector UMA VEZ, executar todos os candidates, fechar no final. Elimina N+1 connections.

### 3.3 Consolidar Queries em Insights
- **Arquivo**: `backend/app/api/routes/insights.py:58-83`
- **Fix**: Usar window function `COUNT(*) OVER()` para eliminar count query separada. Mover unread count para o endpoint dedicado (ja existe).

### 3.4 staleTime nos Hooks React Query
- **Arquivos**: 
  - `src/hooks/useInsights.ts` — `staleTime: 30_000`
  - `src/hooks/useRecommendations.ts` — `staleTime: 30_000`
  - `src/hooks/useAlerts.ts` — `staleTime: 30_000`
  - `src/hooks/useReports.ts` — `staleTime: 60_000`

### 3.5 Indices Faltantes no Banco (nova migration)
- `proactive_insights`: index em `(company_id, is_dismissed, created_at)`
- `recommendations`: index em `(company_id, status)`
- `alerts`: index em `(company_id, is_active)`
- `alert_history`: index em `triggered_at`

### 3.6 Scheduler Sequential → Concurrent
- **Arquivo**: `backend/app/api/routes/scheduler.py:78`
- **Fix**: `asyncio.gather(*[engine.orchestrate(cid) for cid in company_ids])` com semaphore

### 3.7 SQL Multi-Dialect no Anomaly Detection
- **Arquivo**: `backend/app/services/anomaly_detection_service.py:357-373`
- **Fix**: Usar SQLAlchemy expressions ou dialect-aware SQL builder em vez de PostgreSQL-only syntax

---

## Verificacao

### Seguranca
- [ ] `npm audit` retorna 0 vulnerabilidades HIGH+
- [ ] Markdown `[x](javascript:alert(1))` renderiza como `href="#"`
- [ ] 6+ requests rapidos em `/auth/refresh` retorna 429
- [ ] PATCH em KPI de outro tenant retorna 404
- [ ] `/health/detailed` sem token retorna 403

### Funcionalidade
- [ ] Criar alerta com cron → esperar tick → alert_history populada
- [ ] Criar report schedule → esperar tick → report gerado
- [ ] Trigger manual de alerta falho retorna HTTP != 200
- [ ] Report via chat respeita periodo solicitado
- [ ] Recommendation update atualiza `updated_at`

### Performance
- [ ] POST /reports/generate retorna 202 em < 1s
- [ ] Insights page load < 500ms (era 2-5s)
- [ ] Anomaly scan usa 1 conexao por scan (nao N)
- [ ] Navegacao rapida entre paginas nao dispara refetch

---

## Ordem de Execucao

```
Onda 1 (Seguranca)     → ~30 items, pode ser parallelizada em 3-4 agentes
Onda 2 (Bugs)          → ~10 items, maioria sequencial (scheduler primeiro)
Onda 3 (Performance)   → ~7 items, pode ser parallelizada
```

Cada onda termina com verificacao antes de avancar para a proxima.
