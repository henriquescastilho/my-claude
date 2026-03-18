# Vibe Frontend System

## Objetivo
Construir frontend bonito e rápido com previsibilidade, reutilizando padrões reais das referências.

## Regras de ouro
- Não inventar linguagem visual sem referência explícita.
- Clonar estrutura visual primeiro, adaptar conteúdo depois.
- Motion com função (hierarquia, feedback, orientação), não enfeite.
- Entregar sempre estados: loading, vazio, erro, sucesso.
- Responsividade e acessibilidade desde o primeiro commit.

## Padrões dominantes extraídos
- Tipografia expressiva: `font-geist`, `font-jakarta`, combinações sans/mono.
- Superfícies: gradientes, `backdrop-blur`, bordas semitransparentes, shadows suaves.
- Layout: `grid` + `flex`, spacing por escala, cartões modulares.
- Interação: `hover:`, `transition-*`, `duration-*`, microfeedback em botões e cards.
- Motion: `@keyframes`, entrance motion, loop controlado, scroll/snap em experiências narrativas.

## Arquitetura de implementação (rápida)
1. `Foundation`: tokens de cor, tipografia, espaçamento, radius, shadow.
2. `Patterns`: hero, cards, list/grid, CTA, nav, form.
3. `Behaviors`: hover/focus/active, reveal, stagger, sticky/snap quando fizer sentido.
4. `States`: skeleton, empty, error boundary, success feedback.
5. `Guardrails`: contraste, teclado, `prefers-reduced-motion`.

## Checklist de qualidade por tela
- Identidade visual clara em 3 segundos.
- Hierarquia tipográfica legível sem zoom.
- CTA principal inequívoco.
- Nenhuma animação trava leitura ou interação.
- Mobile first sem quebra de layout.
- Sem assets externos quebrados offline.

## Anti-padrões
- Telas genéricas sem assinatura visual.
- Excesso de animação sem propósito.
- Misturar muitas fontes sem sistema.
- Componentes isolados sem linguagem comum.
- Ignorar estado de erro/loading.
