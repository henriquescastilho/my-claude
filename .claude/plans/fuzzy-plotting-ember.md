# Landing Page Institucional ROW Capital — Plano de Implementação

## Contexto

A landing page atual é uma tela simples com logo, headline e CTA. O objetivo é transformá-la numa experiência institucional completa com todo o conteúdo da apresentação oficial da ROW Capital (MFO, fee-based, tributário, estudo de caso, compliance, roadmap), abertura cinematográfica do remo, animações de scroll, e CTAs intercalados que levam ao questionário de suitability.

**Resultado esperado:** Uma landing que vende a ROW Capital como parceira de patrimônio, com o remo como fio condutor visual, culminando no questionário. WhatsApp do CFO só aparece para patrimônio >= R$ 6M.

---

## Arquitetura

A `LandingPage.tsx` atual (~220 linhas) será substituída por um orquestrador que compõe ~20 sub-componentes em `src/components/landing/`. Cada seção é um componente isolado que recebe texto do i18n.

```
src/components/landing/
  CinematicIntro.tsx      — Abertura 4s (SVG stroke draw + timeline anime.js)
  LandingHeader.tsx       — Header fixo transparente→cream no scroll
  FloatingOar.tsx         — Mini-remo fixo canto inferior esquerdo
  SectionWrapper.tsx      — Container compartilhado (bg alternado, padding, useInView)
  AnimatedCounter.tsx     — Count-up numérico (anime.js + IO)
  CTARespiro.tsx          — CTA reutilizável (standard/final)
  HeroSection.tsx         — Seção 1
  MFOSection.tsx          — Seção 2
  GestoraSection.tsx      — Seção 3
  FeeBasedSection.tsx     — Seção 4
  TaxEfficiencySection.tsx — Seção 5 (tabela comparativa)
  TaxExemptSection.tsx    — Seção 6 (grid de isentos)
  ComparativesSection.tsx — Seção 7 (2 tabelas)
  CaseStudySection.tsx    — Seção 8 (números animados)
  ComplianceSection.tsx   — Seção 9
  QualificationSection.tsx — Seção 10
  BenefitsSection.tsx     — Seção 11
  RoadmapSection.tsx      — Seção 12 (timeline)
  LandingFooter.tsx       — Seção 13
```

**LandingPage.tsx** vira orquestrador:
```
CinematicIntro → (onComplete) →
  LandingHeader
  FloatingOar
  HeroSection
  MFOSection
  GestoraSection
  CTARespiro 1
  FeeBasedSection
  TaxEfficiencySection
  TaxExemptSection
  CTARespiro 2
  ComparativesSection
  CaseStudySection
  CTARespiro 3
  ComplianceSection
  QualificationSection
  BenefitsSection
  RoadmapSection
  CTARespiro Final
  LandingFooter
```

---

## Arquivos a Modificar/Criar

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `src/i18n/types.ts` | MODIFICAR | Adicionar interface `landing` com todas as seções |
| `src/i18n/pt.ts` | MODIFICAR | Adicionar traduções PT de todas as seções |
| `src/i18n/en.ts` | MODIFICAR | Adicionar traduções EN de todas as seções |
| `src/components/Logo.tsx` | MODIFICAR | Adicionar `mode="cinematic"` com SVG paths para stroke draw |
| `src/components/landing/*.tsx` | CRIAR | ~20 componentes de seção |
| `src/components/LandingPage.tsx` | REESCREVER | Orquestrador que monta todas as seções |
| `src/styles/globals.css` | MODIFICAR | Smooth scroll, estilos de seção, SVG stroke |
| `src/steps/Step03Financial.tsx` | MODIFICAR | Adicionar campo de faixa de patrimônio |
| `src/steps/Step12Confirmation.tsx` | MODIFICAR | WhatsApp condicional >= R$ 6M |
| `src/hooks/useFormState.tsx` | SEM MUDANÇA | `identification` Record já suporta campos arbitrários |

---

## Tarefas de Implementação

### Wave 1: Fundação (i18n + utilidades)

**Task 1: i18n — tipos e traduções completas**
- `src/i18n/types.ts` — Adicionar `landing` key à interface `Translations` com sub-tipos para cada seção
- `src/i18n/pt.ts` — Todo o conteúdo PT da apresentação oficial
- `src/i18n/en.ts` — Espelho EN completo
- Adicionar `identification.patrimonyValue` e `identification.patrimonyRanges` (array de faixas)

**Task 2: Componentes utilitários**
- `src/components/landing/SectionWrapper.tsx` — bg alternado (cream/white por index), padding 120px, Framer Motion `useInView` para entrance stagger, prop `id` para IO
- `src/components/landing/AnimatedCounter.tsx` — Count-up com anime.js ao entrar no viewport (IO), props: value, prefix, suffix, duration, decimals
- `src/components/landing/CTARespiro.tsx` — Variantes `standard` (fundo navy/cream) e `final` (maior, dourado). Dispara `startSession()` + `trackEvent('landing_cta_click')` + `onStart()`

### Wave 2: Logo cinematográfico + intro

**Task 3: Logo mode="cinematic"**
- `src/components/Logo.tsx` — Novo prop `mode?: 'default' | 'cinematic'`
- Mode `cinematic`: renderiza SVG com `<path>` elements (blade outline, shaft, water lines) em vez de divs CSS
- Paths com `stroke="#1B2A4A"` e `fill="none"`, prontos para `strokeDashoffset` draw
- Manter mode `default` intacto (CSS divs com clip-path)
- Exportar constantes de path data para reuso no FloatingOar

**Task 4: CinematicIntro.tsx**
- Timeline anime.js `createTimeline()`:
  - 0-1200ms: stroke draw do remo (strokeDashoffset → 0)
  - 800-1400ms: linhas d'água (scaleX 0→1, stagger)
  - 1200-2800ms: remada completa (rotate 0 → -15 → 0 → 15 → 0)
  - 1400-2400ms: ondas concêntricas (3 circles, r 0→200, opacity 0.08→0, stagger 400ms)
  - 2800-3400ms: "ROW CAPITAL" fade in
  - 3400-4000ms: tudo faz fade out
- Prop `onComplete` chamado aos 4000ms
- Overlay fixo z-50, bg-cream

**Task 5: FloatingOar.tsx**
- Fixo `bottom-6 left-6`, z-30, opacity 0.25
- SVG do remo em `sm` (~40px)
- Intersection Observer detecta mudança de seção
- No cruzamento: anime.js rotação rápida -8→8→0 (600ms)
- Idle: opacity oscila 0.2↔0.35 (anime.js loop)
- `hidden md:block` (esconde no mobile)

### Wave 3: Seções de conteúdo (paralelizável)

**Task 6: Header + Hero + Footer**
- `LandingHeader.tsx` — Fixo, transparente → `bg-cream/95 backdrop-blur` ao scrollar (scroll listener). Logo sm + LanguageToggle. z-40
- `HeroSection.tsx` — Headline Playfair Display, subtítulo gold, descrição, indicadores de confiança. Full viewport height. Mesmo texto do design aprovado
- `LandingFooter.tsx` — Fundo navy, texto cream, ROW Capital MFO, www.rowcapital.com.br, referências CVM/ANBIMA

**Task 7: Seções 2-3 (MFO + Gestora)**
- `MFOSection.tsx` — Definição MFO, Regulação CVM Res. 19, fee-based, visão holística. Layout: título à esquerda, 2-3 cards à direita. Cards entram da esquerda (framer-motion)
- `GestoraSection.tsx` — Definição Gestora, CVM Res. 21, execução imediata, acesso institucional. Cards entram da direita

**Task 8: Seções 4-6 (Fee-Based + Tributário + Isentos)**
- `FeeBasedSection.tsx` — Alinhamento, transparência, 0.5%-1.0% a.a., conflito zero. Números grandes com AnimatedCounter (>60% margem)
- `TaxEfficiencySection.tsx` — Tabela Fundo vs Carteira (come-cotas, compensação, isenção, dividendos, tributação). Coluna "Carteira" com highlight gold. Números 15% e 0% com AnimatedCounter
- `TaxExemptSection.tsx` — Grid 2x4: LCI, LCA, CRI, CRA, Debêntures, FIIs, Dividendos, Fiagro. Ícones abstratos em navy, hover gold

**Task 9: Seções 7-8 (Comparativos + Estudo de Caso)**
- `ComparativesSection.tsx` — 2 tabelas lado a lado (desktop), empilhadas (mobile). Fundo vs Carteira + Assessoria vs Gestão. Coluna ROW com highlight gold
- `CaseStudySection.tsx` — "Família X": R$ 50M patrimônio, economia R$ 450k/ano, +0.8% a.a., 125% CDI. Números gigantes com AnimatedCounter. Layout tipo dashboard card

**Task 10: Seções 9-12 (Compliance + Qualificação + Benefícios + Roadmap)**
- `ComplianceSection.tsx` — CVM, ANBIMA, VaR, stress test, PLD/CFT, Suitability. Grid de badges/selos navy com borda
- `QualificationSection.tsx` — CGA, CGE, CEA, CFP (badges), experiência, educação continuada. Layout limpo
- `BenefitsSection.tsx` — Duas colunas: Ganhos Estratégicos (receita, fidelização, escala) + Benefícios para Investidores (personalização, transparência, performance). Cards
- `RoadmapSection.tsx` — 4 etapas: Estruturação → Onboarding → Consolidação → Expansão. Timeline horizontal (desktop) / vertical (mobile). Nós conectados por linha. Stagger entrance

### Wave 4: Montagem + WhatsApp condicional

**Task 11: Reescrever LandingPage.tsx**
- Orquestrador que compõe CinematicIntro + Header + FloatingOar + todas as seções + CTAs + Footer
- Passa `onStart` para Hero e CTAs
- `trackEvent('page_view', { page: 'landing' })` no mount
- Sem texto inline — tudo via `t.landing.*`

**Task 12: Campo de patrimônio + WhatsApp condicional**
- `src/i18n/pt.ts` e `en.ts` — Adicionar `identification.patrimonyValue` label e `identification.patrimonyRanges` (faixas: "Até R$ 1M", "R$ 1M - R$ 3M", "R$ 3M - R$ 6M", "R$ 6M - R$ 10M", "R$ 10M - R$ 30M", "R$ 30M - R$ 50M", "Acima de R$ 50M")
- `src/steps/Step03Financial.tsx` — Adicionar SelectInput de faixa de patrimônio antes das perguntas Q1-Q3. Salvar o valor mínimo da faixa em `setIdentification('patrimonyValue', minValue)`
- `src/steps/Step12Confirmation.tsx` — WhatsApp CTA condicional: `parseInt(state.identification.patrimonyValue || '0') >= 6000000`. Se menor, mostrar mensagem alternativa ("Entraremos em contato por e-mail")

### Wave 5: Estilos + Analytics + Polish

**Task 13: Estilos globais**
- `src/styles/globals.css` — `html { scroll-behavior: smooth }`, estilos de tabela com highlight gold, font-variant-numeric: tabular-nums para contadores, SVG stroke styles

**Task 14: Analytics de landing**
- Nos CTARespiro: `trackEvent('landing_cta_click', { cta: 'respiro_1' | 'respiro_2' | 'respiro_3' | 'final' })`
- No `SectionWrapper`: `trackEvent('landing_section_view', { section: id })` via IO
- No scroll: `trackEvent('landing_scroll_depth', { depth: 25|50|75|100 })` em thresholds

**Task 15: Testes e deploy**
- `npm run build` — 0 erros
- Testar no browser: intro → scroll completo → CTA → questionário → WhatsApp condicional
- Testar bilíngue (toggle PT/EN em qualquer ponto)
- Testar mobile (responsividade de todas as seções)
- Deploy: `vercel deploy --prod`

---

## Detalhes de Animação

### CinematicIntro Timeline (anime.js createTimeline)

```
0ms          1200ms        2800ms        3400ms   4000ms
|-- draw ---|-- rowing ---|-- text --|-- fade --|
     |-- water (800-1400) --|
          |-- waves (1400-2400) --|
```

### Scroll Animations (Framer Motion useInView)

Cada seção entra com:
```ts
const variants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.32, 0.72, 0, 1], staggerChildren: 0.08 } }
}
```

### AnimatedCounter (anime.js + IO)

```ts
// Quando entra no viewport:
animate(counterRef, {
  innerHTML: [0, targetValue],
  round: decimals === 0 ? 1 : Math.pow(10, decimals),
  duration: 1200,
  ease: 'easeOutExpo',
})
```

### FloatingOar Micro-Row

```ts
// No cruzamento de seção:
animate(oarRef, {
  rotate: [0, -8, 8, 0],
  duration: 600,
  ease: 'easeInOutSine',
})
```

---

## Verificação

1. `npm run build` — 0 erros TypeScript
2. Abrir `http://localhost:5175` — intro cinematográfico roda, landing completa aparece
3. Scroll — seções entram com animação, números fazem count-up, remo flutuante reage
4. Toggle PT/EN — todo o conteúdo troca, sem strings inline
5. Clicar qualquer CTA — transição para o questionário, analytics disparam
6. Preencher questionário com patrimônio < R$ 6M — WhatsApp NÃO aparece
7. Preencher questionário com patrimônio >= R$ 6M — WhatsApp APARECE
8. Admin panel — novos eventos de landing aparecem nos gráficos
9. Mobile (375px) — todas as seções responsivas, FloatingOar escondido
10. `vercel deploy --prod` — site no ar em row-capital.vercel.app
