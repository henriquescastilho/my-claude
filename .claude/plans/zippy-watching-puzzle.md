# Plano de Migracacao: Midas Startup Forge - Plataforma Nativa

## Contexto

O Midas Startup Forge e uma plataforma aceleradora de startups com 47 paginas, backend Flask (Python), e apps mobile via Capacitor (wrapper da SPA). O objetivo e reescrever para linguagens nativas em cada plataforma:
- **Web**: React + TypeScript (manter/melhorar)
- **Android**: Kotlin + Jetpack Compose (nativo real)
- **iOS**: Swift + SwiftUI (nativo real)
- **Backend**: Node.js + TypeScript (migrar de Flask)
- **Database**: PostgreSQL no Supabase (manter como esta)

Estrategia: **Big bang rewrite** com backend rodando em paralelo durante a transicao.

---

## Estrutura do Monorepo

```
midas-platform/
  pnpm-workspace.yaml
  turbo.json
  
  packages/
    api-contract/              # OpenAPI spec + tipos gerados (TS, Kotlin, Swift)
      openapi.yaml             # Fonte unica de verdade da API
      src/schemas/             # Zod schemas compartilhados
    shared-types/              # Tipos de dominio (web + backend)
  
  apps/
    backend/                   # Node.js + Fastify + Prisma
    web/                       # React SPA existente (migrada)
    android/                   # Kotlin + Jetpack Compose
    ios/                       # Swift + SwiftUI
  
  tools/
    openapi-codegen/           # Scripts de geracao de tipos
    db-seed/                   # Dados de seed
```

---

## Stack Tecnica por Plataforma

### Backend (Node.js + TypeScript)
| Componente | Tecnologia | Justificativa |
|-----------|-----------|---------------|
| Framework | **Fastify 5** | Schema-based, gera OpenAPI automaticamente, 2-3x mais rapido que Express |
| ORM | **Prisma 6** | Type-safe, `prisma db pull` para introspeccao do DB existente |
| Validacao | **Zod** | Compartilhado com frontend via `packages/api-contract` |
| Auth | `@fastify/jwt` + bcrypt | Replica o fluxo JWT atual |
| Pagamentos | `stripe` + Asaas REST | Manter os dois gateways |
| AI | `@google/generative-ai` | SDK Gemini para Node.js |
| Rate limit | `@fastify/rate-limit` | Equivalente ao Flask-Limiter |
| Testes | Vitest + Supertest | Testes de integracao com DB real |

### Android (Kotlin)
| Componente | Tecnologia |
|-----------|-----------|
| UI | Jetpack Compose |
| Arquitetura | MVVM + Clean Architecture |
| Rede | Retrofit 2 + OkHttp + kotlinx.serialization |
| DI | Hilt |
| Cache local | Room |
| Navegacao | Jetpack Navigation Compose |
| Imagens | Coil 3 |
| Pagamentos | Stripe Android SDK + Asaas (PIX QR nativo) |
| OAuth | Chrome Custom Tabs + deep links |

### iOS (Swift)
| Componente | Tecnologia |
|-----------|-----------|
| UI | SwiftUI |
| Arquitetura | MVVM + Repository Pattern |
| Rede | URLSession + async/await |
| Cache local | SwiftData |
| Auth tokens | Keychain |
| Imagens | AsyncImage / Kingfisher |
| Pagamentos | Stripe iOS SDK + Asaas (PIX QR nativo) |
| OAuth | ASWebAuthenticationSession + deep links |

### Contrato de API
- **OpenAPI 3.1** como fonte unica de verdade
- Fastify gera o spec automaticamente via `@fastify/swagger`
- Codegen: `openapi-typescript` (web), `openapi-generator kotlin` (Android), `openapi-generator swift6` (iOS)

---

## Fases de Implementacao

### Fase 0: Fundacao (Semanas 1-2)
- [ ] Criar monorepo (pnpm workspaces + Turborepo)
- [ ] Gerar Prisma schema via `prisma db pull` do Supabase existente
- [ ] Documentar API atual como OpenAPI spec (baseado nas rotas Flask)
- [ ] Setup CI/CD para todos os projetos
- [ ] Projetos Android e iOS vazios mas compilaveis

**Arquivos criticos a estudar:**
- `supabase/migrations/20250115000000_create_midas_schema.sql` (schema base)

### Fase 1: Backend Core + Auth (Semanas 3-5)
- [ ] Portar modulo auth: login email/senha, login CPF, JWT issue/refresh, `/auth/me`
- [ ] Portar OAuth (Google, Microsoft, Apple) incluindo handoff codes
- [ ] Portar middleware de roles (admin, founder, mentor)
- [ ] Portar `/api/data/*` CRUD generico (usado pesadamente pelo frontend)
- [ ] Testes de integracao contra Supabase

**Arquivos criticos a portar:**
- `backend/auth/routes.py` (1.230 linhas - modulo mais complexo)
- `backend/auth/jwt_utils.py`
- `backend/data/routes.py` (CRUD generico com filtros)

### Fase 2: Web Frontend Reconexao (Semanas 5-7)
- [ ] Apontar React SPA existente para novo backend Node.js
- [ ] Atualizar `src/services/apiClient.ts` se houver diferencas no formato
- [ ] Verificar todas as 47 paginas contra novo backend
- [ ] Remover dependencia do Capacitor (web vira web-only)

**Arquivos criticos:**
- `src/services/apiClient.ts` (contrato que o novo backend deve honrar)
- `src/hooks/useAuth.ts`

### Fase 3: Startups + AI (Semanas 7-9)
- [ ] Portar CRUD de startups (ODS, membros, custos)
- [ ] Portar servico AI fill-project (Google Gemini)
- [ ] Portar AI chat endpoint
- [ ] Portar deducao de creditos para uso de AI
- [ ] Gerar tipos para clientes mobile via OpenAPI codegen

**Arquivos criticos a portar:**
- `backend/business/routes.py` (760 linhas)
- `backend/business/ai_routes.py` (406 linhas)
- `backend/business/credits_routes.py` (186 linhas)

### Fase 4: Pagamentos + Creditos (Semanas 9-11)
- [ ] Portar Stripe checkout + webhook
- [ ] Portar Asaas (PIX, Boleto, Cartao) + webhook
- [ ] Portar sistema de creditos (saldo, transacoes, compras)
- [ ] Operacoes atomicas com `FOR UPDATE` via `prisma.$queryRaw`

**Arquivos criticos a portar:**
- `backend/business/payment_routes.py` (510 linhas - CUIDADO MAXIMO)
- `backend/business/credits_routes.py`

### Fase 5: Comunidade + Marketplace + Admin (Semanas 11-13)
- [ ] Portar community feed (posts, comentarios, votos)
- [ ] Portar marketplace de vagas
- [ ] Portar admin (convites, templates, settings, moderacao)
- [ ] Portar referrals, awards, phases
- [ ] **Marco: paridade completa com Flask. Descomissionar Flask.**

**Arquivos criticos a portar:**
- `backend/business/community_routes.py` (645 linhas - schema dinamico)
- `backend/admin/` (todos os modulos)
- `backend/business/job_routes.py` (471 linhas)

### Fase 6: App Android Nativo (Semanas 13-18)
- [ ] Setup projeto: Hilt, Retrofit, Room, Navigation
- [ ] Auth: login, registro, OAuth via Chrome Custom Tabs
- [ ] Dashboard + fases de startup
- [ ] Lista/detalhe/edicao de projetos com AI fill
- [ ] Feed da comunidade
- [ ] Wallet + pagamentos (Stripe SDK, Asaas PIX/Boleto)
- [ ] Marketplace, referrals, perfil
- [ ] **Entrega: app no Google Play Internal Track**

### Fase 7: App iOS Nativo (Semanas 13-18, PARALELO com Android)
- [ ] Setup projeto: SwiftUI, SwiftData, URLSession
- [ ] Mesma ordem de features do Android
- [ ] OAuth via ASWebAuthenticationSession
- [ ] Pagamentos via Stripe iOS SDK + Asaas
- [ ] **Entrega: app no TestFlight**

### Fase 8: Polish + Lancamento (Semanas 18-20)
- [ ] QA cross-platform
- [ ] Push notifications (FCM Android, APNs iOS)
- [ ] Deep linking universal
- [ ] Submissao App Store + Play Store
- [ ] Descomissionar wrapper Capacitor

---

## Fluxo de Autenticacao (Cross-Platform)

```
POST /auth/login        -> { accessToken, refreshToken, user }
POST /auth/login-cpf    -> { accessToken, refreshToken, user }
POST /auth/refresh      -> { accessToken }
GET  /auth/me           -> { user }
POST /auth/oauth-handoff -> { accessToken, refreshToken, user }
```

**Armazenamento de tokens:**
| Plataforma | Local |
|-----------|-------|
| Web | localStorage |
| Android | EncryptedSharedPreferences |
| iOS | Keychain |

**OAuth nativo:** App abre browser do sistema -> callback redireciona para `midas://oauth-callback?code=HANDOFF_CODE` -> app troca code por JWT via `/auth/oauth-handoff`

---

## Pagamentos Nativos

**Stripe:** Backend cria PaymentIntent, retorna `clientSecret`, SDK nativo renderiza PaymentSheet.

**Asaas (PIX):** Backend cria cobranca, retorna QR code (base64) + codigo copia-e-cola. App exibe nativamente.

**Asaas (Boleto):** Backend retorna URL do boleto. App abre no browser do sistema.

**Asaas (Cartao):** WebView minima para tokenizacao, ou preferir Stripe para cartao.

---

## Formato Padrao de Erros

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "Saldo insuficiente. Preenchimento com IA custa 20 creditos.",
    "details": null
  }
}
```

| HTTP | Significado |
|------|------------|
| 400 | Erro de validacao (Zod) |
| 401 | Token expirado/ausente |
| 403 | Sem permissao (role) |
| 404 | Recurso nao encontrado |
| 409 | Conflito (email duplicado) |
| 422 | Erro de negocio (creditos insuficientes) |
| 500 | Erro inesperado |

---

## Riscos e Mitigacoes

| Risco | Mitigacao |
|-------|----------|
| Rewrite nao atinge paridade | Flask e Node.js rodam em paralelo com mesmo DB ate Fase 5 completa |
| Webhooks de pagamento quebram | Configurar webhooks apontando para ambos backends durante transicao |
| OAuth handoff codes perdidos | Ja armazenados em DB (`oauth_handoff_codes`), ambos backends leem |
| Dev mobile demora mais que previsto | Capacitor wrapper continua como stopgap; Fases 6-7 sao paralelas |
| Prisma nao suporta SQL complexo | Usar `prisma.$queryRaw` para queries com `FOR UPDATE`, CTEs, etc. |
| Codegen OpenAPI produz codigo ruim | Avaliar na Fase 0; se necessario, escrever API layer manualmente (~15 grupos de endpoints) |

---

## Verificacao

Para validar cada fase:
1. **Backend**: Testes de integracao com Vitest + Supertest contra Supabase real
2. **Web**: Smoke test manual das 47 paginas + testes e2e com Playwright
3. **Android**: Testes instrumentados + build no CI (Codemagic)
4. **iOS**: XCTest + build no CI (Codemagic)
5. **Paridade**: Comparar respostas da API Flask vs Node.js para os mesmos requests
6. **Pagamentos**: Testar com Stripe test mode + Asaas sandbox
