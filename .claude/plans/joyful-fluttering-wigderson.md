# Instalar RTK (Rust Token Killer)

## Contexto

RTK e um proxy CLI que comprime output de comandos Bash antes de chegar ao LLM, economizando 60-90% de tokens por sessao. Henrique aprovou a instalacao para otimizar o fluxo de trabalho da DME com Claude Code.

## Passos

1. **Instalar via Homebrew**
   ```bash
   brew install rtk-ai/tap/rtk
   ```

2. **Inicializar hook global no Claude Code**
   ```bash
   rtk init -g
   ```

3. **Verificar instalacao**
   ```bash
   rtk --version
   rtk status
   ```

4. **Testar com um comando simples**
   ```bash
   rtk git status
   ```

## Verificacao

- `rtk --version` retorna versao instalada
- `rtk status` mostra configuracao ativa
- Hook presente em `~/.claude/settings.json` ou equivalente
- Proxima sessao do Claude Code ja usa RTK automaticamente
