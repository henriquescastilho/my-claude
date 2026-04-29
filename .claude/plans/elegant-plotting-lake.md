# Plano: Modularizar CLAUDE.md em arquivos de memória

## Contexto
CLAUDE.md global (12.5k chars) é sempre carregado. Arquivos de memória são carregados sob demanda. Ao quebrar seções detalhadas em módulos de memória, o CLAUDE.md fica leve e o conteúdo continua acessível.

**Nenhum conteúdo será deletado** — tudo será preservado, apenas reorganizado.

## Como funciona

```
ANTES (tudo no CLAUDE.md = sempre carregado):
  CLAUDE.md [12.5k] ← sempre na memória

DEPOIS (modular):
  CLAUDE.md [~5k] ← regras essenciais + ponteiros
  memory/security_standards.md ← carregado quando trabalha com segurança
  memory/graphify_setup.md ← carregado quando trabalha com graphify
  memory/deploy_workflow.md ← carregado quando faz deploy
  memory/bootstrap_project.md ← carregado quando cria projeto novo
  memory/banner_startsh.md ← carregado quando cria .start.sh
  ...etc
```

## Etapa 1 — Extrair seções do CLAUDE.md para módulos de memória

### Módulo 1: `memory/ref_security_standards.md` (~2.5k)
**Extrair de CLAUDE.md linhas 76-113:**
- OWASP Top 10 completo (10 itens detalhados)
- Checklist de segurança (13 itens)
- Pentest Mindset (5 perguntas)

**Deixar no CLAUDE.md:** Uma linha: "Segurança: OWASP Top 10 obrigatório. Ver `ref_security_standards.md` para checklist completo."

### Módulo 2: `memory/ref_deploy_workflow.md` (~800)
**Extrair de CLAUDE.md linhas 196-210:**
- Regras de inferência de deploy target
- Pre-deploy checklist (7 itens)

**Deixar no CLAUDE.md:** Uma linha: "Deploy: inferir target do código. Ver `ref_deploy_workflow.md` para checklist."

### Módulo 3: `memory/ref_bootstrap_project.md` (~600)
**Extrair de CLAUDE.md linhas 136-152:**
- Bootstrap automático detalhado (CLAUDE.md local, handoff template, .gitignore)

**Deixar no CLAUDE.md:** Uma linha: "Projeto novo sem CLAUDE.md local → bootstrap automático. Ver `ref_bootstrap_project.md`."

### Módulo 4: `memory/ref_handoff_system.md` (~1k)
**Extrair de CLAUDE.md linhas 154-194:**
- Sistema de handoff completo
- Template do handoff.md
- Regras de início/fim de sessão
- mem-hybrid regras

**Deixar no CLAUDE.md:** Duas linhas: "Início de sessão: ler CLAUDE.md local + handoff.md. Fim de sessão: atualizar handoff.md. Ver `ref_handoff_system.md`."

### Módulo 5: `memory/ref_banner_startsh.md` (~800)
**Extrair de CLAUDE.md linhas 221-252:**
- Regras de banner ASCII
- Template bash
- Regras de cor ANSI

**Deixar no CLAUDE.md:** Uma linha: "Todo projeto DEVE ter .start.sh com banner ASCII. Ver `ref_banner_startsh.md`."

### Módulo 6: `memory/ref_ui_no_emoji.md` (~500)
**Extrair de CLAUDE.md linhas 10-24:**
- Lista de substituições (Lucide, dots CSS, badges)
- Exemplo CSS

**Deixar no CLAUDE.md:** Uma linha: "Zero emojis. Em UI usar Lucide/Heroicons e CSS. Ver `ref_ui_no_emoji.md`."

## Etapa 2 — Consolidar memórias graphify existentes

Fundir 3 arquivos (8.9k total) em 1 arquivo organizado:
- `graphify_memory_sync.md` (5.3k) + `graphify_lobby_setup.md` (2.4k) + `graphify_workflow.md` (1.2k)
- → `graphify_setup.md` (~3k, tudo preservado, sem duplicação)

## Etapa 3 — Atualizar MEMORY.md

Adicionar os novos módulos ao index para que Claude saiba onde buscar cada tema.

## Resultado esperado

| Componente | Antes | Depois |
|-----------|-------|--------|
| CLAUDE.md (auto-loaded) | 12.5k | ~5k |
| MEMORY.md (auto-loaded) | 607 | ~900 |
| **Total auto-loaded** | **~13.1k** | **~5.9k** |
| Memórias (sob demanda) | 19.5k | ~22k |
| **Total disponível** | ~32.6k | ~27.9k |

O conteúdo total AUMENTA levemente (ponteiros + frontmatter), mas o que é carregado automaticamente CAI de ~13k para ~6k, eliminando o problema de performance.

## Arquivos a modificar
- `$HOME/.claude/CLAUDE.md` — enxugar, adicionar ponteiros
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_security_standards.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_deploy_workflow.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_bootstrap_project.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_handoff_system.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_banner_startsh.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/ref_ui_no_emoji.md` — criar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/graphify_setup.md` — criar (consolidado)
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/graphify_memory_sync.md` — deletar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/graphify_lobby_setup.md` — deletar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/graphify_workflow.md` — deletar
- `$HOME/.claude/projects/-Users-henriquecastilho/memory/MEMORY.md` — atualizar index

## Verificação
1. `wc -c CLAUDE.md` → confirmar ~5k
2. Somar CLAUDE.md + MEMORY.md → confirmar < 7k auto-loaded
3. Verificar que cada módulo tem frontmatter correto (name, description, type: reference)
4. Ler cada módulo e confirmar que o conteúdo original está intacto
