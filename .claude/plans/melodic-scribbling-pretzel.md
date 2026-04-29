# Plano: Módulo NF-e + Tesouraria para Escritório Contábil

## Contexto

A PaymentsLine precisa virar a ferramenta completa de tesouraria para escritórios de contabilidade. O módulo NF-e conecta o fiscal ao financeiro: rastreia notas, vincula a pagamentos, detecta inconsistências e gera lançamentos contábeis. Um escritório com 50 clientes pagaria R$1.347/mês (BUSINESS R$597 + R$15/CNPJ), margem 46%.

**O que já existe** (e será reutilizado):
- `NfeDocument` model com 16 colunas, `NfeIntegration` model
- XML parser (`_extract_nfe_fields()` em main.py:598-632) usando defusedxml
- Auto-match NF-e↔boleto (`_score_nfe_boleto_match()` em main.py:677-724)
- Router nfe.py (422 linhas): import XML, auto-match, link/unlink, audit
- Frontend notas-fiscais (26KB): upload, match, filtros, auditoria
- 10 testes em test_nfe.py
- EmailClient (15+ templates), Pub/Sub workers, AuditEvent, AccountingEvent
- Gemini OCR, ReconciliationService, GCS storage

**O que falta**: direção entrada/saída, impostos (CFOP/ICMS/PIS/COFINS), captura automática (IMAP/SEFAZ), detecção de órfãos, validação de valores, alertas, lançamentos contábeis.

**Pré-requisito**: commitar as mudanças locais pendentes (CORS, auth, pricing, subscription sync — 14 arquivos modificados, já deployados em prod).

---

## Fase 1: Enriquecer Modelo de Dados + Classificação (2 dias)

**Objetivo**: NfeDocument suporta todas as 6 funcionalidades. Fundação para tudo.

### Migration 047_nfe_treasury_fields

```sql
-- NfeDocument: campos fiscais + classificação
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS direction TEXT DEFAULT 'unknown';
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS operation_type TEXT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS cfop TEXT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS nature_of_operation TEXT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS icms_total_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS pis_total_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS cofins_total_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS ipi_total_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS iss_total_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS validation_status TEXT DEFAULT 'pending';
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS validation_details JSON;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS matched_amount_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS amount_divergence_cents BIGINT;
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual_xml';
ALTER TABLE nfe_documents ADD COLUMN IF NOT EXISTS gcs_path TEXT;
-- NfeIntegration: config de sync
ALTER TABLE nfe_integrations ADD COLUMN IF NOT EXISTS provider_config JSON;
ALTER TABLE nfe_integrations ADD COLUMN IF NOT EXISTS last_sync_at TIMESTAMPTZ;
ALTER TABLE nfe_integrations ADD COLUMN IF NOT EXISTS sync_status TEXT DEFAULT 'idle';
ALTER TABLE nfe_integrations ADD COLUMN IF NOT EXISTS sync_error TEXT;
-- Indices
CREATE INDEX IF NOT EXISTS idx_nfe_docs_direction ON nfe_documents(tenant_id, direction);
CREATE INDEX IF NOT EXISTS idx_nfe_docs_validation ON nfe_documents(tenant_id, validation_status);
```

### Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `backend/services/shared/models.py` (linhas 733-758) | Adicionar novas colunas ao NfeDocument e NfeIntegration |
| `backend/services/api/main.py` (linhas 598-652) | Expandir `_extract_nfe_fields()`: extrair CFOP de `det/prod/CFOP`, impostos de `ICMSTot`, natureza de `ide/natOp`, classificar direção comparando CNPJ tenant vs issuer/recipient |
| `backend/services/api/routers/nfe.py` (linhas 106-119) | Adicionar filtros em GET /api/nfe/documents: direction, validation_status, date_from/to, search |
| `backend/services/api/routers/admin.py` | Adicionar migration 047 ao dict |

### Arquivo novo

| Arquivo | Conteúdo |
|---------|----------|
| `backend/services/shared/nfe_service.py` | Extrair toda lógica NF-e de main.py (elimina lazy imports circulares em nfe.py): `extract_nfe_fields()`, `score_nfe_boleto_match()`, `run_nfe_auto_match()`, `classify_direction()` |

---

## Fase 2: Detecção de Órfãos + Validação (2-3 dias)

**Objetivo**: Identificar NF-e sem pagamento, pagamento sem NF-e, divergências de valor. Core value para contadores.

### Novos endpoints em nfe.py

| Endpoint | O que faz |
|----------|-----------|
| `GET /api/nfe/orphans` | LEFT JOIN nfe_documents↔boletos, retorna {nfe_without_payment, payments_without_nfe, summary} |
| `POST /api/nfe/validate` | Executa regras: divergência de valor, duplicatas, CFOP missing, boleto cancelado. Atualiza validation_status |
| `GET /api/nfe/reconciliation` | Agregado mensal: total entrada, total saída, linked vs unlinked |

### Lógica em nfe_service.py

- `detect_orphans(db, tenant_id, date_from, date_to)` — Query com LEFT JOIN
- `validate_nfe_documents(db, tenant_id, threshold_cents=100)` — Engine de regras
- `detect_duplicates(db, tenant_id)` — Same issuer + amount + date window 3 dias
- `fiscal_reconciliation_summary(db, tenant_id, period)` — Agregação mensal

### Reutilizar
- Padrão do `ReconciliationService` (match + anomaly detection)
- `_score_nfe_boleto_match()` como base para orphan detection

---

## Fase 3: Alertas Inteligentes (1-2 dias)

**Objetivo**: Notificações proativas de anomalias fiscais.

### Migration 048_nfe_alerts

```sql
CREATE TABLE IF NOT EXISTS nfe_alerts (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  alert_type TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'MEDIUM',
  nfe_document_id UUID REFERENCES nfe_documents(id),
  details JSON,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_nfe_alerts_tenant ON nfe_alerts(tenant_id, status);
```

### Arquivos novos

| Arquivo | Conteúdo |
|---------|----------|
| `backend/services/shared/nfe_alerts.py` | 4 funções de alerta: `nfe_issued_not_received()`, `nfe_received_no_payment()`, `amount_divergence()`, `possible_duplicates()` |

### Endpoints em nfe.py

| Endpoint | O que faz |
|----------|-----------|
| `GET /api/nfe/alerts` | Lista alertas ativos do tenant |
| `POST /api/nfe/alerts/{id}/dismiss` | Marca alerta como dismissed |
| `POST /api/nfe/alerts/refresh` | Recalcula alertas (on-demand) |

### EmailClient (email_client.py)

Novo método: `send_nfe_daily_digest(to_email, alerts)` — email consolidado com todos os alertas do dia, template dark/gold.

### Reutilizar
- `EmailClient` branded templates
- `AuditEvent` para log de alertas
- Orphan detection da Fase 2

---

## Fase 4: Worker de Captura Automática (4-5 dias)

**Objetivo**: Ingestão automática via email (IMAP) e futuramente SEFAZ/Arquivei.

### Novo Pub/Sub topic: `topic-nfe-ingest`

### Novo worker

```
backend/services/worker_nfe_ingest/
├── __init__.py
├── main.py          # FastAPI app (padrão worker_extract)
├── imap_client.py   # Conecta IMAP, busca XMLs em anexo
└── Dockerfile       # Copia do worker_extract
```

### Fluxo IMAP
1. Recebe mensagem Pub/Sub `{tenant_id, source: "imap"}`
2. Lê config de `nfe_integrations.provider_config` (creds encriptadas)
3. Conecta IMAP, busca emails não lidos com `.xml` attachment
4. Para cada XML: `extract_nfe_fields()` → dedup (xml_hash) → insert NfeDocument com `source='email_imap'`
5. Armazena XML no GCS
6. Trigger auto-match para documentos novos
7. Atualiza `last_sync_at`, `sync_status`

### Endpoints em nfe.py

| Endpoint | O que faz |
|----------|-----------|
| `POST /api/integrations/nfe/configure` | Salva config IMAP/Arquivei (encripta credentials) |
| `POST /api/integrations/nfe/sync` | Publica mensagem no topic-nfe-ingest |
| `GET /api/integrations/nfe/sync-status` | Retorna last_sync_at, status, error |

### Segurança
- Credentials IMAP encriptadas com `FIELD_ENCRYPTION_KEY` (já existe no Secret Manager)
- Nunca plaintext no PostgreSQL

### Reutilizar
- Padrão worker_extract (FastAPI + Pub/Sub push)
- `publish_to_worker()` de main.py
- `_extract_nfe_fields()` de nfe_service.py
- `StorageClient` para GCS upload

---

## Fase 5: Automação Contábil (2-3 dias)

**Objetivo**: Gerar lançamentos contábeis a partir de NF-e + pagamento.

### Migration 049_accounting_nfe

```sql
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS nfe_document_id UUID REFERENCES nfe_documents(id);
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS debit_account TEXT;
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS credit_account TEXT;
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS amount_cents BIGINT;
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS tax_amount_cents BIGINT;
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS fiscal_period TEXT;
ALTER TABLE accounting_events ADD COLUMN IF NOT EXISTS classification TEXT;
```

### Arquivo novo

| Arquivo | Conteúdo |
|---------|----------|
| `backend/services/shared/accounting_engine.py` | `generate_entries_from_nfe(nfe_doc, boleto)` — usa CFOP pra determinar débito/crédito. Tabela dos 20 CFOPs mais comuns (5101, 5102, 1101, 1102, etc). Gera entries separadas para cada imposto. Idempotente (checa se já existe por nfe_document_id). |

### Endpoints em nfe.py

| Endpoint | O que faz |
|----------|-----------|
| `POST /api/nfe/documents/{id}/generate-accounting` | Gera lançamentos para 1 NF-e |
| `POST /api/nfe/accounting/generate-batch` | Gera para todos NF-e linked sem lançamento no período |
| `GET /api/nfe/accounting/summary` | Agregado por período fiscal, conta, classificação |
| `GET /api/nfe/accounting/export` | CSV para importação em ERP |

### Reutilizar
- `AccountingEvent` model (extender)
- CSV export pattern de flows.py

---

## Fase 6: Frontend (3 dias)

**Objetivo**: Surfar todas as funcionalidades no dashboard.

### Modificar: `frontend/src/app/(dashboard)/notas-fiscais/page.tsx`

Adicionar tabs:
1. **Visão Geral** — Cards: total NF-e, % linked, órfãos, alertas, impostos por período
2. **Órfãos** — Duas colunas: NF-e sem pagamento / Pagamentos sem NF-e, ações rápidas de link
3. **Alertas** — Lista com badges de severidade, dismiss/resolver
4. **Conciliação** — Grid mensal NF-e vs pagamentos
5. **Contabilidade** — Lançamentos gerados, botão gerar, export CSV

### Modificar: `frontend/src/lib/api.ts`

Novas funções: `getNfeOrphans()`, `validateNfeDocuments()`, `getNfeAlerts()`, `dismissNfeAlert()`, `configureNfeIntegration()`, `triggerNfeSync()`, `generateNfeAccounting()`, `getNfeAccountingSummary()`, `exportNfeAccounting()`

---

## Ordem de Execução e Dependências

```
Commit pending changes (prerequisite)
    │
    v
Fase 1 (Modelo + Classificação) ─── 2 dias
    │
    ├──> Fase 2 (Órfãos + Validação) ── 2-3 dias
    │         │
    │         └──> Fase 3 (Alertas) ── 1-2 dias
    │
    └──> Fase 4 (Worker Captura) ── 4-5 dias (paralelo com Fase 2-3)
    │
    v
Fase 5 (Contabilidade) ── 2-3 dias (depende de Fase 1)
    │
    v
Fase 6 (Frontend) ── 3 dias (depende de todas as fases backend)
```

**Total estimado: 14-18 dias (solo dev)**
**Com paralelização de Fase 2-3 e Fase 4: ~12 dias**

---

## Verificação (como testar)

1. **Fase 1**: Upload XML de NF-e → verificar que direction, CFOP, impostos são extraídos. Filtrar por direção no endpoint.
2. **Fase 2**: Criar boletos sem NF-e e NF-e sem boletos → GET /api/nfe/orphans retorna ambos. POST /api/nfe/validate detecta divergências.
3. **Fase 3**: Criar cenários de órfãos → POST /api/nfe/alerts/refresh gera alertas. GET /api/nfe/alerts lista. Email chega com digest.
4. **Fase 4**: Configurar IMAP de teste → POST /api/integrations/nfe/sync → verificar NfeDocuments criados automaticamente.
5. **Fase 5**: NF-e linked a boleto → POST generate-accounting → GET summary mostra lançamentos com débito/crédito corretos por CFOP.
6. **Fase 6**: Navegar tabs no frontend, verificar dados em cada view.

### Testes automatizados
- Expandir `test_nfe.py` com testes para: orphan detection, validation rules, duplicate detection, accounting generation, direction classification.
