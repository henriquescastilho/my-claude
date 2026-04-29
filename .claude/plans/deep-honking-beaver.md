# Plano: Agent Control Plane (Paperclip adaptado)

## Contexto

O Co-Pilot AI ja tem 4 agentes C-level (CFO/CMO/COO/CRO) + Analyst + Orchestrator, alem de sistemas proativos (PulseEngine, VigilantWorker, MACEO). Porem, esses agentes nao tem perfil configuravel, orcamento, historico de tarefas, ou trilha de auditoria. O usuario quer adaptar conceitos do Paperclip (control plane para agentes IA) ao Co-Pilot, transformando os agentes existentes em uma equipe autonoma, rastreavel e governavel.

**Diferenca-chave do Paperclip:** Co-Pilot e SaaS multi-tenant. Cada "company" e um CLIENTE, nao uma org de IA. Os agentes servem o cliente.

---

## Fase 1 (MVP): Perfis, Tarefas, Orcamento, Auditoria

### 1. Novos modelos DB (3 tabelas)

#### 1a. `AgentProfile` -- `backend/app/db/models/agent_profile.py`
Configuracao por empresa. 5 perfis pre-criados no registro.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| company_id | UUID FK companies.id CASCADE | Tenant |
| role | String(30) | cfo, cmo, coo, cro, analyst |
| display_name | String(100) | Nome exibido (ex: "Diretor Financeiro") |
| is_enabled | Boolean default=True | Agente ativo? |
| monthly_token_budget | Integer nullable | null = sem limite dedicado |
| monthly_token_used | Integer default=0 | Reset mensal |
| budget_warning_pct | Integer default=80 | Alerta em 80% |
| budget_hard_stop | Boolean default=True | Bloquear ao exceder? |
| pulse_enabled | Boolean default=True | Pulse ativo? |
| pulse_interval_hours | Integer default=24 | Intervalo entre pulses |
| last_pulse_at | DateTime nullable | Ultimo pulse |
| last_heartbeat_at | DateTime nullable | Ultimo heartbeat |
| heartbeat_status | String(20) default="idle" | idle, running, error, budget_exceeded |
| total_tasks_completed | Integer default=0 | Denormalizado |
| total_insights_generated | Integer default=0 | Denormalizado |
| config | JSONB nullable | Configuracoes extensiveis |

- UniqueConstraint(company_id, role)
- Index(company_id, is_enabled)

#### 1b. `AgentTask` -- `backend/app/db/models/agent_task.py`
Tickets de trabalho dos agentes.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| company_id | UUID FK companies.id CASCADE | Tenant |
| creator_role | String(30) | Quem criou (cfo, system, pulse) |
| assignee_role | String(30) nullable | Quem executa |
| title | String(500) | Titulo |
| description | Text nullable | Descricao |
| task_type | String(50) | analysis, investigation, report, alert_followup, delegation |
| priority | String(20) default="medium" | low, medium, high, critical |
| status | String(20) default="pending" | pending, in_progress, completed, failed, cancelled |
| source_insight_id | UUID FK proactive_insights.id SET NULL | Insight de origem |
| parent_task_id | UUID FK self SET NULL | Cadeia de delegacao |
| started_at | DateTime nullable | Inicio |
| completed_at | DateTime nullable | Conclusao |
| result_summary | Text nullable | Resumo do resultado |
| result_data | JSONB nullable | Dados do resultado |
| tokens_consumed | Integer default=0 | Tokens usados |
| error_message | Text nullable | Erro |
| locked_at | DateTime nullable | Checkout atomico |
| lock_expires_at | DateTime nullable | Expiracao do lock |

- Index(company_id, status)
- Index(company_id, assignee_role, status)

#### 1c. `AgentActivityLog` -- `backend/app/db/models/agent_activity_log.py`
Trilha de auditoria imutavel (append-only).

| Campo | Tipo | Descricao |
|-------|------|-----------|
| company_id | UUID FK companies.id CASCADE | Tenant |
| agent_role | String(30) | cfo, cmo, vigilant, system |
| action | String(100) | pulse_started, task_created, task_completed, budget_warning, insight_generated, error |
| description | Text nullable | Descricao legivel |
| task_id | UUID FK agent_tasks.id SET NULL | Referencia |
| insight_id | UUID FK proactive_insights.id SET NULL | Referencia |
| tokens_used | Integer default=0 | Tokens nesta acao |
| duration_ms | Float nullable | Duracao |
| metadata_ | JSONB("metadata") nullable | Dados extras |

- Index(company_id, created_at)
- Index(company_id, agent_role, created_at)

### 2. Migration Alembic

Arquivo: `backend/alembic/versions/031_add_agent_control_plane.py`
- Cria 3 tabelas
- Data migration: seed 5 AgentProfile para cada Company ACTIVE existente

### 3. Service layer (2 arquivos novos)

#### 3a. `backend/app/services/agent_profile_service.py`
- `seed_profiles(session, company_id)` -- cria 5 perfis default
- `get_profiles(session, company_id)` -- lista perfis
- `get_profile(session, company_id, role)` -- perfil unico
- `update_profile(session, company_id, role, **kwargs)` -- atualiza config
- `check_budget(session, company_id, role)` -> (allowed, remaining, pct_used)
- `record_agent_usage(session, company_id, role, tokens)` -- incrementa monthly_token_used
- `reset_monthly_budgets(session)` -- zera monthly_token_used (chamado pelo scheduler no 1o dia do mes)
- `log_activity(session, company_id, role, action, ...)` -- cria AgentActivityLog

#### 3b. `backend/app/services/agent_task_service.py`
- `create_task(session, company_id, ...)` -- cria task + activity log
- `list_tasks(session, company_id, filters)` -- lista paginada
- `checkout_task(session, task_id, role)` -- lock atomico (UPDATE WHERE locked_at IS NULL)
- `complete_task(session, task_id, ...)` -- marca completa + activity log
- `fail_task(session, task_id, error)` -- marca falha + activity log
- `get_task_stats(session, company_id)` -- contagens por status/role

### 4. Schemas Pydantic

Arquivo: `backend/app/schemas/agents.py`
- AgentProfileResponse, AgentProfileUpdateRequest
- AgentTaskResponse, AgentTaskListResponse
- AgentActivityLogResponse
- AgentStatsResponse

### 5. API endpoints

Arquivo: `backend/app/api/routes/agents.py`

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | /agents/profiles | Listar perfis da empresa |
| GET | /agents/profiles/{role} | Detalhe de um agente |
| PATCH | /agents/profiles/{role} | Atualizar config (OWNER/ADMIN) |
| GET | /agents/tasks | Listar tasks (filtros: status, role, priority) |
| GET | /agents/tasks/{task_id} | Detalhe da task |
| GET | /agents/activity | Log de atividade (filtros: role, action, datas) |
| GET | /agents/stats | Estatisticas agregadas |

Registrar router em `backend/app/api/main.py`.

### 6. Integracoes com codigo existente

#### 6a. `backend/app/core/pulse_engine.py`
- Em `_pulse_connection()`: antes de rodar um role, chamar `check_budget()`. Se excedido e hard_stop=True, pular e logar.
- Apos execucao: chamar `record_agent_usage()`, criar `AgentTask(task_type="analysis", status="completed")` linkado ao insight.
- Criar `AgentActivityLog` para cada pulse (sucesso ou falha).
- Atualizar `AgentProfile.last_pulse_at` e `heartbeat_status`.

#### 6b. `backend/app/api/routes/scheduler.py`
- Adicionar secao: reset mensal de budgets (1o tick do mes).
- Apos MACEO/Pulse: bulk-update `AgentProfile.last_heartbeat_at`.

#### 6c. `backend/app/workers/vigilant_worker.py`
- Apos persistir insight: criar `AgentActivityLog(agent_role="vigilant")`.

#### 6d. `backend/app/api/routes/auth.py` (linha 86)
- Apos `session.flush()` da Company: chamar `seed_profiles(session, company.id)`.

#### 6e. `backend/app/db/models/__init__.py`
- Adicionar imports e __all__ para AgentProfile, AgentTask, AgentActivityLog.

### 7. Frontend

#### 7a. Sidebar -- `src/components/dashboard/sidebar.tsx`
- Adicionar `{ label: "Agentes", href: "/agents", icon: Bot }` apos "Insights" (Lucide Bot icon)

#### 7b. Pagina principal -- `src/app/(dashboard)/agents/page.tsx`
- Grid de 5 cards (CFO, CMO, COO, CRO, Analyst)
- Cada card: icone do role, display_name, status dot (verde/amarelo/vermelho/cinza), barra de orcamento, ultimo pulse, contadores
- Toggle ativar/desativar (OWNER/ADMIN)
- Barra de resumo no topo: tokens totais, agentes ativos, tasks pendentes

#### 7c. Detalhe do agente -- `src/app/(dashboard)/agents/[role]/page.tsx`
- Tabs: Visao Geral | Tarefas | Atividade | Configuracoes
- Visao Geral: medidor de orcamento, schedule do pulse, timeline de atividade recente
- Tarefas: lista filtravel de tasks criadas/atribuidas
- Atividade: log scrollavel com badges por tipo de acao
- Configuracoes: orcamento, intervalo de pulse, ativar/desativar

#### 7d. Hooks -- `src/hooks/useAgents.ts`
- useAgentProfiles(), useAgentProfile(role), useUpdateAgentProfile(role)
- useAgentTasks(filters), useAgentActivity(filters), useAgentStats()

#### 7e. API client -- `src/lib/agents-api.ts`
- Wrappers tipados usando apiFetch() para todos os endpoints

---

## Fase 2+ (pos-MVP)

### 2a. Aprovacoes humanas
- Modelo `AgentApprovalRequest`: task_id, requested_by_role, status (pending/approved/rejected), reviewed_by FK users.id
- Tasks critical ou acima de threshold de tokens geram approval automatico
- Notificacao ao OWNER/ADMIN via NotificationService
- Endpoints: GET /agents/approvals, PATCH /agents/approvals/{id}
- Badge de aprovacoes pendentes na sidebar

### 2b. Rotinas recorrentes
- Modelo `AgentRoutine`: company_id, agent_role, cron_expression, task_template (JSONB), is_active
- Scheduler gera AgentTask a partir do template quando next_run_at <= now()
- Exemplo: "CFO analise semanal toda segunda 9h"

### 2c. Delegacao entre agentes
- Campo `delegation_chain` JSONB no AgentTask
- PulseEngine: se insight fora do dominio, agente indica qual deve investigar
- Cria task atribuida ao agente correto

### 2d. Hierarquia de goals
- Modelos AgentGoal + AgentProject
- Tasks referenciam project -> goal
- Rastreabilidade "por que este agente fez isto?"

### 2e. Org chart visual
- Componente frontend com Orchestrator no topo, C-levels abaixo
- Indicadores de status ao vivo, consumo de tokens
- Linhas de delegacao ativa

---

## Sequencia de implementacao (Fase 1)

Trabalho paralelizavel em 3 streams:

**Stream A (Backend Models + Migration):**
1. Criar agent_profile.py, agent_task.py, agent_activity_log.py
2. Atualizar __init__.py
3. Criar migration 031

**Stream B (Backend Services + API):**
4. Criar agent_profile_service.py
5. Criar agent_task_service.py
6. Criar schemas/agents.py
7. Criar routes/agents.py
8. Registrar router em main.py

**Stream C (Integracoes):**
9. Modificar pulse_engine.py (budget check + activity log)
10. Modificar scheduler.py (monthly reset + heartbeat update)
11. Modificar auth.py (seed profiles no registro)
12. Modificar vigilant_worker.py (activity log)

**Stream D (Frontend) -- apos A+B:**
13. Sidebar nav entry
14. hooks/useAgents.ts + lib/agents-api.ts
15. Pagina /agents (grid de cards)
16. Pagina /agents/[role] (detalhe com tabs)

**Validacao final:**
17. ruff check em todos os arquivos modificados
18. pytest tests/ (sem regressoes)
19. Verificar import chain completo
20. Testar endpoints com curl
21. Verificar frontend no browser (dev server)

---

## Arquivos criticos

| Arquivo | Acao |
|---------|------|
| `backend/app/db/models/agent_profile.py` | CRIAR |
| `backend/app/db/models/agent_task.py` | CRIAR |
| `backend/app/db/models/agent_activity_log.py` | CRIAR |
| `backend/app/db/models/__init__.py` | EDITAR (imports) |
| `backend/alembic/versions/031_*.py` | CRIAR |
| `backend/app/services/agent_profile_service.py` | CRIAR |
| `backend/app/services/agent_task_service.py` | CRIAR |
| `backend/app/schemas/agents.py` | CRIAR |
| `backend/app/api/routes/agents.py` | CRIAR |
| `backend/app/api/main.py` | EDITAR (router) |
| `backend/app/core/pulse_engine.py` | EDITAR (budget + activity) |
| `backend/app/api/routes/scheduler.py` | EDITAR (monthly reset) |
| `backend/app/api/routes/auth.py` | EDITAR (seed profiles) |
| `backend/app/workers/vigilant_worker.py` | EDITAR (activity log) |
| `src/components/dashboard/sidebar.tsx` | EDITAR (nav entry) |
| `src/hooks/useAgents.ts` | CRIAR |
| `src/lib/agents-api.ts` | CRIAR |
| `src/app/(dashboard)/agents/page.tsx` | CRIAR |
| `src/app/(dashboard)/agents/[role]/page.tsx` | CRIAR |

## Padroes a reutilizar

| Padrao | Onde existe | Reutilizar em |
|--------|-------------|--------------|
| BaseModel (UUID + timestamps) | `backend/app/db/base.py` | Todos os 3 modelos novos |
| CurrentActiveUser dependency | `backend/app/security/auth.py` | routes/agents.py |
| apiFetch() | `src/lib/api.ts` | agents-api.ts |
| useUnreadInsightCount pattern | `src/hooks/useInsights.ts` | useAgents.ts (refetchInterval) |
| Sidebar NAV array + badge | `src/components/dashboard/sidebar.tsx:28-38, 146-150` | Nav entry de Agents |
| Pydantic from_attributes | `backend/app/schemas/*.py` | schemas/agents.py |
