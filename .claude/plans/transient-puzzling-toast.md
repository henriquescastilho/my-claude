# Plano: Paridade total de telas — Web × iOS × Android

## Context

O app Midas roda em 3 plataformas (Web React, iOS SwiftUI, Android Compose). O Web é a referência mais completa (48 páginas). iOS tem 28 telas. Android tem 15 telas + 3 stubs. O objetivo é que TODAS as plataformas tenham exatamente as mesmas telas e funcionalidades.

Os backends já estão 100% prontos — todos os endpoints existem. O trabalho é puramente de **UI nativa** (iOS/Android) + pequenos ajustes no web.

---

## Matriz de gaps

### Telas que faltam no iOS (7 gaps)

| # | Tela | Existe no Web | Existe no Android | Ação iOS |
|---|------|--------------|-------------------|----------|
| 1 | **Register completo** (2 steps + CPF/phone) | ✅ Register1+Register2 | ❌ Stub | RegisterView existe mas falta phone field completo |
| 2 | **Journeys / Jornada** (visual 4 fases com stats) | ✅ Journeys.tsx | ❌ | Criar `JourneysView.swift` |
| 3 | **Content pages** (Histórias, Insights, UAU, Learning, Benefícios, Ideas) | ✅ 6 páginas | ❌ | Criar `ContentListView.swift` genérico |
| 4 | **Phase Idea wizard** (5 steps) | ✅ PhaseIdea.tsx | ❌ | Criar `PhaseIdeaWizardView.swift` |
| 5 | **Oportunidades** (links externos curados) | ✅ Oportunidades.tsx | ❌ | Criar `OportunidadesView.swift` |
| 6 | **MetronEconomy** (explicação da moeda) | ✅ MetronEconomy.tsx | ❌ | Criar `MetronEconomyView.swift` |
| 7 | **Admin panel** | ✅ Admin.tsx | ❌ | Criar `AdminView.swift` (se necessário em mobile) |

### Telas que faltam no Android (20 gaps)

| # | Tela | Existe no Web | Existe no iOS | Ação Android |
|---|------|--------------|---------------|--------------|
| 1 | **Register** (form completo) | ✅ | ✅ | Implementar `RegisterScreen.kt` |
| 2 | **Forgot/Reset Password** | ✅ | ✅ | Criar `ForgotPasswordScreen.kt` |
| 3 | **Challenges** (lista + participar) | ✅ | ✅ | Criar `ChallengesScreen.kt` |
| 4 | **Leaderboard** | ✅ | ✅ | Criar `LeaderboardScreen.kt` |
| 5 | **Notification inbox** | ✅ | ✅ | Criar `InboxScreen.kt` |
| 6 | **Chat P2P** (conversas + mensagens) | ✅ | ✅ | Criar `ChatScreen.kt` + `ChatDetailScreen.kt` |
| 7 | **Mentors** | ✅ | ✅ | Criar `MentorsScreen.kt` |
| 8 | **Grants** | ✅ | ✅ | Criar `GrantsScreen.kt` |
| 9 | **Events** | ✅ | ✅ | Criar `EventsScreen.kt` |
| 10 | **Rewards** (daily bonus + streaks) | ✅ | ✅ | Criar `RewardsScreen.kt` |
| 11 | **Journeys** (jornada visual) | ✅ | ❌ (gap iOS também) | Criar `JourneysScreen.kt` |
| 12 | **Content pages** (6 tipos) | ✅ | ❌ (gap iOS também) | Criar `ContentListScreen.kt` genérico |
| 13 | **Phase Idea wizard** | ✅ | ❌ | Criar `PhaseIdeaScreen.kt` |
| 14 | **Oportunidades** | ✅ | ❌ | Criar `OpportunitiesScreen.kt` |
| 15 | **MetronEconomy** | ✅ | ❌ | Criar `MetronEconomyScreen.kt` |
| 16 | **Clone projeto** (botão no detail) | ✅ | ✅ | Adicionar botão no `ProjectDetailScreen.kt` |
| 17 | **Export PDF** | ✅ | ❌ | Não prioritário pra Android |
| 18 | **Team members** | ✅ | ❌ | Criar `TeamMembersScreen.kt` |
| 19 | **Marketplace 3ª tab** (Minhas ofertas) | ✅ | ✅ | Adicionar tab no `MarketplaceScreen.kt` |
| 20 | **Empresas/Governos** (landing + form) | ✅ | ❌ | Criar `LeadCaptureScreen.kt` |

### Ajustes no Web (3 minor)

| # | Ajuste | Ação |
|---|--------|------|
| 1 | ProtectedRoute em todas as rotas auth | Wrap rotas no App.tsx |
| 2 | Chat P2P view (web não tem UI, só backend) | Criar `/chat` page |
| 3 | Rewards view (web não tem UI, só backend) | Criar `/rewards` page |

---

## Ordem de execução (por prioridade de impacto)

### Batch 1 — Android telas core (blocker pra beta)
**8 telas essenciais que faltam pra Android funcionar como app real**

1. `RegisterScreen.kt` — form completo (nome, email, CPF, phone, senha, termos)
2. `ForgotPasswordScreen.kt` — email input + reset flow
3. `ChallengesScreen.kt` + `ChallengeDetailSheet` — lista desafios + participar
4. `LeaderboardScreen.kt` — ranking por período
5. `InboxScreen.kt` — notificações in-app
6. `RewardsScreen.kt` — daily bonus + streaks + milestones
7. `MentorsScreen.kt` — lista mentores
8. `GrantsScreen.kt` + `EventsScreen.kt` — editais + eventos

### Batch 2 — Android telas secundárias
9. `ChatScreen.kt` + `ChatDetailScreen.kt` — P2P messaging
10. `JourneysScreen.kt` — visual 4 fases
11. `ContentListScreen.kt` — genérico pra 6 tipos conteúdo
12. `OpportunitiesScreen.kt` — links curados
13. `MetronEconomyScreen.kt` — explicação moeda
14. Marketplace 3ª tab + Clone botão no detail
15. `TeamMembersScreen.kt`
16. `LeadCaptureScreen.kt` (empresas/governos)

### Batch 3 — iOS gaps
17. `JourneysView.swift` — visual jornada com stats
18. `ContentListView.swift` — genérico pra 6 tipos
19. `PhaseIdeaWizardView.swift` — wizard 5 steps
20. `OportunidadesView.swift`
21. `MetronEconomyView.swift`

### Batch 4 — Web gaps
22. `/chat` page (ConversationsPage + ChatPage)
23. `/rewards` page
24. Wrap ProtectedRoute nas rotas

### Batch 5 — Android navegação + polish
25. Adicionar todas as novas telas ao `MidasNavGraph.kt`
26. Expandir bottom nav ou drawer pra todas as telas
27. Profile menu links (mesma estrutura do iOS)
28. Android design polish (gold/navy theme parity com iOS)

---

## Arquivos críticos a modificar

### Android (criar)
- `app/src/main/java/com/midas/forge/ui/auth/RegisterScreen.kt`
- `app/src/main/java/com/midas/forge/ui/auth/ForgotPasswordScreen.kt`
- `app/src/main/java/com/midas/forge/ui/challenges/ChallengesScreen.kt`
- `app/src/main/java/com/midas/forge/ui/challenges/LeaderboardScreen.kt`
- `app/src/main/java/com/midas/forge/ui/notifications/InboxScreen.kt`
- `app/src/main/java/com/midas/forge/ui/rewards/RewardsScreen.kt`
- `app/src/main/java/com/midas/forge/ui/mentors/MentorsScreen.kt`
- `app/src/main/java/com/midas/forge/ui/grants/GrantsScreen.kt`
- `app/src/main/java/com/midas/forge/ui/events/EventsScreen.kt`
- `app/src/main/java/com/midas/forge/ui/chat/ChatScreen.kt`
- `app/src/main/java/com/midas/forge/ui/chat/ChatDetailScreen.kt`
- `app/src/main/java/com/midas/forge/ui/journeys/JourneysScreen.kt`
- `app/src/main/java/com/midas/forge/ui/content/ContentListScreen.kt`

### Android (modificar)
- `navigation/MidasNavGraph.kt` — adicionar rotas
- `navigation/Route.kt` — adicionar sealed cases
- `ui/marketplace/MarketplaceScreen.kt` — 3ª tab
- `ui/projects/ProjectDetailScreen.kt` — botão clone
- `data/api/MidasApi.kt` — endpoints novos
- `data/repository/` — repositórios novos

### iOS (criar)
- `Features/Journeys/JourneysView.swift` + ViewModel
- `Features/Content/ContentListView.swift` (genérico)
- `Features/PhaseIdea/PhaseIdeaWizardView.swift`

### iOS (modificar)
- `Navigation/ContentView.swift` — links pras novas telas

### Web (criar)
- `src/pages/Chat.tsx` (conversations + detail)
- `src/pages/Rewards.tsx`

### Web (modificar)
- `src/App.tsx` — wrap ProtectedRoute + novas rotas

---

## Padrões a reutilizar

### Android
- **ViewModel**: `@HiltViewModel` com `StateFlow`, padrão de `DashboardViewModel.kt`
- **Repository**: `@Singleton` injetado via Hilt, padrão de `AuthRepository.kt`
- **API**: endpoints em `MidasApi.kt` (Retrofit)
- **Theme**: `MidasTheme` com `MidasColors`, `midasGold`, `navyDeep`
- **Components**: `GlowCard`, `CountUpText`, `ParticleNetwork`

### iOS
- **ViewModel**: `@MainActor final class XViewModel: ObservableObject`
- **APIClient**: `APIClient.shared.get/post(endpoint:)`
- **Endpoints**: enum cases em `Endpoints.swift`
- **Design**: `GlassCard`, `MidasButton`, `.goldPrimary`, `.navyDeep`

### Web
- **Componente genérico**: `ContentListPage.tsx` já existe — reusar pra content
- **apiClient**: `apiClient.get/post(path)`
- **UI**: shadcn/ui components, Tailwind

---

## Estratégia de paralelização

- **Android Batch 1**: 4 agentes paralelos (cada um cria 2 telas)
- **Android Batch 2**: 4 agentes paralelos
- **iOS Batch 3**: 2 agentes paralelos
- **Web Batch 4**: 1 agente
- **Navegação Android Batch 5**: 1 agente final

Total estimado: ~30 arquivos novos + ~10 modificados

---

## Verificação

1. `./gradlew assembleDevDebug` — Android BUILD SUCCESSFUL
2. `xcodebuild -scheme MIDAS build` — iOS BUILD SUCCEEDED
3. `pnpm --filter @midas/web exec tsc --noEmit` — Web clean
4. Instalar nos simuladores e navegar por todas as telas
5. Login com `admin@midas.local` / `admin` nas 3 plataformas
6. Verificar cada tela nova carrega sem crash
