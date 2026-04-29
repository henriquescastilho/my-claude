# Dashboard Redesign — Simples para "um velho"

## Contexto
O dashboard atual é confuso: hero "Painel Executivo" genérico, Timeline de Agent fake, "Envie uma NF" (Fase 2), métricas sem contexto. O usuário-alvo é um empresário mais velho que precisa de clareza: ver saldo, pagar boleto, cobrar, pagar folha. Todas as 10 páginas têm funcionalidade real — nada será deletado, features futuras ficam com badge "Em breve".

## Fluxo do usuário
```
Deposita via PIX na subconta → Upa boletos → Sistema paga em nome do CNPJ do cliente → Saldo volta a zero
```

---

## Implementação (4 etapas)

### Etapa 1: Sidebar — reorganizar menu
**Arquivo:** `frontend/src/components/ui/dashboard-with-collapsible-sidebar.tsx`

Adicionar prop `badge?: string` ao componente `Option`. Quando `badge` está definido, mostra pill dourado ("Em breve") e linka para `/em-breve?feature=X`.

Nova estrutura:
```
OPERAÇÕES
  📊 Início           → /dashboard
  📄 Pagar            → /flows          (renomear de "Pagadoria")
  📥 Cobranças        → /cobrancas
  👥 Folha            → /folha          (NOVO no sidebar)

EM BREVE
  📑 Notas Fiscais    → /em-breve?feature=notas-fiscais    [badge]
  💳 Cartão           → /em-breve?feature=cartao            [badge]
  📊 Relatórios       → /em-breve?feature=relatorios        [badge]

CONTA
  📦 Plano & Créditos → /credits
  ⚙️ Configurações    → /settings
```

Removidos do sidebar (acessíveis via URL direto): Clientes, API Keys.

### Etapa 2: Página "Em breve"
**Novo arquivo:** `frontend/src/app/(dashboard)/em-breve/page.tsx`

- Ícone de cadeado grande
- "Em desenvolvimento"
- "Esta funcionalidade estará disponível em breve."
- Botão "Voltar ao início" → `/dashboard`
- ~50 linhas, usa DashboardShell

### Etapa 3: Dashboard home — reescrever
**Arquivo:** `frontend/src/app/(dashboard)/dashboard/page.tsx`

Manter APIs existentes (`getAccountBalance`, `getCurrentUserExtended`, `listFlows`), remover todo o conteúdo visual atual e substituir por:

**Bloco 1 — Info cards (3 colunas):**
| Card | Dado | API |
|------|------|-----|
| Saldo disponível | R$ real da subconta | `getAccountBalance` |
| Chave PIX | UUID copiável | `getCurrentUserExtended.asaas_pix_key` |
| Créditos | Unidades restantes | `getDashboardMetrics` |

**Bloco 2 — Ações rápidas (4 botões grandes, 2x2 grid):**
- "Pagar boletos" → `/flows/new` (gold, primário)
- "Cobrar clientes" → `/cobrancas`
- "Pagar folha" → `/folha`
- "Ver extrato" → `/flows`

Botões grandes (h-20), ícone + label, fácil de clicar.

**Bloco 3 — Boletos pendentes:**
- Filtrar `recentFlows` por status != COMPLETED/CANCELED
- Lista com nome, valor, status badge
- Total a depositar
- CTA: "Deposite R$ X via PIX" com chave copiável

**Bloco 4 — Últimos pagamentos:**
- Lista simples dos 5 flows mais recentes
- Data, nome, valor, status badge
- Link "Ver todos" → `/flows`

**Remover:** Hero "Painel Executivo", AgentTimeline, MetricsCards (6 cards), UpcomingPayments mockado, ReportsCard.

**Preservar:** Redirect PF → `/funcionario/dashboard` (linha 91-94 atual).

### Etapa 4: Cleanup
- Verificar build
- Testar redirect PF
- Verificar que /notas-fiscais, /cartao, /api-keys ainda funcionam via URL direto

---

## Arquivos tocados

| Arquivo | Ação |
|---------|------|
| `frontend/src/components/ui/dashboard-with-collapsible-sidebar.tsx` | Editar sidebar + Option component |
| `frontend/src/app/(dashboard)/dashboard/page.tsx` | Reescrever completo |
| `frontend/src/app/(dashboard)/em-breve/page.tsx` | Criar novo |

## Arquivos NÃO tocados (referência)
- `frontend/src/lib/api.ts` — APIs já existem, sem mudança
- Todas as páginas de features (flows, cobrancas, folha, etc.) — intactas
- Backend — zero mudanças

## Verificação
1. `npm run build` passa
2. Sidebar mostra 4 itens ativos + 3 "Em breve" + 2 conta
3. Dashboard mostra saldo real, PIX copiável, créditos, 4 botões de ação
4. Clicar "Em breve" mostra página de interceptação
5. URLs diretas (/notas-fiscais, /cartao, /api-keys) ainda funcionam
6. Deploy GCP e teste visual
