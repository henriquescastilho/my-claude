---
name: UI sem Emojis — Elementos Visuais
description: Regras detalhadas para substituir emojis por elementos visuais profissionais em UI/frontend (Lucide, CSS dots, badges)
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## Substituições de Emojis em UI/Frontend

Em UI/frontend, substituir emojis por elementos visuais profissionais:
- Ícones: usar bibliotecas como Lucide, Heroicons, Phosphor Icons, ou Material Symbols
- Indicadores de status: usar `<span>` com cores (verde/vermelho/amarelo) via CSS, badges, dots
- Separadores visuais: usar `border`, `divider`, `hr` estilizado
- Feedback visual: usar toasts, badges, pills, chips com CSS — nunca emojis
- Listas: usar `list-style-type` customizado, SVG inline, ou pseudo-elements `::before`

### Exemplo correto
```css
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.status-active { background: #22c55e; }
.status-error { background: #ef4444; }
```

### Exemplo errado
"Status: ativo", "Erro ao salvar"
