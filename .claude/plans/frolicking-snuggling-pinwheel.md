# Plano — Midas App: Caminho até Production-Ready (iOS + Web + Android)

## Context

Retomando o Midas App após sessão anterior que deixou iOS ~95%, Firebase dual env configurado, sistema de Desafios + Templates seedado, Metrons renomeado, e paridade ~88% com o projeto antigo. Objetivo agora: fechar 100% de paridade e chegar a **app em stores com Asaas funcionando** (iOS + Web primeiro, Android logo depois).

Este plano é denso por design — vai guiar várias sessões, então prefere clareza operacional a prosa. Ordem das waves é o **caminho feliz** do blocker mais alto (pagamento real) até polish final.

---

## Correções ao panorama (o que a memória não refletia)

Descobertas da exploração que mudam o escopo de algumas waves:

1. **Asaas JÁ ESTÁ FUNCIONAL no backend** — não é stub. `payments/routes.ts` tem `asaasFetch()`, customer search/create, payment creation (PIX/BOLETO/CREDIT_CARD), webhook handler com `creditUserAccount()` atômico via `runTransaction`. A memória dizia "só stub". **Wave 1 fica muito menor**: falta testar end-to-end, plugar UI mobile, remover Stripe.
2. **Stripe ainda está ATIVO em paralelo** — precisa ser desativado (via `system_settings.stripe_enabled=false` + remoção gradual do código).
3. **`system_settings` helpers já existem** mas inline em `payments/routes.ts` (`getSetting`, `getSettingBool`, `getSettingNumber`). Precisam virar shared em `common/settings.ts` quando notifications/email/admin também precisarem.
4. **AI `/fill-detailed-project` existe mas NÃO carrega `templates/{id}/pages`** — prompt é hardcoded genérico. Gap de Wave 2 é exatamente esse: injetar `ai_context` de cada page no system prompt. Debito de 20 metrons já funciona via `debitForAiFill()`.
5. **`sendPushToUser()` wrapper JÁ EXISTE** em `notifications/routes.ts` — resolve userId → tokens e chama `sendPushToDevice()` com `Promise.allSettled`. Só falta o core `sendPushToDevice()` sair de `console.log` e virar `getMessaging().send()`. Wave 3 é mais barata do que parecia.
6. **Android tem ~40% de scaffold, não 0%** — 9 screens com ViewModels+UI parcial (LoginScreen completa com particle background/tabs email+CPF, DashboardScreen, WalletScreen com balance card + tx history), `MidasApi` com 58 endpoints + 70+ DTOs, Hilt DI completo, Retrofit+OkHttp+interceptors, Theme Material3 com Cinzel/Inter via Google Fonts, NavGraph com 9 routes + deep-link scheme `midas://`. Muitas screens são `PlaceholderScreen`, mas a infra está pronta. **Wave 4 vira "completar screens + ligar ViewModels" em vez de "scaffold tudo"**.
7. **iOS Wallet já faz checkout end-to-end** — `WalletViewModel.createCheckout()` chama `/api/payments/create-checkout`, abre URL via `UIApplication.shared.open()`. Falta: default provider=asaas, polling de balance pós-checkout, tela de sucesso/erro.
8. **`MidasFirebaseService.onNewToken()` Android tem TODO** de POST para `/api/notifications/register-device` — só precisa ligar.

---

## Sumário executivo

Fechar paridade focando em **Wave 1 (Asaas polish + iOS/Web plug)** → **Wave 2 (AI fill detailed com pages)** → **Wave 3 (FCM real + triggers)** destrava teste de usuário real em iOS/Web. **Wave 4 (Android screens)** e **Wave 5 (Web audit)** rodam em paralelo depois. **Waves 6-8** são infra/polish pra stores.

---

## Tabela de waves

| # | Wave | Esforço | Bloqueia stores? | Depende de | Status |
|---|------|---------|------------------|------------|--------|
| 1 | **Asaas end-to-end + remover Stripe** | ~1-2 dias | 🔴 SIM | — | ✅ feito `3228280` |
| 2 | **AI Fill Detailed consumindo 18 pages** | ~0.5-1 dia | ⚠️ parcial | Wave 1 estável | ✅ feito `be41fe9` |
| 3 | **FCM push real + triggers automáticos** | ~1-1.5 dias | ⚠️ parcial | Wave 1 | ✅ feito `303213b` |
| 3.5 | **Paridade blockers com o legado** | ~7-10 dias | 🔴 SIM | Wave 3 | ⏳ em sessão nova |
| 4 | **Android nativo — completar 8 telas** | ~2-3 semanas | 🔴 SIM (p/ Android) | Wave 3.5 | pendente |
| 5 | **Web audit + paridade completa (iOS + legado)** | ~4-5 dias | 🔴 SIM (p/ Web) | Wave 3.5 | pendente |
| 6 | **Infra: smoke tests + CI + Firestore rules + Sentry** | ~2-3 dias | 🔴 SIM | — (pode paralelizar) | pendente |
| 7 | **Email transacional + password reset** | ~1-2 dias | 🔴 SIM (reset senha é blocker loja) | Wave 6 | absorvido em 3.5 |
| 8 | **Conteúdo curado + Mentorias + Calendar** | ~4-6 dias | 🟢 não | Wave 3.5 (backend base) | pendente |
| 9 | **Polish UX**: team members, export PDF, pie chart, inbox, search users, leaderboard | ~5-7 dias | 🟡 UX | Wave 4 | pendente |
| 10 | **IA avançada v1.3**: pitch deck, market research, matching de sócios, análise concorrência | ~2 semanas | 🟢 não | Wave 9 | pendente |
| 11 | **Long-tail v1.2**: LinkedIn OAuth, chat P2P, analytics | — | 🟢 não | Wave 10 | pendente |

**Caminho feliz (atualizado)**: `1 → 2 → 3` ✅ → **`3.5` (paridade blockers, sessão atual)** → `5` (Web audit completo) + `6` (smoke + CI, paralelo) → `4` (Android) → `8` (mentorias) → `9` (polish) → `10` (IA avançada) → `11` (long-tail).

Waves 5, 6 e 8 podem correr em paralelo depois da 3.5. Wave 6 não depende de nada e pode começar junto com a 3.5 se houver bandwidth.

---

## Wave 1 — Asaas end-to-end + remover Stripe

**Por que primeiro:** sem pagamento real funcionando, não dá pra testar usuário beta. Já está ~80% pronto no backend, então é o investimento com melhor ROI imediato.

### 1.1 Backend: polish Asaas + desativar Stripe

**Arquivos:**
- `apps/backend/src/modules/payments/routes.ts` — já tem Asaas funcional
- `apps/backend/src/common/settings.ts` **(criar)** — extrair `getSetting*` helpers (hoje duplicados inline em `payments/routes.ts:16-33`)
- `apps/backend/src/config/index.ts` — remover placeholders `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` do env loader

**Tasks:**
1. **Extrair helpers**: mover `getSetting/getSettingBool/getSettingNumber` pra `common/settings.ts`, re-export em `payments/routes.ts`. Notifications e admin vão reusar.
2. **Desativar Stripe via flag**: `GET /api/payments/config` já lê `stripe_enabled`. Rodar seed `system_settings` com `stripe_enabled=false`, `asaas_enabled=true`, `asaas_sandbox=true`, `credits_per_brl=10` (PRD seção 8 — corrigir default que está 100).
3. **Pacotes canônicos**: backend hoje calcula metrons por BRL dinamicamente — OK. Mas garantir que `CreditPackage.defaults` do iOS (100/500/1000/5000 metrons @ R$9,90-299,90) bate com `credits_per_brl=10`. Se não bater, ajustar `credits_per_brl` ou os valores BRL.
4. **Remover Stripe handlers** (ou deixar guarded por `stripe_enabled`): `POST /api/payments/webhook/stripe` pode continuar registrado mas retornar 503 se flag off. Código pode ficar até Wave 5 e ser deletado de vez.
5. **Logar webhook Asaas estruturado**: `app.log.info({event, paymentId, status})` em `/webhook/asaas` handler antes do `creditUserAccount()`. Hoje loga pouco — vai ser crítico pra debug em sandbox.
6. **Validar `creditUserAccount()` é idempotente**: webhook Asaas pode disparar 2x (`PAYMENT_RECEIVED` + `PAYMENT_CONFIRMED`). Checar se já existe `credit_purchases.status='completed'` antes de creditar de novo. Se não existe, adicionar check.

**Arquivos de config/seed a atualizar:**
- `tools/scripts/seed-firestore.ts` — seed `system_settings` com novos defaults
- `apps/backend/.env.example` — documentar `ASAAS_API_KEY` opcional (lido de `system_settings` preferencialmente)

### 1.2 iOS: plug Wallet ao Asaas + polling de balance

**Arquivos:**
- `apps/ios/MIDAS/Features/Wallet/WalletView.swift`
- `apps/ios/MIDAS/Features/Wallet/WalletViewModel.swift`
- `apps/ios/MIDAS/Shared/Models/Payments.swift`
- `apps/ios/MIDAS/Core/Network/Endpoints.swift` — confirmar `.createCheckout`, `.paymentsConfig`

**Tasks:**
1. **Default provider=asaas**: `CreateCheckoutRequest` hoje aceita `provider` opcional. `WalletViewModel.createCheckout()` deve enviar `provider: "asaas"` + `billing_type: "PIX"` (default) com toggle pra BOLETO/CREDIT_CARD.
2. **UI de seleção de método**: bottom sheet com 3 opções (PIX, Boleto, Cartão) antes de abrir URL. Usar `ConfirmationDialog` ou sheet custom com MetronIcon.
3. **Abrir URL**: continuar com `UIApplication.shared.open()` (ou `SFSafariViewController` pra manter dentro do app — recomendado pro fluxo de retorno). Criar `SafariView.swift` em `Shared/Components/` usando `UIViewControllerRepresentable`.
4. **Polling de balance pós-checkout**: quando user volta pro app (scene phase `.active`), se há `pendingPurchaseId` salvo no ViewModel, disparar `loadBalance()` a cada 3s por até 60s. Se balance subiu, mostrar toast "Compra confirmada! +N metrons".
5. **Tela de histórico de compras**: reusar lista de `CreditTransaction` já existente, filtrando `type == "purchase"`. Ícone dedicado (cart.fill + MetronIcon).
6. **Remover qualquer reference a Stripe no iOS**: buscar `Stripe`, `StripeConfig` em models/views — provavelmente só referências cosméticas.

### 1.3 Web: mesma plumbagem

**Arquivos:**
- `apps/web/src/pages/Wallet*` (confirmar path exato via grep)
- `apps/web/src/services/apiClient.ts` — já existe

**Tasks:**
1. Mesmo fluxo: botão "Comprar metrons" → bottom sheet (PIX/Boleto/Cartão) → `POST /api/payments/create-checkout` → `window.open(url, '_blank')` ou redirect.
2. Polling de balance via React Query `refetchInterval` quando `pendingPurchaseId` no localStorage.
3. Toast de sucesso com shadcn/ui `toast`.

### 1.4 Testes end-to-end contra Asaas sandbox

**Arquivos:**
- `apps/backend/src/__tests__/payments.test.ts` **(criar)**
- `tools/scripts/test-asaas-sandbox.sh` **(criar)** — script manual pra rodar com sandbox real

**Tasks:**
1. Unit test `creditUserAccount()` com mock Firestore — valida idempotência + `runTransaction` + transaction record.
2. Integration test do webhook com payload real do Asaas (fixture capturado da doc).
3. Script shell `test-asaas-sandbox.sh`: cria purchase, simula webhook (curl), valida saldo atualizado. Documenta como rodar.
4. Usuário configura chave sandbox real via `POST /api/admin/settings {key: "asaas_api_key", value: "aact_hmlg_..."}` (rota admin já existe).

### Critério de aceitação Wave 1

- [ ] `GET /api/payments/config` retorna `{asaas_enabled: true, stripe_enabled: false, credits_per_brl: 10}`
- [ ] `POST /api/payments/create-checkout` com `{provider: "asaas", credits_amount: 100, billing_type: "PIX"}` retorna URL Asaas válida
- [ ] Webhook `/api/payments/webhook/asaas` com payload `PAYMENT_CONFIRMED` credita exatamente 1x (idempotente)
- [ ] iOS: botão "Comprar" → sheet método → Safari → volta ao app → saldo atualiza automaticamente
- [ ] Web: mesmo fluxo
- [ ] Stripe não é mais oferecido na UI (nem mencionado)
- [ ] Teste Vitest passando pro `creditUserAccount()`
- [ ] Script sandbox documentado em `tools/scripts/test-asaas-sandbox.sh`

### Riscos Wave 1

- **Webhook token**: Asaas envia via header `asaas-access-token` string simples, sem HMAC. Backend auto-registra o primeiro token recebido. Se sandbox enviar token novo antes de produção, `system_settings.asaas_webhook_token` pode ter valor errado — documentar como resetar.
- **Polling vs push**: polling de balance é simples mas fura contexto. Alternativa: quando webhook confirma, backend envia FCM push pro user (depende de Wave 3). Por enquanto polling é suficiente.
- **SFSafariViewController e retorno**: iOS precisa de URL scheme registrado pra deep-link de volta do Asaas. Se Asaas suporta `return_url`, passar `midas://wallet/success`. Senão, polling serve.

---

## Wave 2 — AI Fill Detailed consumindo as 18 pages

**Por que agora:** feature destrava experiência "wow" do onboarding (usuário digita 3 linhas, IA preenche canvas completo). Debito de metrons incentiva compras — sinergia com Wave 1.

### Arquivos
- `apps/backend/src/modules/ai/routes.ts` — handler `/fill-detailed-project` (existe, precisa enriquecer)
- `apps/backend/src/modules/ai/prompts.ts` **(criar, opcional)** — extrair prompt builder pra testes
- `apps/ios/MIDAS/Features/Projects/CanvasSheet.swift` — adicionar botão + estado de loading
- `apps/ios/MIDAS/Features/Projects/ProjectDetailViewModel.swift` — chamada `fillDetailed()`
- `apps/ios/MIDAS/Shared/Models/AIFillResponse.swift` (confirmar path) — já pode existir

### Tasks

1. **Carregar pages no handler backend**:
   - Antes de construir system prompt, buscar `templates/{templateId}/pages` ordenadas por `sort_order`.
   - Se user passou `template_id` no body, usa esse. Senão, rodar `matchTemplate(idea)` (já existe via `/api/ai/match-template`) e usar o retorno.
2. **Montar system prompt enriquecido**: iterar as 18 pages e construir bloco:
   ```
   Você está preenchendo o canvas de uma startup. Retorne JSON estruturado com 18 campos, um para cada página do canvas.

   Fase IDEA:
   1. Problema: {pages[0].ai_context}
   2. Solução: {pages[1].ai_context}
   ...

   Fase VALIDATION: ...
   Fase TRACTION: ...
   Fase SCALE: ...

   Retorne JSON no formato: {"fields": [{"page_id": "...", "sort_order": 0, "title": "Problema", "content": "..."}, ...]}
   ```
3. **Config Gemini explícita**: `generateContent({contents, generationConfig: {temperature: 0.7, maxOutputTokens: 8000}})`. Hoje usa defaults.
4. **Retry com backoff**: wrapper `callGeminiWithRetry(fn, attempts=3, delayMs=1000)` — reusa pra outros handlers AI. Criar em `modules/ai/gemini-client.ts` **(opcional)**.
5. **Response shape estável**: `{success: true, data: {startup: {...}, suggestions: [{page_id, sort_order, title, content, flow_step}]}}`. iOS decodifica como array ordenado.
6. **Debito de 20 metrons já existe** via `debitForAiFill()` — confirmar que está na ordem certa (debita ANTES da chamada Gemini, estorna se Gemini falha? Ou debita só no sucesso? PRD não especifica — recomendar **debita após sucesso** pra evitar estornos).
7. **iOS**: botão "Preencher detalhado com IA" em `CanvasSheet.swift` no topo (ou flutuante). Loading state: cards pulsam gold (reusar `GoldShimmer`). Ao receber resposta, repopula `content` de cada page via `content: suggestion.content` e fade-in. Toast: "Canvas preenchido! -20 metrons".
8. **Confirmação antes de gastar**: alert "Esta ação custa 20 metrons. Continuar?" antes do POST.

### Critério de aceitação Wave 2

- [ ] `POST /api/ai/fill-detailed-project` com `{startup_id: "..."}` retorna 18 campos preenchidos
- [ ] System prompt inclui `ai_context` de todas as 18 pages
- [ ] Debito de 20 metrons confirmado em `credit_transactions` com `type=ai_fill`
- [ ] iOS: botão funcional em `CanvasSheet`, loading visual, cards preenchidos ao retornar
- [ ] Testado com `pedro@midas.local` contra BicicletAlimento (template Foodtech)
- [ ] Falha graciosa: se Gemini retorna lixo, fallback heurístico existente preenche placeholders

### Riscos Wave 2

- **Gemini retorna JSON quebrado**: adicionar `responseMimeType: "application/json"` no `generationConfig` + schema JSON. Se falhar, fallback heurístico.
- **Prompt longo**: 18 pages × ~200 chars = ~3600 tokens só de contexto. OK pro Gemini 3 Flash Preview.
- **Ordem das pages**: frontend espera `sort_order` exato. Backend DEVE retornar ordenado.

---

## Wave 3 — FCM push real + triggers automáticos

**Por que agora:** push é UX crítica pra retenção (aprovação de desafio, comentário recebido, compra confirmada). Backend já tem quase tudo pronto.

### 3.1 Implementar `sendPushToDevice()` real

**Arquivo:** `apps/backend/src/modules/notifications/routes.ts:9-21`

**Tasks:**
1. Substituir `console.log` por `getMessaging().send({token, notification: {title, body}, data})` de `firebase-admin/messaging`.
2. **Cleanup de tokens inválidos**: try/catch `messaging/registration-token-not-registered` e `messaging/invalid-registration-token` — deletar doc do `device_tokens` nesses casos.
3. **Logger estruturado**: `app.log.info({userId, platform, title})` em sucesso, `.warn` em falha.
4. **Rota admin de teste**: `POST /api/admin/notifications/test` (criar) body `{user_id, title, body, type}` — dispara `sendPushToUser()` com payload de teste. Guard `requireAdmin`.

### 3.2 Triggers automáticos nos 5 pontos identificados

**Arquivos com injeção:**
- `apps/backend/src/modules/challenges/routes.ts:~435` — handler `POST /participations/:partId/approve` (admin). Após commit do `runTransaction`, chamar `sendPushToUser(part.user_id, "Desafio aprovado!", "+${reward} metrons — ${challenge.title}", {type: "challenge_approved", challenge_id})`.
- `apps/backend/src/modules/marketplace/routes.ts:~332` — `POST /api/jobs/:offerId/applications/:id/accept`. Após update status, `sendPushToUser(applicant.user_id, "Você foi aceito!", "Sua candidatura para \"${listing.title}\" foi aceita", {type: "job_accepted", offer_id, application_id})`.
- `apps/backend/src/modules/marketplace/routes.ts:~368` — `POST /.../reject`. Idem com texto de rejeição.
- `apps/backend/src/modules/community/routes.ts:~228` — `POST /api/community/feed/:postId/comments`. Após criar comment, buscar post author → `sendPushToUser(post.author_id, "Novo comentário", "Alguém respondeu ao seu post", {type: "feed_comment", post_id, comment_id})`.
- `apps/backend/src/modules/community/routes.ts:~291` — `POST /api/community/feed/:postId/vote` (quando é donation). Após commit da transação, notificar comment author: "+${amount} metrons recebidos". Cuidado: `sendPushToUser` fora do `runTransaction`, depois do commit.

### 3.3 Welcome notification

**Arquivo:** `apps/backend/src/modules/notifications/routes.ts` — handler `/register-device`

Se `users/{uid}.welcome_notification_sent !== true`, envia push "Bem-vindo ao Midas App!" com `{type: "welcome"}` e seta flag.

### 3.4 iOS deep-linking

**Arquivo:** `apps/ios/MIDAS/Core/Notifications/PushNotificationManager.swift:104-114`

Substituir TODO por switch no `type` do payload:
- `challenge_approved` → navegar pra `ChallengesView` com `challenge_id`
- `job_accepted` / `job_rejected` → navegar pra Marketplace → detail
- `feed_comment` / `feed_donation` → navegar pra FeedView + scroll pro post
- `credit_purchase` → navegar pra WalletView
- `welcome` → dashboard

Usar `AppState` ou coordenador (`Navigation/ContentView.swift` tem TabView, pode expor `@Published selectedTab` + `pendingDeepLink`).

### 3.5 Shared types

**Arquivo:** `packages/shared-types/src/notifications.ts` **(criar)**

```ts
export type NotificationType =
  | 'challenge_approved' | 'challenge_rejected'
  | 'job_accepted' | 'job_rejected' | 'job_completed'
  | 'feed_comment' | 'feed_donation'
  | 'credit_purchase' | 'ai_fill_complete'
  | 'welcome' | 'system'

export interface NotificationPayload {
  title: string
  body: string
  data: { type: NotificationType; [k: string]: string }
}
```

### Critério de aceitação Wave 3

- [ ] `POST /api/admin/notifications/test` dispara push real pro device do usuário
- [ ] Aprovar desafio no admin → push aparece no simulator iOS dentro de 5s
- [ ] Aceitar candidatura marketplace → push aparece
- [ ] Comentar no post alheio → autor recebe push
- [ ] Doar metrons em comentário → autor do comentário recebe push
- [ ] Tocar push → iOS abre tela correta (deep-link funciona)
- [ ] Token inválido é removido automaticamente de `device_tokens`

### Riscos Wave 3

- **APNs certificado iOS**: pra push real em device físico precisa APNs key no Firebase Console. Simulator recebe via FCM direto. Documentar no plano de stores.
- **Payload limit FCM**: 4KB. Deep-link data deve ser pequeno (só IDs).
- **Silent push vs alert**: usar `notification` + `data` juntos pra funcionar background + foreground.

---

## Wave 3.5 — Paridade blockers com o legado

**Por que existe:** análise de gap produzida em 2026-04-11 via 2 Explore agents paralelos mostrou que o novo cobre ~85% do legado com qualidade superior, mas há **12 blockers reais** que precisam fechar antes de beta/stores. Esta wave condensa o que era originalmente parte de Waves 5/7/8 com os gaps novos encontrados.

**Fonte completa:** `memory/project_parity_gaps.md` (seção 🔴 Blockers).

### Tasks em aberto (criadas na sessão anterior, ids #25-#37)

Execute nesta ordem. Cada bloco (3.5.1-3.5.10) vira uma feature branch + PR separado pra `main` seguindo Git Flow (hook `cct-prevent-direct-push.py` bloqueia push direto).

| Task ID | Subject | Bloco |
|---|---|---|
| **#25** | Instalar Resend + templates React Email (WelcomeEmail, PasswordResetEmail, PurchaseConfirmationEmail, `common/email.ts` helper, RESEND_API_KEY no .env + system_settings) | 3.5.1 |
| **#26** | Password reset flow backend (`POST /api/auth/forgot-password` com token TTL 1h em Firestore, `POST /api/auth/reset-password` com validação + testes Vitest) | 3.5.1 |
| **#27** | Triggers de email: signup dispara WelcomeEmail, webhook Asaas dispara PurchaseConfirmationEmail (non-blocking em falha) | 3.5.1 |
| **#28** | iOS/Web "Esqueci minha senha" UI (iOS ForgotPasswordView sheet, web `/forgot-password` + `/reset-password?token=` pages) | 3.5.1 |
| **#29** | Backend `modules/mentorships/routes.ts` — `GET /mentors`, `GET /mentors/:id/slots`, `POST /mentorships`, `DELETE /:id`, `GET /mine`. Schema + testes. | 3.5.2 |
| **#30** | Backend `modules/grants/routes.ts` — `GET /grants?status&sort`, `GET /:id`, seed 5-8 editais reais BR (FINEP, BNDES, CNPq). | 3.5.3 |
| **#31** | Backend `modules/events/routes.ts` — `GET /events?from&to&type`, `GET /:id`, seed 3-5 eventos. | 3.5.4 |
| **#32** | Web pages `/mentorias`, `/grants`, `/events` sair de placeholder e consumir os endpoints acima. | 3.5.2-4 |
| **#33** | Jornada visual `/journeys` (web `Journeys.tsx` + iOS `JourneyView.swift`) com 4 fases + lista startups por fase + botão avançar. | 3.5.5 |
| **#34** | Phase unlock sequencial no backend: `POST /api/phases/complete` valida fase anterior + requisitos, retorna 409 PHASE_LOCKED se bloqueado. | 3.5.6 |
| **#35** | EULA/Contract aceite obrigatório no signup — backend grava `accepted_terms_at`, web `/contract` + iOS `ContractView` sheet modal. | 3.5.7 |
| **#36** | Rate limit keyed por user_id em rotas sensíveis: `/credits/transfer` 1/5s, `/auth/login` 10/min, `/auth/forgot-password` 3/h, `/ai/fill-*` 10/min, `/payments/create-checkout` 10/min. | 3.5.8 |
| **#37** | Validar OAuth handoff end-to-end no simulator iOS (Google/Microsoft/Apple). Ajustar URL scheme Info.plist se quebrar. | 3.5.9 |

**Ordem recomendada de execução** (por dependência):
1. #25 → #26 → #27 → #28 (email inteiro numa feature branch `feat/wave-3.5-email`)
2. #29 → #30 → #31 → #32 (backend + web numa feature branch `feat/wave-3.5-content`)
3. #33 → #34 (journey + phase unlock em `feat/wave-3.5-journey`)
4. #35 (EULA em `feat/wave-3.5-eula`)
5. #36 (rate limit em `feat/wave-3.5-rate-limit`)
6. #37 (validação OAuth em `feat/wave-3.5-oauth-validation`)

Cada feature branch abre PR separado — menor risco de merge conflict e facilita review.

### 3.5.1 Email transacional (Resend) + password reset

**Arquivos a criar/editar:**
- `apps/backend/src/common/email.ts` **(criar)** — helper `sendEmail({to, subject, react})` com Resend SDK
- `apps/backend/src/emails/WelcomeEmail.tsx` **(criar)** — React Email template
- `apps/backend/src/emails/PasswordResetEmail.tsx` **(criar)**
- `apps/backend/src/emails/PurchaseConfirmationEmail.tsx` **(criar)**
- `apps/backend/src/modules/auth/routes.ts` — novos handlers `forgot-password` / `reset-password`
- `apps/backend/src/modules/notifications/routes.ts` — welcome email paralelo ao welcome push
- `apps/backend/src/modules/payments/routes.ts` — dispara purchase confirmation no webhook
- `apps/web/src/pages/ForgotPassword.tsx` **(criar)**
- `apps/web/src/pages/ResetPassword.tsx` **(criar)** — consome `?token=...`
- `apps/ios/MIDAS/Features/Auth/ForgotPasswordView.swift` **(criar)** — linkada do Login

**Tasks:**
1. Instalar Resend: `pnpm --filter @midas/backend add resend @react-email/render @react-email/components`
2. `RESEND_API_KEY` em `apps/backend/.env`
3. `email_from` + `email_from_name` em `system_settings`
4. 3 templates React Email com design Midas (gold + navy)
5. Token TTL 1h no Firestore `password_reset_tokens/{token}` com `user_id + expires_at`
6. Endpoint `POST /api/auth/forgot-password { email }` — gera token, envia email, **sempre retorna 200** (evita user enumeration)
7. Endpoint `POST /api/auth/reset-password { token, new_password }` — valida TTL, atualiza `password_hash`, deleta token
8. Gatilhos:
   - `signup` → welcome email
   - Webhook Asaas `creditUserAccount` → purchase confirmation email
9. iOS/Web linkam "Esqueci minha senha" do Login

**Critério de aceitação:**
- [ ] Signup → email chega na inbox (Resend dashboard em dev)
- [ ] Forgot password → email com link funcional
- [ ] Link abre `/reset-password?token=...`, form submete, login com nova senha funciona
- [ ] Webhook Asaas dispara purchase email
- [ ] iOS/Web têm fluxo completo

**Risco:** domínio `midasapp.com.br` (ou similar) precisa ser verificado no Resend (SPF/DKIM) pra envio em prod. Dev pode usar domínio sandbox do Resend.

### 3.5.2 Mentorships backend + página web

**Arquivos:**
- `apps/backend/src/modules/mentorships/routes.ts` **(criar)**
- `apps/backend/src/app.ts` — registrar `/api/mentorships` + `/api/mentors`
- `apps/web/src/pages/Mentorias.tsx` — sair de placeholder

**Schema Firestore `mentorships/{id}`:**
```
{
  mentor_id, user_id, startup_id?, status,
  scheduled_at, duration_minutes, meet_link?, notes?,
  created_at, updated_at
}
```

**Tasks:**
1. Handler `GET /api/mentors` — lista `users` com `role=mentor`
2. Handler `GET /api/mentors/:id/slots?from=YYYY-MM-DD&to=YYYY-MM-DD` — retorna slots livres dos próximos 14 dias (placeholder: array de horários)
3. Handler `POST /api/mentorships` `{ mentor_id, slot_iso, notes? }` — cria doc status=`scheduled`, **sem** Google Calendar ainda
4. Handler `DELETE /api/mentorships/:id` — cancela, status=`cancelled`
5. Handler `GET /api/mentorships/mine` — histórico do user
6. Web: tela lista mentores com cards → detail com slots → confirmar → histórico
7. Trigger push `mentorship_confirmed` (adicionar ao enum) + email via 3.5.1

**Critério de aceitação:**
- [ ] User agenda mentoria → doc criado → push + email chegam
- [ ] Lista de próximas mentorias aparece no Dashboard
- [ ] Cancelar funciona

**Nota:** Google Calendar fica em Wave 8 (evolução). Esta wave cria só o backend + UI mínima.

### 3.5.3 Grants backend + página web

**Arquivos:**
- `apps/backend/src/modules/grants/routes.ts` **(criar)**
- `apps/web/src/pages/Grants.tsx`
- `tools/scripts/seed-firestore.ts` — seed de 5-8 grants curados (editais reais do Brasil)

**Tasks:**
1. `GET /api/grants?status=active&sort=deadline` — filtros status, deadline range, valor min/max
2. `GET /api/grants/:id` — detalhe
3. Seed de 5-8 editais (FINEP, BNDES, CNPq, startups.gov.br, etc)
4. Web tela com filter chips + cards de edital (título, valor, prazo, link externo)
5. Admin pode editar via `admin/routes.ts` CRUD genérico

**Critério de aceitação:**
- [ ] `/api/grants?status=active` retorna seed
- [ ] Web tela mostra cards com filtros
- [ ] Tap no card abre URL externa do edital

### 3.5.4 Events backend + página web

Mesmo padrão de 3.5.3 mas com `events/{id}` (título, data, local, tipo, descrição). Seed 3-5 eventos fictícios.

### 3.5.5 Jornada visual (Journeys)

**Arquivos:**
- `apps/web/src/pages/Journeys.tsx` — sair de placeholder
- `apps/ios/MIDAS/Features/Journey/JourneyView.swift` **(criar)**
- `apps/ios/MIDAS/Navigation/ContentView.swift` — Journey pode virar card destacado no Dashboard

**Tasks:**
1. Visualização das 4 fases com progress bar (completed/unlocked/locked)
2. Lista de startups do user agrupadas por fase
3. Botão "Avançar fase" chama `POST /api/phases/complete` (quando requisitos atendidos)
4. Requisitos por fase (implícitos, documentar no UI):
   - **Ideia → MVP**: ter pelo menos 1 startup criada com canvas preenchido
   - **MVP → Tração**: ter candidatado/criado oferta no marketplace
   - **Tração → Escala**: ter concluído 1 desafio

**Critério de aceitação:**
- [ ] `/journeys` mostra visualização dinâmica
- [ ] iOS tem View equivalente no Dashboard ou tab dedicada
- [ ] Unlock sequencial funciona (próxima fase só depois da anterior)

### 3.5.6 Phase unlock sequencial no backend

**Arquivo:** `apps/backend/src/modules/startups/routes.ts` handler `POST /api/phases/complete`

**Tasks:**
1. Ler `phases_progress` do user
2. Se tentar completar fase N+1 com N ainda não completa → 409 `PHASE_LOCKED`
3. Validar requisitos (ver 3.5.5) antes de marcar completed
4. Atualizar `users/{uid}.current_phase`

### 3.5.7 EULA / Contract aceite explícito

**Arquivos:**
- `apps/backend/src/modules/auth/routes.ts` — signup grava `accepted_terms_at` no user doc
- `apps/web/src/pages/Contract.tsx` — página já existe, confirmar que é obrigatória antes do signup
- `apps/ios/MIDAS/Features/Auth/ContractView.swift` **(criar)** — sheet modal no fluxo de signup
- `apps/ios/MIDAS/Features/Auth/RegisterView.swift` — adicionar checkbox obrigatório

**Tasks:**
1. Textos do EULA em `/apps/web/public/eula.txt` (ou inline constants)
2. Checkbox "Li e aceito os Termos" obrigatório antes de submit
3. Backend valida `accepted_terms` no signup (400 se false)
4. `users/{uid}.accepted_terms_at = Timestamp.now()` no create

### 3.5.8 Rate limit transfer metrons + outras rotas sensíveis

**Arquivo:** `apps/backend/src/app.ts` ou módulos específicos

**Tasks:**
1. `@fastify/rate-limit` já instalado — configurar keyed por `request.user?.id` (não só IP)
2. Rotas sensíveis com limites específicos:
   - `/api/credits/transfer` → 1 req / 5s / user
   - `/api/auth/login` → 10 req / min / IP
   - `/api/auth/forgot-password` → 3 req / hora / email
   - `/api/ai/fill-project` + `/fill-detailed-project` → 10 req / min / user
   - `/api/payments/create-checkout` → 10 req / min / user

### 3.5.9 Validação end-to-end OAuth handoff mobile

**Arquivo:** `apps/ios/MIDAS/Core/Auth/OAuthHandler.swift`

**Tasks:**
1. Testar fluxo Google OAuth no simulator: tap "Entrar com Google" → SafariView → provider → callback → handoff_code → `/api/auth/oauth-handoff` → JWT → login
2. Validar Microsoft e Apple idem
3. Se falhar, ajustar deep-link URL scheme no `Info.plist` e o redirect do backend

**Critério de aceitação:**
- [ ] OAuth Google funciona end-to-end no simulator com user real
- [ ] Microsoft + Apple idem

### 3.5.10 Confirmar Wave 1 filter `.purchase` na Wallet iOS

Revisão visual do histórico de transações no iOS — só confirmar que transações `type=purchase` aparecem distintas (ícone cart ou badge "COMPRA").

### Critério de aceitação Wave 3.5

- [ ] Email (Resend) enviando welcome + reset + purchase
- [ ] Password reset funcional web + iOS
- [ ] `/api/mentorships`, `/api/grants`, `/api/events` respondendo
- [ ] 4 páginas web saem de placeholder: `/mentorias`, `/grants`, `/events`, `/journeys`
- [ ] iOS Journey visualização implementada
- [ ] Phase unlock sequencial valida requisitos no backend
- [ ] EULA checkbox obrigatório, gravado no user doc
- [ ] Rate limit ativo nas 5 rotas sensíveis
- [ ] OAuth handoff validado end-to-end no simulator
- [ ] Wallet iOS confirma filtro `.purchase`
- [ ] Backend tsc clean + 50+ vitest passando
- [ ] iOS xcodebuild BUILD SUCCEEDED
- [ ] Web tsc clean

### Riscos Wave 3.5

- **Domínio Resend** não verificado em dev — usar domínio sandbox do Resend até ter domínio real
- **Google Calendar** ausente nesta wave — mentorias só criam doc, sem evento calendar (Wave 8)
- **Grants/Events** dependem de conteúdo curado — seed com dados fictícios é aceitável pra MVP
- **Phase unlock requisitos** são "implícitos" no legado — documentar no UI pra não surpreender user

---

## Wave 4 — Android nativo: completar 8 telas

**Por que depois de 1-3:** Android precisa do checkout flow (Wave 1) e triggers de push (Wave 3) prontos pra ter experiência real. Infra já está pronta, então escopo é "completar UIs + ligar ViewModels".

### Correção crítica ao escopo original

A memória dizia "0% das telas". Exploração mostrou:
- **LoginScreen** ✅ completa (particle background, tabs email+CPF, error snackbar)
- **DashboardScreen** ✅ existe mas com stubs
- **WalletScreen** ⚠️ skeleton (balance card + tx list, falta package cards + buy flow)
- **ProjectList/Detail, Feed, Marketplace, Profile, AIChat, Referrals, Awards** ⚠️ são `PlaceholderScreen` ou shells de ~50 linhas
- **Infra 100% pronta**: Hilt, Retrofit (58 endpoints + DTOs), Room, TokenManager, NavGraph (9 routes + deep-link `midas://`), Firebase SDK, Theme Material3 com Cinzel/Inter, ParticleNetwork + GoldShimmer + CountUpText já portados
- **`MidasFirebaseService.onNewToken()` TEM TODO** de registrar token no backend — precisa ligar

Então Wave 4 é **"completar telas existentes + polish Wallet"**, não "scaffold tudo".

### Ordem de implementação (por impacto)

**Arquivos em `apps/android/app/src/main/java/com/midas/forge/`:**

1. **ui/notifications/MidasFirebaseService.kt** — remover TODO da linha ~55, registrar FCM token: `apiService.registerDevice(RegisterDeviceRequest(token, "android"))`. Usar Hilt `@AndroidEntryPoint` pra injetar `MidasApi`.
2. **ui/dashboard/DashboardScreen.kt + DashboardViewModel.kt** — completar UI com timeline da jornada (reusar `AnimatedPhaseIndicator` pattern), MetronIcon no saldo (criar `MetronIcon.kt` composable), headline "Qual ideia vamos transformar em ouro hoje?", quick actions (Projetos, Desafios, Feed, Marketplace).
3. **ui/common/MetronIcon.kt (criar)** — Canvas composable: disco com `Brush.radialGradient` gold, letra "M" Cinzel Bold preta no centro. Estilos `.Filled` e `.Outline`.
4. **ui/wallet/WalletScreen.kt + WalletViewModel.kt** — completar: adicionar cards de pacotes (LazyRow horizontal), botão "Comprar metrons" → ModalBottomSheet com escolha PIX/Boleto/Cartão → `buyCredits(packageId, billingType)` → `Intent(ACTION_VIEW, url)`. Polling de balance via `repeat(20) { delay(3000); loadBalance() }` quando volta do browser.
5. **ui/challenges/** **(criar)** — `ChallengesScreen.kt` + `ChallengesViewModel.kt`. Nova tab na bottom nav (substituir Marketplace como no iOS). Lista de desafios com categorias (chip row), tap → detail sheet com botão "Participar". Endpoint `GET /api/challenges` já está em `MidasApi`.
6. **ui/projects/ProjectListScreen.kt** — completar: LazyColumn de startups com card visual, FAB "Novo projeto", pull-to-refresh via `SwipeRefresh`, empty state ("Nenhum projeto ainda"), error retry.
7. **ui/projects/ProjectDetailScreen.kt** — completar: tabs (Informações, Canvas, Custos), seção Canvas lista as 18 pages via `GET /api/templates/{id}/pages` (adicionar ao `MidasApi`), botão "Preencher com IA" (Wave 2 endpoint).
8. **ui/community/FeedScreen.kt** — LazyColumn de posts, compose post bottom sheet, vote/donate actions (slider de metrons), infinite scroll.
9. **ui/marketplace/MarketplaceScreen.kt** — lista de jobs em grid 2 colunas, filter chips, tap → detail → botão "Candidatar-se".
10. **ui/profile/ProfileScreen.kt** — header avatar + nome + role, seções (Dados, Wallet, Prêmios, Indicações, Configurações, Sair). Wallet/Prêmios/Indicações navegam pra suas screens.
11. **ui/referrals/** e **ui/awards/** — completar: código de indicação com botão copiar, share intent. Grid de awards com ícones, modal de envio.
12. **ui/aichat/AIChatScreen.kt** — chat bubble UI (LazyColumn com reverso), TextField fixo no bottom, `/api/ai/chat` integrado.
13. **navigation/MidasNavGraph.kt** — garantir que todas as rotas passam args corretos, deep-link por `midas://` de push notifications.
14. **ui/common/NotificationHelper.kt** — parse `message.data["type"]` e criar `PendingIntent` com deep-link para rota correta.

### Tarefa por tela (padrão)

Cada tela precisa de:
- Scaffold com MidasTopBar, MidasButton, loading/error/empty states
- ViewModel com `StateFlow<UiState>` (Loading/Success/Error), `load()` + `refresh()`
- Pull-to-refresh via `PullToRefreshContainer` (Compose 1.3+)
- Empty state visual com ilustração
- Error state com retry
- Snackbar pra feedback de ações

### Critério de aceitação Wave 4

- [ ] Login → Dashboard → navegação completa funciona
- [ ] Todas as 9 rotas do NavGraph têm UI real
- [ ] Wallet: comprar metrons → PIX → volta → saldo atualiza
- [ ] Desafios: listar, participar, submeter evidência
- [ ] Feed: ler, comentar, votar, doar metrons
- [ ] FCM: receber push → tocar → abrir tela correta
- [ ] MetronIcon aparece em todos os lugares que mostram saldo
- [ ] Compose previews funcionando pra catch de regressão visual

### Riscos Wave 4

- **Package legado `com.midas.forge`**: NÃO renomear. 60+ arquivos afetados, armadilha conhecida. Pra stores, display name vira "MIDAS APP" via `app_name` em strings.xml mas package fica.
- **Cinzel via Google Fonts Compose**: já configurado em `Type.kt`, mas requer Google Play Services. Em dispositivos sem Play Services, fallback pra serif default.
- **FCM push em device físico**: precisa build assinado + APNs equivalente (Google Services). Pra testar em emulator, FCM funciona direto.
- **Checkout externo + retorno**: Android usa `Intent(ACTION_VIEW)`. Quando user volta via back button, `onResume()` do Activity dispara — ViewModel pode checar balance.

---

## Wave 5 — Web audit + paridade completa (iOS + legado)

**Por que depois de 3.5:** Web hoje tem 48 páginas mas **18 são placeholder**. Além de trazer features iOS (Desafios, CanvasSheet, Metrons), precisa fechar gap com o legado — o novo perdeu páginas que existiam: Historias, Insights, UAU, Learning Mood, Beneficios, Ideas, phase-idea wizard, journeys visual (já coberto em 3.5), etc.

### 5.1 Paridade visual com iOS

1. **Smoke tour Playwright**: `apps/web/tests/smoke.spec.ts` loga como `pedro@midas.local`, navega por todas as rotas, valida status 200 + ausência de crashes.
2. **Diff com iOS**: rodar `pnpm dev:web`, comparar com screenshots iOS:
   - Dashboard: headline "Qual ideia vamos transformar em ouro hoje?", MetronIcon, timeline única
   - Projetos: CanvasSheet detalhado (agrupado em 4 flow_steps)
   - Tab **Desafios** nova (rota `/desafios`)
   - Wallet: fluxo Asaas da Wave 1 com seleção PIX/Boleto/Cartão
3. **`apps/web/src/components/MetronIcon.tsx` (criar)** — SVG com gradient gold + letra M serif (Cinzel via CSS).
4. **`apps/web/src/pages/Challenges.tsx` (criar)** — equivalente do iOS.
5. **Ortografia PT-BR** — grep `Ideacao`, `Tracao`, `Premios`, `Usuario`, `Notificacoes`, trocar pelos com acento.
6. **Textos "créditos" → "metrons"** em toda UI visível.

### 5.2 Páginas placeholder do novo saem de placeholder (paridade legado)

Implementar (ou converter pra static content dignos) as páginas abaixo:

| Página | Origem | Abordagem |
|---|---|---|
| `/phase-idea` | legado | Wizard multi-step de ideação (usa `/api/ai/fill-project` com prompt especial) |
| `/historias` | legado | Curado — 6-10 cases fictícios com foto/logo/storyboard |
| `/insights` | legado | Biblioteca de artigos (seed Firestore `insights/{id}` + rota data) |
| `/uau` | legado | Traction milestones celebrados (seed) |
| `/learning-mood` | legado | Seletor de humor/mood + recomendação de conteúdo (pode começar simples) |
| `/beneficios` | legado | Landing estática descrevendo benefícios do programa |
| `/ideas` | legado | Tab no Feed filtrado por `intention=StartupHelp` + submissão |
| `/metron-economy` | legado | Landing educativa sobre Metrons (estática) |
| `/about` | legado | Already landing, só revisar conteúdo |
| `/privacy` | legado | Já existe no novo |
| `/midas-empresas` | legado | Landing institucional (Wave 11 pode expandir) |
| `/midas-governos` | legado | Landing institucional (Wave 11 pode expandir) |

### 5.3 Componentes e fluxos adicionais

1. **Feed intenção enum** — filtro + badge visual (5 intenções: Amizades, Investidores, Sócios, Relax, StartupHelp)
2. **Search users** — `GET /api/users/search?q=` para send award + referrals invite
3. **Paginação consistente**: Wallet, Feed, Projects com `useInfiniteQuery` React Query
4. **Notification inbox** in-app (lista de pushes recebidos, lidos/não-lidos)
5. **Error boundary global** + logging pro Sentry (integra na Wave 6)
6. **LGPD banner + privacy page** com link visível no footer

### Critério de aceitação Wave 5

- [ ] Playwright smoke passa em TODAS as 48 rotas (nenhum 5xx, nenhum crash)
- [ ] Todas as 12 páginas placeholder saem de placeholder (mesmo que content static)
- [ ] MetronIcon renderizado em saldo, dashboard, cards, sheets
- [ ] Ortografia PT-BR validada por grep
- [ ] Fluxo Asaas ponta a ponta no web
- [ ] Feed com filter de intenção funcional
- [ ] Search users usado em awards e referrals

### Riscos Wave 5

- **Conteúdo curado** — historias/insights/uau/learning dependem de texto/imagem que o user precisa fornecer ou aceitar fictício
- **Bundle size** — Cinzel via Google Fonts CSS (não npm), preload no head
- **React Query cache stale** — invalidar balance após webhook callback

---

## Wave 6 — Infra: smoke tests + CI + Firestore rules + Sentry

**Por que:** evitar regressões silenciosas. Pode começar já em paralelo com qualquer wave.

### Tasks

1. **Script `tools/scripts/smoke-test.sh`** **(criar)** — roda após `pnpm dev:local`, bate em ~30 endpoints críticos com token admin (login, balance, feed, projects, challenges, templates, marketplace, awards, referrals, admin/*), valida status 2xx + shape básica do JSON. Usa `curl` + `jq`.
2. **GitHub Actions** `.github/workflows/ci.yml` **(criar)** — no PR:
   - `pnpm install`
   - `pnpm typecheck`
   - `pnpm --filter @midas/backend test`
   - Subir Firebase Emulators em background, rodar seed, rodar smoke-test.sh
3. **Firestore rules** `firestore.rules` **(criar)** — guards por role/ownership:
   - `users/{uid}`: read se authenticated, write só próprio
   - `startups/{id}`: read/write só owner
   - `credits/{uid}`: read só próprio, write só backend (Admin SDK bypassa)
   - `credit_transactions`: read só próprio, write só backend
   - `feed/{postId}`: read auth, write owner ou admin
   - `challenges/{id}`: read all, write só admin
   - `system_settings`: read/write só admin
4. **Rate limiting revisão**: `@fastify/rate-limit` já instalado. Garantir que rotas sensíveis (login, signup, AI, payments) têm limites por IP + por user. `payments/create-checkout` → 10/min por user.
5. **Logger estruturado**: pino já configurado, mas uniformizar formato em todos os módulos. Criar `common/logger.ts` helper.
6. **Error boundary Web**: React Error Boundary global com fallback.
7. **Sentry integration** — backend (`@sentry/node`) + web (`@sentry/react`) + iOS (`Sentry-SwiftUI`). DSN via env. Capturar exceptions + breadcrumbs + user context.
8. **Uptime checker** — configurar Uptime Robot ou equivalente no backend `/health` + web.
9. **Firestore rules teste** — `firebase emulators:exec` rodando rules test suite.

### Critério de aceitação Wave 6

- [ ] `bash tools/scripts/smoke-test.sh` rodando após `pnpm dev:local` passa em todos os endpoints
- [ ] CI no GitHub Actions executa em cada PR e falha se smoke test quebra
- [ ] `firestore.rules` deployado em dev, testado via Rules Playground
- [ ] Rate limiting ativo em rotas sensíveis

### Riscos Wave 6

- **Firestore emulator no CI**: precisa Java 17+, docker opcional. Usar `firebase-tools` + setup-java action.
- **Rules muito restritivas**: podem quebrar admin panel. Testar manualmente após deploy.

---

## Wave 7 — [absorvida em Wave 3.5]

Conteúdo original (email + password reset) foi totalmente absorvido pela Wave 3.5 porque reset de senha é blocker pra publicação em stores (Apple e Google exigem um caminho de recuperação de conta). Esta numeração é mantida pra referência histórica — pular direto pra Wave 8.

---

## Wave 8 — Conteúdo curado + Mentorias + Google Calendar

**Por que depois da 3.5:** a Wave 3.5 criou os backends mínimos de mentorships/grants/events (CRUD básico, sem integrações externas). A Wave 8 evolui esses módulos com calendar + conteúdo rico + fluxos end-to-end.

### 8.1 Google Calendar integration (mentorships evolução)

1. **OAuth Google Calendar scope**: adicionar `https://www.googleapis.com/auth/calendar.events` no fluxo OAuth Google (user autoriza quando vira mentor)
2. **`modules/integrations/googleCalendar.ts` (criar)** — helper que cria/atualiza/deleta eventos via Google API client
3. **Handler `POST /api/mentorships`** (evolução): após criar o doc Firestore, chama Google Calendar pra criar evento no calendar do **mentor** (que precisa ter autorizado OAuth calendar), retorna `meet_link`
4. **Webhook Google Calendar** (opcional) — sync de cancelamentos externos
5. **Refresh token storage** — `users/{uid}.google_calendar_refresh_token` (criptografado? ou confia no Google)
6. Email `MentorshipScheduledEmail.tsx` (reusa Wave 3.5) com meet link

### 8.2 Mentor profile + disponibilidade

1. **Role `mentor`** disponível no signup via invitation code especial (`admin_grants_mentor_role`)
2. **Página "Seja Mentor"** com form de aplicação
3. **`mentor_profiles/{uid}`** — bio, áreas de expertise, duração slot padrão (30/45/60 min), horários de trabalho (dia da semana + janela)
4. **Slots disponíveis** calculados on-the-fly considerando: horário base - mentorships já agendadas
5. **Tela mentor** no admin pra gerenciar próprios slots e mentorias marcadas

### 8.3 Grants / Events evolução

1. **Grants scraper** (opcional) — cron mensal que busca editais novos de fontes curadas (FINEP, BNDES, CNPq) — background worker
2. **Events Google Calendar embed** — integração opcional pra calendar público do ecossistema
3. **Notificação de novos grants** — push + email quando grant novo aparece por área de interesse do user

### Critério de aceitação Wave 8

- [ ] User agenda mentoria → evento aparece no Google Calendar do mentor (com Meet link)
- [ ] Cancelar mentoria remove evento
- [ ] Mentor pode gerenciar próprios slots
- [ ] Grants com filtros avançados (área, valor, deadline)
- [ ] Events com embed Calendar público
- [ ] Notificações de novos grants funcionam

### Riscos

- **OAuth scope verification**: Google exige review pra scopes sensíveis (calendar.events). Pode atrasar prod release.
- **Service account vs user OAuth**: pra criar eventos no calendar do mentor, precisa OAuth do mentor (refresh token persistente).
- **Rate limit Google Calendar API**: 1M requests/day free tier, OK.

---

## Wave 9 — Polish UX: team members, PDF, gráficos, inbox

**Por que depois da 4:** a maioria destas features depende do Android estar pronto pra garantir consistência 3-plataforma.

### 9.1 Team members em startups

1. **`startups/{id}/team_members`** subcoleção — user_id, role (cofounder/dev/design/mentor), status (pending/accepted/rejected), invited_at
2. Handler `POST /api/startups/:id/team-members` — admin do startup convida por email
3. Email de convite com link `https://midasapp.com.br/team-invite?token=...`
4. Handler `POST /api/startups/:id/team-members/:memberId/accept` / `reject`
5. iOS/Web: seção "Time" no ProjectDetail com lista + botão convidar

### 9.2 Export PDF projeto

1. **Backend**: `GET /api/startups/:id/export.pdf` — render PDF server-side com PDFKit ou Puppeteer
2. **Alternativa cliente**: jsPDF (web) + PDFKit (iOS)
3. PDF contém: canvas 18 pages, custos, stats, ODS
4. Botão "Exportar PDF" no ProjectDetail

### 9.3 Pie chart de custos

1. **Web**: Recharts `PieChart` no ProjectDetail mostrando custos agrupados por categoria
2. **iOS**: Swift Charts `SectorMark`
3. **Android**: Jetpack Compose `PieChart` (ou Canvas custom)

### 9.4 Notification inbox in-app

1. **Backend**: `notifications/{id}` com `user_id, title, body, type, read, created_at`
2. Quando `sendPushToUser` dispara, também grava doc em `notifications/`
3. Handler `GET /api/notifications` — lista últimas 50, ordenado por `created_at DESC`
4. Handler `PATCH /api/notifications/:id/read` — marca como lido
5. iOS/Web/Android: tela "Notificações" no Perfil com badge de não-lidos na tab bar

### 9.5 Search users

1. Handler `GET /api/users/search?q=` — busca por email, full_name, cpf (só admin), retorna até 20 results
2. Usado em: send award, referrals invite, team member invite

### 9.6 Leaderboard challenges

1. Handler `GET /api/challenges/:id/leaderboard` — ranking de participações aprovadas por metrons ganhos
2. View no detail de challenge

### 9.7 Admin user management

1. Sub-tab no admin: "Usuários"
2. Listar users com filtro (role, email, ativo)
3. Ações: mudar role (founder↔mentor↔admin), bloquear (flag `is_blocked`), deletar
4. Audit log em `admin_audit_log/{id}` com actor, action, target, timestamp

### 9.8 Clone projeto

1. Handler `POST /api/startups/:id/clone` — cria novo startup com mesmo canvas, ODS, mas user pode editar antes de salvar

### 9.9 `/phase-idea` wizard

1. Página multi-step no web + iOS com form guiado: problema → solução → público → canais → modelo
2. Na conclusão, cria startup via AI fill com essas entradas

### Critério de aceitação Wave 9

- [ ] Team members CRUD completo 3-plataforma
- [ ] PDF export funcional com canvas + custos
- [ ] Pie chart em 3 plataformas
- [ ] Notification inbox com badges
- [ ] Search users usado em awards/referrals/team
- [ ] Leaderboard challenges no admin + user
- [ ] Admin user management + audit log
- [ ] Clone projeto funciona
- [ ] `/phase-idea` wizard completo

---

## Wave 10 — IA avançada v1.3

**Por que no final:** são features de diferenciação que dependem de todo o resto estar estável. Todas usam Gemini 3 Flash Preview com prompts especializados + cache de respostas.

### 10.1 Pitch deck generator

1. Handler `POST /api/ai/generate-pitch-deck` — recebe startup_id, monta prompt com canvas + startup data
2. Gemini retorna estrutura de slides (title, bullets, speaker_notes) em JSON
3. Backend renderiza PDF via Puppeteer ou similar
4. Custo: 50 metrons
5. UI iOS/Web: botão no ProjectDetail "Gerar Pitch Deck com IA"

### 10.2 Market research automatizado

1. Handler `POST /api/ai/market-research` — startup_id + área de interesse
2. Prompt Gemini solicita: tamanho de mercado (TAM/SAM/SOM), concorrentes top, tendências, riscos
3. Retorna relatório JSON com seções
4. Custo: 30 metrons

### 10.3 Matching de sócios

1. Handler `POST /api/ai/match-cofounders` — análise de perfil do user + startup + retorna 5 sugestões de sócios ideais entre users do Midas
2. Algoritmo: embedding de skills/área/fase + similarity search (Firestore não tem vector search nativo — usar Pinecone ou seed manual)
3. UI: tela "Encontrar sócios" com cards

### 10.4 Análise de concorrência

1. Handler `POST /api/ai/competitor-analysis` — startup_id
2. Gemini busca (via grounding) concorrentes conhecidos, matriz SWOT, diferenciadores
3. Custo: 25 metrons
4. UI: seção no ProjectDetail

### Critério de aceitação Wave 10

- [ ] 4 features IA retornando output estruturado usable
- [ ] Metrons debitados corretamente em cada
- [ ] Fallback heurístico quando Gemini falha
- [ ] UI consistente 3-plataforma

### Riscos

- **Gemini cost** em produção — cache agressivo de respostas por hash do input
- **Matching sócios** depende de base de users grande (não funciona com 10 users seed)
- **Pinecone ou vector search** adiciona custo de infra
- **Grounding** pra competitor analysis pode trazer info desatualizada

---

## Wave 11 — Long-tail v1.2: LinkedIn, chat P2P, analytics, programas institucionais

### 11.1 LinkedIn OAuth

1. LinkedIn Developer App + OAuth 2.0 flow
2. Auto-preencher perfil do user com bio, foto, empresas, educação
3. Tela Profile com toggle "Conectar LinkedIn"

### 11.2 Chat P2P (Firestore real-time listeners)

1. `chats/{chatId}` + `chats/{chatId}/messages/{messageId}` com real-time listener iOS/Android/web
2. Cada user vê lista de conversas ativas
3. Push notification on new message (integra Wave 3)
4. Typing indicator, read receipts (opcional)
5. Integra com team_members, marketplace applications, mentorships

### 11.3 Analytics (Mixpanel / PostHog)

1. Eventos estruturados: login, signup, project_created, ai_fill, checkout, push_tap, etc.
2. User properties: role, current_phase, metrons_total
3. Funnel analysis via dashboard Mixpanel
4. Frontend tracker em web + iOS + Android

### 11.4 `/empresas` — programa intraempreendedorismo

1. Landing institucional com caso de uso corporate
2. CTA: agendar demo (cria lead em `sales_leads/`)
3. (v2.0) dashboard customizado pra empresa contratante com métricas dos próprios colaboradores

### 11.5 `/governos` — programa governo

1. Similar a `/empresas` mas orientado a secretarias/ministérios
2. Dashboard com métricas agregadas por região/setor

### 11.6 Export CSV admin

1. Handler `GET /api/admin/export/:resource.csv` — users, startups, transactions, etc.
2. Stream CSV direto pro browser
3. Usado pra relatórios e compliance

### 11.7 Reward system automático

1. Daily login: +5 metrons (1x/dia)
2. First project created: +50 metrons
3. Streak 7 dias consecutivos: +100 metrons
4. Cron ou trigger baseado em login timestamp

### Critério de aceitação Wave 11

- [ ] LinkedIn OAuth funcional
- [ ] Chat P2P MVP (listas + mensagens + push)
- [ ] Mixpanel tracker capturando 10+ eventos key
- [ ] /empresas + /governos landing pages
- [ ] Export CSV funcional no admin
- [ ] Reward automático via cron

---

## Fora de escopo / escopo v2

Coisas que NÃO entram neste plano:

- **Videoconferência integrada** — usar Google Meet/Jitsi externo
- **White-label corporate SaaS** — requer contratos, billing complexo, SLA enterprise
- **Mobile push APNs em device real** — requer conta Apple Developer $99/ano + APNs key
- **Full-text search com relevance ranking** — adicionar Algolia se precisar
- **Chat em grupo (mais de 2 users)**
- **Integração ERPs** (SAP, TOTVS)
- **Marketplace de serviços pagos externos** (advocacia, contabilidade, etc)

Documentar em `docs/ROADMAP-v3.md` **(criar)** quando fechar Wave 11.

---

## Caminho feliz sequencial (atualizado pós-gap-analysis)

1. **Waves 1-3** ✅ feitas (commits `3228280`, `be41fe9`, `303213b`)
2. **Wave 3.5** (7-10 dias) — **ATIVA** — email, mentorships/grants/events backend, páginas web saindo de placeholder, EULA, rate limit, OAuth mobile validation
3. **Wave 5** (4-5 dias, pode correr em paralelo com 6) — web audit completo + 12 páginas placeholder finalizadas
4. **Wave 6** (2-3 dias, paralelo livre) — smoke tests, CI, Firestore rules, Sentry
5. **Wave 4** (2-3 semanas) — Android nativo
6. **Wave 8** (4-6 dias) — Google Calendar evolução de mentorships + grants scraper
7. **Wave 9** (5-7 dias) — polish UX (team, PDF, gráficos, inbox, search)
8. **Wave 10** (~2 semanas) — IA avançada v1.3
9. **Wave 11** (escopo extenso) — LinkedIn, chat P2P, analytics, programas institucionais

**Total até iOS+Web beta em stores**: ~3-4 semanas (3.5 + 5 + 6 em paralelo)
**Total até Android em stores**: +3-4 semanas (Wave 4)
**Total até v1.2 completo**: +2-3 meses (Waves 8-11)

---

## Arquivos críticos (referência rápida)

### Backend
- `apps/backend/src/modules/payments/routes.ts` — Asaas funcional (Wave 1)
- `apps/backend/src/modules/ai/routes.ts:124-142` — `_fillDetailedProjectFallback` (Wave 2)
- `apps/backend/src/modules/notifications/routes.ts:9-43` — `sendPushToDevice` + `sendPushToUser` (Wave 3)
- `apps/backend/src/modules/challenges/routes.ts:~435` — inject push trigger
- `apps/backend/src/modules/marketplace/routes.ts:332, 368` — inject push triggers
- `apps/backend/src/modules/community/routes.ts:228, 291` — inject push triggers
- `apps/backend/src/common/errors/index.ts` — AppError subclasses (reusar)
- `apps/backend/src/__tests__/helpers.ts` — test fixtures (expandir)
- `tools/scripts/seed-firestore.ts` — system_settings seed (Wave 1)

### iOS
- `apps/ios/MIDAS/Features/Wallet/WalletView.swift` + `WalletViewModel.swift` (Wave 1)
- `apps/ios/MIDAS/Features/Projects/CanvasSheet.swift` (Wave 2)
- `apps/ios/MIDAS/Core/Notifications/PushNotificationManager.swift:104-114` — TODO deep-link (Wave 3)
- `apps/ios/MIDAS/Shared/Models/Payments.swift:40-53` — `CreditPackage.defaults`
- `apps/ios/MIDAS/Shared/Components/MetronIcon.swift` — já existe, reusar
- `apps/ios/MIDAS/Core/Network/APIClient.swift` — `APIListResponse<T>` / `APIObjectResponse<T>` / custom date decoder (reusar)

### Android
- `apps/android/app/src/main/java/com/midas/forge/ui/notifications/MidasFirebaseService.kt:55` — TODO registrar token
- `apps/android/app/src/main/java/com/midas/forge/data/api/MidasApi.kt` — 58 endpoints (reusar, expandir)
- `apps/android/app/src/main/java/com/midas/forge/ui/theme/{Color,Type,Theme}.kt` — Material3 Galaxy x Greece pronto (reusar)
- `apps/android/app/src/main/java/com/midas/forge/ui/common/` — MidasButton, MidasCard, LoadingIndicator (reusar)
- `apps/android/app/src/main/java/com/midas/forge/navigation/MidasNavGraph.kt` — NavHost + deep-link `midas://`

### Web
- `apps/web/src/pages/Wallet*.tsx` (Wave 1)
- `apps/web/src/services/apiClient.ts` — token refresh on 401 (reusar)
- `apps/web/tailwind.config.ts` — design tokens (reusar)

---

## Verificação end-to-end (como testar o plano em cada wave)

### Wave 1
```bash
# Setup
pnpm dev:local                                    # sobe emulators + backend + web
pnpm emulators:seed                               # popula users + system_settings

# Configurar chave sandbox Asaas
curl -X POST http://localhost:3000/api/admin/settings \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"key":"asaas_api_key","value":"aact_hmlg_xxx"}'

# Validar config
curl http://localhost:3000/api/payments/config | jq

# Criar checkout
curl -X POST http://localhost:3000/api/payments/create-checkout \
  -H "Authorization: Bearer <pedro_token>" \
  -d '{"provider":"asaas","credits_amount":100,"billing_type":"PIX"}' | jq

# iOS: abrir simulator, login pedro@midas.local / midas123, Wallet, comprar
# Web: http://localhost:9080, login pedro, Wallet, comprar
# Simular webhook sandbox manualmente (script tools/scripts/test-asaas-sandbox.sh)
```

### Wave 2
```bash
# iOS: login pedro, abrir BicicletAlimento, CanvasSheet, "Preencher com IA"
# Validar saldo decrescido de 20 metrons
# Validar 18 campos preenchidos nas pages
```

### Wave 3
```bash
# Rota admin de teste
curl -X POST http://localhost:3000/api/admin/notifications/test \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"user_id":"pedro_id","title":"Teste","body":"Hello","type":"system"}'

# Validar no simulator iOS se push aparece
# Aprovar desafio no admin → push chega
# Doar em comentário → autor recebe push
```

### Wave 4
```bash
cd apps/android && ./gradlew :app:installDevDebug
# Open emulator, run, login flow completo
# Validar todas as 9 rotas
```

### Wave 5
```bash
pnpm --filter web test:smoke  # playwright
```

### Wave 6
```bash
bash tools/scripts/smoke-test.sh
# Push branch → GitHub Actions verde
```

### Wave 7
```bash
# Forgot password
curl -X POST http://localhost:3000/api/auth/forgot-password \
  -d '{"email":"pedro@midas.local"}'
# Validar email chega (Resend dashboard ou log)
```

### Wave 8
```bash
# Agendar mentoria no web
# Validar evento no Google Calendar do mentor
```

---

## Restrições que vou respeitar (não-negociáveis)

Da memória `feedback_platform_conventions.md`:

1. ✅ **Metrons** em toda UI, nunca "créditos". Código técnico mantém `credits`.
2. ✅ **Sem scroll em login/register**. Novas telas seguem o mesmo padrão.
3. ✅ **MetronIcon** em todo lugar que mostra saldo. Criar equivalente Android (Wave 4) e Web (Wave 5).
4. ✅ **Ortografia PT-BR com acentos**. Grep em Wave 5 pra pegar legados.
5. ✅ **5 tabs iOS**: Dashboard · Projetos · Desafios · Comunidade · Perfil. Marketplace é Quick Action.
6. ✅ **Backend wrapped vs plain**: novos endpoints emitem `{success, data}`. Existentes não renomeados.
7. ✅ **Datas ISO com fracional seconds** — iOS custom decoder já trata.
8. ✅ **`runTransaction` pra todo debito/credito de metrons** — Wave 2/3 seguem.
9. ✅ **`requireAdmin` guard** nas novas rotas admin (notification/test, settings)
10. ✅ **Asaas é o ÚNICO gateway** — Stripe desativado em Wave 1
11. ✅ **Android package `com.midas.forge`** — NÃO renomear
12. ✅ **iOS Keychain fallback UserDefaults** — manter, não configurar signing real pra dev
13. ✅ **Respostas curtas pro usuário** — sem preamble

---

## Perguntas abertas (confirmar com usuário antes de executar)

- **Wave 1**: a taxa `credits_per_brl` deve ser **10** (PRD) ou **100** (default atual do backend)? Pacotes iOS hardcoded em `CreditPackage.defaults` precisam bater.
- **Wave 2**: debitar 20 metrons **antes** ou **depois** da chamada Gemini? (Recomendação: depois, pra evitar estornos em falha.)
- **Wave 4**: Android Wallet com Chrome Custom Tabs (CCT) ou `Intent(ACTION_VIEW)` simples? CCT dá melhor UX mas adiciona dep `androidx.browser`.
- **Wave 7**: Resend ou Postmark? (Recomendação: Resend pelo template system React.)
- **Wave 6 CI**: GitHub Actions ou Codemagic (já usado pra mobile)? Recomendação: GitHub Actions pra backend/web, Codemagic só mobile.
