---
name: Sistema de Handoff DME
description: Sistema completo de handoff por projeto — template, regras de início/fim de sessão, e integração com mem-hybrid
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## Sistema de Handoff

NÃO depender de auto-memory para continuidade. Usar sistema de handoff por projeto.

### Regra: ao ENCERRAR qualquer sessão de trabalho num projeto, SEMPRE criar/atualizar o handoff

Arquivo: `.claude/handoff.md` na raiz do projeto.

Conteúdo do handoff (máximo 50 linhas, sem enrolação):
```
# Handoff — [nome do projeto]
Data: [YYYY-MM-DD HH:MM]

## O que foi feito
- [lista curta do que mudou nesta sessão]

## Estado atual
- Branch: [branch atual]
- Build: [passa/falha]
- Testes: [passam/falham/não existem]
- Deploy: [último deploy ou "não deployado"]

## Próximos passos
- [o que falta fazer, em ordem de prioridade]

## Decisões tomadas
- [decisões de arquitetura ou padrão que afetam sessões futuras]

## Bloqueios
- [o que está travando, se houver]
```

### Regra: ao INICIAR uma sessão num projeto, ler APENAS:
1. `.claude/CLAUDE.md` do projeto (se existir)
2. `.claude/handoff.md` (se existir)
3. Pronto. Isso é o contexto. Não ler mais nada até precisar.

### mem-hybrid (MCP) — usar com parcimônia
- `memory_search` SOMENTE quando precisar de contexto que não está no handoff
- `memory_store` SOMENTE para decisões que sobrevivem ao projeto (padrões cross-projeto)
- NÃO usar `memory_recent` como substituto de handoff
