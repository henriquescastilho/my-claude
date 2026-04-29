# Plano de Correção — Midas Startup Forge v1.0.3

## Contexto

Auditoria E2E revelou **31 bugs**. Este plano corrige todos em **7 agentes paralelos** (Wave 1) + 2 tarefas pós-merge (Wave 2). Nenhum agente toca arquivo de outro — zero conflitos.

## Arquitetura do Projeto (importante)

Este é um **monorepo com codebase única** que atende 3 plataformas:

| Plataforma | Como funciona | Linguagem real |
|-----------|---------------|----------------|
| **Web** | `npm run build` → `dist/` servido pelo Passenger/Apache | TypeScript/React |
| **Android** | Capacitor copia `dist/` para um WebView. `MainActivity.java` tem 5 linhas (shell vazio) | TypeScript/React (rodando em WebView) |
| **iOS** | Capacitor copia `dist/` para um WKWebView. `AppDelegate.swift` é boilerplate padrão | TypeScript/React (rodando em WKWebView) |

**Consequência prática:** Todo fix no `src/` (React/TS) corrige as 3 plataformas automaticamente. Os diretórios `android/` e `ios/` são containers nativos gerados — sem código de negócio. A única diferença cross-platform está em:
- `src/lib/oauthBridge.ts` — detecta nativo vs web para OAuth
- `src/lib/apiBaseUrl.ts` — resolve URL da API (emulador usa `10.0.2.2`, web usa `localhost`)
- `capacitor.config.ts` — splash screen e plugins nativos

**Backend:** Flask (Python) servindo API em `/api/*` — compartilhado por todas as plataformas.

---

## WAVE 1 — 7 Agentes Paralelos (worktrees isolados)

### AGENT A: `fix/header-nav-layout`
**Plataformas afetadas:** Web + Android + iOS (fix único no React)
**Arquivos:** `src/components/TopNav.tsx`, `src/components/BottomNav.tsx`

| Bug | Arquivo:Linha | Correção |
|-----|---------------|----------|
| Padding jitter ao abrir dropdown | `TopNav.tsx:69` | Mudar `7.5rem` → `7rem` no cálculo de `paddingTop` |
| max-h excessivo nos dropdowns | `TopNav.tsx:135,159,183` | Mudar `max-h-[200px]` → `max-h-20` (80px) |
| Botões overflow em phones <375px | `TopNav.tsx:93,103,114,125` | Remover `min-w-[90px]`, deixar flex distribuir naturalmente |

**Verificação:** `npm run build` + teste visual em viewport 320px (simula iPhone SE) e 390px (iPhone 14) no devtools.

---

### AGENT B: `feat/marketplace-notifications`
**Plataformas afetadas:** Todas (backend + frontend React)
**Arquivos:** NOVO `supabase/migrations/20260409100000_marketplace_notifications.sql`, `backend/business/job_routes.py`, `src/pages/Marketplace.tsx`

**1. Nova migration — tabela `midas.notifications`:**
```sql
CREATE TABLE IF NOT EXISTS midas.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES midas.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL DEFAULT 'info',
    title VARCHAR(255) NOT NULL,
    body TEXT,
    reference_type VARCHAR(50),
    reference_id UUID,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user_id ON midas.notifications(user_id);
CREATE INDEX idx_notifications_user_unread ON midas.notifications(user_id) WHERE NOT is_read;
```

**2. Backend — `job_routes.py`:**
- Dentro do `accept_application` (após linha ~313, dentro do `with db.get_cursor()` existente): INSERT notification para o candidato aceito (`type='application_accepted'`)
- No bulk reject (que já acontece dentro do accept_application): INSERT notification para cada candidato rejeitado (`type='application_rejected'`)
- NOVO endpoint `GET /jobs/my-applications`: retorna candidaturas do usuário autenticado com JOIN em `job_offers` + `users` (título da oferta, status, nome do dono, créditos)

**3. Frontend — `Marketplace.tsx`:**
- Adicionar 3ª tab "Minhas Candidaturas" ao componente `Tabs`
- Nova state `myApplications` + interface `MyApplication`
- Chamar `GET /jobs/my-applications` quando tab selecionada
- Renderizar lista com Badge colorido por status (pending=amarelo, accepted=verde, rejected=vermelho)

**Verificação:** Aplicar migration → aceitar candidatura → query `SELECT * FROM midas.notifications` → verificar row criada. Abrir Marketplace → tab "Minhas Candidaturas" → verificar que mostra candidaturas.

---

### AGENT C: `fix/ai-bias-agro`
**Plataformas afetadas:** Todas (backend compartilhado)
**Arquivo:** `backend/business/ai_routes.py`

| Bug | Linha | Correção |
|-----|-------|----------|
| Catchall especial `"agro" in r.split()` só existe para Agtech | 116 | Remover o `or (...)` e usar substring matching como todos os outros setores |

**De:**
```python
if any(p in r for p in ("agricultura", "agronegócio", "fazenda", "rural")) or ("agro" in r.split()):
```
**Para:**
```python
if any(p in r for p in ("agricultura", "agronegócio", "fazenda", "rural", "agroec", "agropec", "agrotech", "agrofloresta")):
```
Usa prefixos agro- específicos para evitar false positive com "milagro" enquanto captura compostos como "agroecologia", "agropecuária", etc. Padrão consistente com os demais setores.

**Verificação:** Testar `_infer_area_from_resumo("plataforma de agroecologia")` → "Agtech". Testar `"app de fitness"` → "Healthtech". Testar `"milagro"` → vazio (sem false positive).

---

### AGENT D: `fix/feed-community-backend`
**Plataformas afetadas:** Web + Android + iOS (frontend) + Backend
**Arquivos:** `src/pages/Feed.tsx`, `backend/business/community_routes.py`

| Bug | Arquivo:Linha | Correção |
|-----|---------------|----------|
| BottomNav duplicado | `Feed.tsx:476` | Deletar a linha 476 (segundo `<BottomNav />`) |
| Feed sem paginação | `community_routes.py:131-140` | Adicionar `LIMIT %s OFFSET %s` ao final do SQL |

**Paginação:** Na função `_posts_select_sql` adicionar `LIMIT %s OFFSET %s` ao SQL. Na função `get_feed` (~linha 235) extrair `limit` e `offset` dos query params:
```python
limit = min(int(request.args.get("limit", 30)), 100)
offset = max(int(request.args.get("offset", 0)), 0)
posts_query = _posts_select_sql(schema)
post_rows = db.execute(posts_query, (limit, offset)) or []
```

**Verificação:** `GET /api/community/feed?limit=5` retorna max 5 posts. Feed.tsx renderiza 1 único BottomNav.

---

### AGENT E: `fix/credits-atomicity`
**Plataformas afetadas:** Todas (backend compartilhado — impacto financeiro)
**Arquivo:** `backend/business/credits_routes.py`

| Bug | Linha | Correção |
|-----|-------|----------|
| Race condition no debit | 31-54 | `SELECT FOR UPDATE` dentro de único `get_cursor()` |
| Sem rate limit no transfer | 107-159 | Cooldown 5s por user + `SELECT FOR UPDATE` |

**`debit_for_ai_fill` reescrito — tudo atômico:**
```python
def debit_for_ai_fill(db, user_id: str, amount: float = 20.0) -> tuple[bool, str]:
    try:
        with db.get_cursor() as cur:
            cur.execute(
                "INSERT INTO midas.user_credits (user_id, balance) VALUES (%s, 0) ON CONFLICT (user_id) DO NOTHING",
                (user_id,),
            )
            cur.execute(
                "SELECT balance FROM midas.user_credits WHERE user_id = %s FOR UPDATE",
                (user_id,),
            )
            row = cur.fetchone()
            balance = float(row["balance"]) if row else 0.0
            if balance < amount:
                return False, f"Saldo insuficiente. Preenchimento com IA custa {int(amount)} créditos."
            cur.execute(
                "UPDATE midas.user_credits SET balance = balance - %s, updated_at = NOW() WHERE user_id = %s",
                (amount, user_id),
            )
            cur.execute(
                """INSERT INTO midas.credit_transactions (from_user_id, to_user_id, amount, type, description)
                   VALUES (%s, NULL, %s, 'ai_fill', %s)""",
                (user_id, amount, "Preenchimento de projeto com IA (Gemini)"),
            )
        return True, ""
    except Exception as e:
        return False, str(e)
```

**Transfer — cooldown + FOR UPDATE:** Adicionar `import time` + dict `_transfer_cooldowns` com check de 5s. Mover balance check para dentro do `with db.get_cursor()` com `SELECT ... FOR UPDATE`.

**Verificação:** 2 requests simultâneos de debit com saldo=20 → só 1 sucede. Transfer rápido em <5s → HTTP 429.

---

### AGENT F: `fix/dashboard-sticky-header`
**Plataformas afetadas:** Web + Android + iOS (fix único no React)
**Arquivo:** `src/pages/Dashboard.tsx`

| Bug | Linha | Correção |
|-----|-------|----------|
| Sticky header fica atrás do TopNav | 80 | Mudar `sticky top-0` → `sticky` com `style={{ top: 'calc(env(safe-area-inset-top, 0px) + 3.5rem)' }}` |
| Form de convite flash durante loading | ~87-119 | Envolver conteúdo com `{!loading && (...)}` + spinner com `Loader2` durante loading |

**Verificação:** Scroll no Dashboard → header sticky gruda abaixo do TopNav. Reload → sem flash do form.

---

### AGENT G: `fix/minor-frontend-batch`
**Plataformas afetadas:** Web + Android + iOS (fix único no React)
**Arquivos:** `src/pages/Grants.tsx`, `src/pages/Login.tsx`, `src/pages/Wallet.tsx`, `src/pages/Projects.tsx`

| Bug | Arquivo | Correção |
|-----|---------|----------|
| Links "#" nos grants | `Grants.tsx:102-107,140-145` | Botões `disabled` quando `link === "#"`, texto "Em breve" |
| OAuth navigate loop | `Login.tsx:~53` | Usar `useRef` para marcar erro já exibido, evitar re-trigger do useEffect |
| Sem validação de provider | `Wallet.tsx:~51` | Auto-selecionar primeiro provider habilitado no useEffect após carregar config |
| Sem check de créditos pré-AI | `Projects.tsx:~199` | Fetch `/credits/balance` antes do fill, toast se <20 |
| Erro genérico no AI fill | `Projects.tsx:~245` | Tratar status 402 com mensagem específica de saldo |

**Verificação:** Grants → botões disabled com "Em breve". Login com `?error=test` → toast 1 vez só. Wallet → provider auto-selecionado. Projects → toast de saldo antes de chamar IA.

---

## WAVE 2 — Pós-merge

### AGENT H: `chore/store-publishing`
**Arquivo:** `codemagic.yaml`
- Descomentar bloco Google Play (linhas 78-82)
- Adicionar `groups: [google_play_credentials]`
- Verificar config iOS TestFlight (já funcional)

### AGENT I: Teste de integração
Rodar `npm run build` no main após merge. Verificar todos os 31 fixes manualmente.

---

## Mapa de Conflitos (prova de zero-conflito)

| Agente | Branch | Arquivos Exclusivos | Conflito |
|--------|--------|---------------------|----------|
| A | fix/header-nav-layout | TopNav.tsx, BottomNav.tsx | Nenhum |
| B | feat/marketplace-notifications | NOVA migration SQL, job_routes.py, Marketplace.tsx | Nenhum |
| C | fix/ai-bias-agro | ai_routes.py | Nenhum |
| D | fix/feed-community-backend | Feed.tsx, community_routes.py | Nenhum |
| E | fix/credits-atomicity | credits_routes.py | Nenhum |
| F | fix/dashboard-sticky-header | Dashboard.tsx | Nenhum |
| G | fix/minor-frontend-batch | Grants.tsx, Login.tsx, Wallet.tsx, Projects.tsx | Nenhum |

**Merge:** Todos os 7 branches podem mergear em qualquer ordem — sem conflitos.

---

## Verificação Final (pós-merge)

```bash
# 1. Build frontend (valida compilação TS + React)
npm run build

# 2. Sync Capacitor (valida que dist/ funciona no nativo)
npx cap sync

# 3. Health check backend
curl https://midas.asegtech.com/health

# 4. Testar migration
flask migrate
```
