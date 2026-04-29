# my-claude

Setup público e sanitizado de um Claude Code completo: agents, skills, hooks, MCP servers, comandos e metodologia de trabalho (handoff, sem emojis, segurança OWASP, deploy workflow, bootstrap de projetos).

## Quick start (recomendado): deixa o Claude Code instalar pra você

1. Clone o repo:

```bash
git clone https://github.com/henriquescastilho/my-claude.git ~/my-claude
cd ~/my-claude
```

2. Abre o Claude Code dentro dessa pasta:

```bash
claude
```

3. Cola o prompt abaixo. O Claude faz o resto.

### Prompt de setup

````
Você está dentro do repo `my-claude`. Faça o setup completo no meu sistema seguindo estes passos, em ordem, parando se algum passo falhar:

1. Backup
   - Se `~/.claude/settings.json` existir, copia para `~/.claude/settings.json.bak-$(date +%Y%m%d-%H%M%S)`.
   - Se `~/.claude.json` existir, copia para `~/.claude.json.bak-$(date +%Y%m%d-%H%M%S)`.

2. Rodar o instalador
   - Executa `./scripts/install.sh`. Isso faz rsync de `.claude/`, `.codex/`, `.claude-mem-hybrid/` para o `$HOME` com exclusões de cache/state.

3. MCPs
   - Lê `.claude/mcp-servers.template.json`.
   - Para cada server, pergunta se quero ativar. Se sim, adiciona em `~/.claude.json` no campo `mcpServers`.
   - Para cada `${VAR}` placeholder em env, pergunta o valor (sem ecoar) ou deixa vazio se eu não tiver a chave ainda.

4. Plugins
   - Abre `.claude/settings.json` e lê `enabledPlugins`.
   - Lista os plugins (context7, commit-commands, claude-md-management, pyright-lsp, typescript-lsp, skill-creator, playwright) e me diz para rodar `/plugin` dentro do Claude pra instalar cada um. Esse passo precisa ser interativo dentro do Claude, não pode ser via shell.

5. Personalização
   - Abre `~/.claude/CLAUDE.md`.
   - Substitui "Henrique Castilho" pelo meu nome (pergunta).
   - Substitui "DME Technology" pelo nome da minha empresa/operação (pergunta, opcional).
   - Mantém o resto da metodologia intacta (regras de ouro, roteamento de modelo, sem emojis, português correto, OWASP, handoff).

6. Métodos
   - Confirma que `~/.claude/methods/` existe com os refs: handoff, no-emoji, security, deploy, bootstrap, banner.
   - Mostra um resumo de 1 linha de cada.

7. Sub-agents
   - Lista os 7 sub-agents instalados em `~/.claude/agents/`: architect, implementer, scout, reviewer, tester, security-auditor, deployer. Mostra o modelo de cada um.

8. Memória híbrida (opcional)
   - Pergunta se quero rodar o servidor de memória com PostgreSQL + Redis.
   - Se sim, executa `cd ~/.claude-mem-hybrid && docker compose up -d` e mostra o status.

9. RTK (opcional)
   - Pergunta se quero instalar o Rust Token Killer (proxy CLI que reduz tokens em 60-90% em operações de dev). Se sim, mostra o link de instalação.

10. Validação final
    - Roda `ls ~/.claude/agents ~/.claude/skills ~/.claude/commands ~/.claude/hooks ~/.claude/methods` e confirma que tudo foi copiado.
    - Mostra um resumo do que foi instalado e o que ficou pendente.

Importante:
- Não comite nada.
- Não exponha chaves de API no terminal.
- Se algum passo falhar, mostra o erro e pergunta se continua.
- Use português correto com acentos. Sem emojis.
````

## O que tem aqui

### `.claude/`
- **`agents/`** — 7 sub-agents com roteamento por modelo (Opus/Sonnet/Haiku)
- **`skills/`** — skills custom (graphify, deslop, deploy-check, ui-ux-pro-max, mcp-builder, etc.)
- **`commands/`** — slash commands organizados (gsd, taskmaster, memory, security, workflow, cct, utility-cmds)
- **`hooks/`** — secret-scanner, dangerous-command-blocker, conventional-commits, env-blocker, gsd-statusline, etc.
- **`methods/`** — refs de metodologia (handoff, no-emoji, security OWASP, deploy, bootstrap, banner)
- **`CLAUDE.md`** + **`RTK.md`** + **`SECOND_BRAIN.md`** — método completo
- **`mcp-servers.template.json`** — MCPs sanitizados (n8n-mcp, claude-skills-mcp, mem-hybrid, magic)
- **`settings.json`** — config de hooks e plugins

### `.codex/`
- Setup do Codex CLI com prompts, skills e vendor imports

### `.claude-mem-hybrid/`
- Servidor MCP de memória persistente (PostgreSQL + Redis via docker compose)

## Filosofia (resumo do `CLAUDE.md`)

1. **Acertar de primeira** — ler todo o contexto antes de codar
2. **Nunca chutar** — se não sabe a stack, lê
3. **Validar antes de declarar pronto** — lint, type, build, testes
4. **Corrigir tudo de uma vez** — não em pingo a pingo
5. **Zero cara de IA** — UI production-grade, sem placeholder, sem "Powered by AI"
6. **Segurança é pré-requisito** — OWASP Top 10 em toda entrega
7. **Sem emojis** — em lugar nenhum (texto, commits, PR, UI, logs)
8. **Português correto** — acentos e cedilha sempre

## Install manual (alternativa ao prompt)

```bash
git clone https://github.com/henriquescastilho/my-claude.git
cd my-claude
./scripts/install.sh
```

Depois:

1. Copia `.claude/mcp-servers.template.json` → adiciona em `~/.claude.json` no campo `mcpServers`, preenche `${VARS}`.
2. No Claude Code, roda `/plugin` e instala cada plugin listado em `enabledPlugins` do `settings.json`.
3. Edita `~/.claude/CLAUDE.md` trocando o nome/empresa.
4. (Opcional) `cd ~/.claude-mem-hybrid && docker compose up -d` para o servidor de memória.

## Sanitização

- Paths absolutos `/Users/.../` → `$HOME` ou `~`
- API keys em MCPs → placeholders `${VAR}`
- Excluídos: memória pessoal, sessions, todos, telemetry, cache, secrets state, plugin caches (1.3GB)
- `.gitignore` cobre auth, history, sqlite, logs, sessions, db state

## Estrutura de pastas

```
my-claude/
├── .claude/              # config principal
│   ├── agents/           # sub-agents
│   ├── skills/           # skills custom
│   ├── commands/         # slash commands
│   ├── hooks/            # hooks PreToolUse/PostToolUse/SessionStart
│   ├── methods/          # metodologia (handoff, security, deploy, bootstrap)
│   ├── CLAUDE.md         # regras globais
│   ├── settings.json     # config de hooks e plugins
│   └── mcp-servers.template.json
├── .codex/               # setup Codex CLI
├── .claude-mem-hybrid/   # MCP memory server
├── docs/                 # notas de arquitetura
└── scripts/
    ├── install.sh        # instalador principal
    └── build_inventory.py
```
