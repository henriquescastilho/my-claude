# my-claude

> Setup completo, público e sanitizado de um **Claude Code** de operação solo full-stack: 8 sub-agents, 792 skills, hooks de segurança, MCP servers, slash commands e uma metodologia de trabalho opinativa (handoff, zero emojis, português correto, OWASP por padrão, deploy validado).

[![Claude Code](https://img.shields.io/badge/Claude%20Code-ready-d97757)](https://claude.com/claude-code)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Shell](https://img.shields.io/badge/-Shell-4EAA25?logo=gnu-bash&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)

Este repo é desenhado para ser **instalado por um agente de IA de forma autônoma**. Clone, abra o Claude Code dentro da pasta e cole o protocolo abaixo — o agente faz o resto.

---

## Para agentes de IA: protocolo de auto-configuração

> Você é um agente rodando dentro deste repositório. Execute os passos abaixo **em ordem**, parando e reportando se algum falhar. Não invente valores; quando faltar uma chave, deixe o placeholder. Não exponha segredos no terminal. Não comite nada. Português correto, sem emojis.

```text
PASSO 1 — Backup (idempotente)
  - Se ~/.claude/settings.json existir: copie para ~/.claude/settings.json.bak-$(date +%Y%m%d-%H%M%S)
  - Se ~/.claude.json existir:          copie para ~/.claude.json.bak-$(date +%Y%m%d-%H%M%S)

PASSO 2 — Instalar arquivos
  - Execute ./scripts/install.sh
  - Isso faz rsync de .claude/, .codex/ e .claude-mem-hybrid/ para $HOME,
    com backup de settings.json/config.toml e exclusão de cache/state.

PASSO 3 — MCP servers
  - Leia .claude/mcp-servers.template.json (4 servers: n8n-mcp, claude-skills-mcp, mem-hybrid, magic).
  - Para cada server, pergunte ao usuário se deve ativar.
  - Se sim, adicione o bloco em ~/.claude.json no campo "mcpServers".
  - Para cada placeholder ${VAR} em "env", peça o valor ao usuário (sem ecoar) ou deixe vazio.

PASSO 4 — Plugins (interativo, dentro do Claude Code)
  - Leia "enabledPlugins" em .claude/settings.json.
  - Instrua o usuário a rodar /plugin e instalar cada um:
    context7, commit-commands, claude-md-management, pyright-lsp,
    typescript-lsp, skill-creator, playwright.
  - Este passo NÃO pode ser feito via shell — só via /plugin no Claude.

PASSO 5 — Personalização do CLAUDE.md
  - Abra ~/.claude/CLAUDE.md.
  - Pergunte o nome do operador e substitua "Henrique Castilho".
  - Pergunte o nome da empresa/operação (opcional) e substitua "DME Technology".
  - Mantenha a metodologia intacta (regras de ouro, roteamento de modelo,
    sem emojis, português, OWASP, handoff).

PASSO 6 — Sub-agents
  - Confirme ~/.claude/agents/ com os 8 sub-agents:
    architect, infra-architect (Fable 5) | implementer, reviewer, tester,
    security-auditor (Opus 4.8) | scout, deployer (Sonnet 4.6).
  - Mostre o modelo roteado de cada um.

PASSO 7 — Memória híbrida (opcional)
  - Pergunte se deve subir o servidor de memória (PostgreSQL + Redis).
  - Se sim: cd ~/.claude-mem-hybrid && docker compose up -d ; mostre o status.

PASSO 8 — Validação final
  - Rode: ls ~/.claude/agents ~/.claude/skills ~/.claude/commands ~/.claude/hooks ~/.claude/methods
  - Resuma o que foi instalado e o que ficou pendente (chaves, plugins, memória).

Ao terminar: reporte o estado final em uma tabela curta. Não comite. Não faça deploy.
```

---

## O que tem aqui

### `.claude/` — config principal

| Diretório | Conteúdo |
|---|---|
| `agents/` | **8 sub-agents** com roteamento por modelo (Fable 5 / Opus 4.8 / Sonnet 4.6) |
| `skills/` | **792 skills** — segurança ofensiva/defensiva, forense, cloud, design, build, review, etc. |
| `commands/` | slash commands (`auto-browser`, `security/`, `utility-cmds/`) |
| `hooks/` | `cct-secret-scanner.py`, `cct-dangerous-command-blocker.py`, `block-env-commit.sh` |
| `methods/` | refs de metodologia: handoff, no-emoji, security OWASP, deploy, bootstrap, banner |
| `output-styles/` | `engineering.md`, `mentor.md` |
| `CLAUDE.md` · `RTK.md` · `SECOND_BRAIN.md` · `AGENTS.md` | método completo |
| `settings.json` | hooks (PreToolUse/PostToolUse/SessionStart) + `enabledPlugins` |
| `mcp-servers.template.json` | MCPs sanitizados com placeholders `${VAR}` |

### Roteamento de modelo (em `CLAUDE.md`)

| Tarefa | Sub-agent | Modelo |
|---|---|---|
| Buscar/explorar código | `scout` | Sonnet 4.6 |
| Implementar feature / fix | `implementer` | Opus 4.8 |
| Arquitetura / PRD / decisão | `architect` | Fable 5 |
| Infraestrutura / cloud | `infra-architect` | Fable 5 |
| Review de código | `reviewer` | Opus 4.8 |
| Testes | `tester` | Opus 4.8 |
| Audit de segurança | `security-auditor` | Opus 4.8 |
| Pre-deploy | `deployer` | Sonnet 4.6 |

### `.codex/` — setup do Codex CLI (prompts, skills, vendor imports)
### `.claude-mem-hybrid/` — MCP de memória persistente (PostgreSQL + Redis via docker compose)

---

## Setup manual (alternativa ao protocolo)

```bash
git clone https://github.com/henriquescastilho/my-claude.git ~/my-claude
cd ~/my-claude
./scripts/install.sh
```

Depois:
1. Copie os blocos de `.claude/mcp-servers.template.json` para `~/.claude.json` (`mcpServers`) e preencha os `${VAR}`.
2. No Claude Code, rode `/plugin` e instale cada plugin listado em `enabledPlugins`.
3. Edite `~/.claude/CLAUDE.md` trocando nome/empresa.
4. (Opcional) `cd ~/.claude-mem-hybrid && docker compose up -d`.

---

## Segredos e sanitização

Este repo é **público e sanitizado**. Nada pessoal é exposto:

- API keys de MCP → placeholders `${VAR}` (nunca valores reais)
- Paths absolutos `/Users/<user>/...` → `$HOME`
- Symlinks resolvidos para conteúdo real (sem vazar paths locais)
- Excluídos via `.gitignore`: auth tokens, history, sessions, sqlite/db state, logs, caches de plugin, memória pessoal, planos de trabalho

Ao instalar, **você** preenche suas próprias chaves localmente — elas nunca tocam o repo.

---

## Filosofia (resumo do `CLAUDE.md`)

1. **Acertar de primeira** — ler todo o contexto antes de codar
2. **Nunca chutar** — se não sabe a stack, lê
3. **Validar antes de declarar pronto** — lint, type, build, testes
4. **Corrigir tudo de uma vez** — não em pingo a pingo
5. **Zero cara de IA** — UI production-grade, sem placeholder, sem "Powered by AI"
6. **Segurança é pré-requisito** — OWASP Top 10 em toda entrega
7. **Sem emojis** — em lugar nenhum (texto, commits, PR, UI, logs)
8. **Português correto** — acentos e cedilha sempre

---

## Estrutura

```
my-claude/
├── .claude/
│   ├── agents/                    # 8 sub-agents (roteamento por modelo)
│   ├── skills/                    # 792 skills
│   ├── commands/                  # slash commands
│   ├── hooks/                     # secret-scanner, dangerous-command-blocker, env-blocker
│   ├── methods/                   # metodologia (handoff, security, deploy, bootstrap, banner)
│   ├── output-styles/             # engineering, mentor
│   ├── CLAUDE.md                  # regras globais + roteamento de modelo
│   ├── settings.json              # hooks + enabledPlugins
│   └── mcp-servers.template.json  # MCPs sanitizados
├── .codex/                        # setup Codex CLI
├── .claude-mem-hybrid/            # MCP memory server (Postgres + Redis)
├── docs/                          # notas de arquitetura + inventário
└── scripts/
    ├── install.sh                 # instalador (rsync + backups)
    └── build_inventory.py
```

---

## Licença

MIT. Use, adapte e republique — só não exponha as suas próprias chaves.
