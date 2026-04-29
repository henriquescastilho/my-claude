---
name: Bootstrap Automático de Projeto
description: Procedimento para criar CLAUDE.md local, handoff.md e .gitignore ao entrar num projeto novo sem configuração
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## Bootstrap Automático

Ao entrar num projeto que NÃO tem CLAUDE.md local, Claude DEVE criar automaticamente:

1. **CLAUDE.md** na raiz do projeto com o mínimo:
   - Nome do projeto (inferir da pasta)
   - Stack detectada (ler package.json, pyproject.toml, go.mod, Cargo.toml, etc.)
   - Deploy target detectado (vercel.json → Vercel, railway.json → Railway, Dockerfile → Docker, etc.)
   - Comando de deploy (inferir ou perguntar uma vez)
   - Comando de build/dev (inferir do package.json scripts, Makefile, etc.)
   - Env vars necessárias (ler .env.example se existir)

2. **`.claude/handoff.md`** vazio com template pronto para preencher

3. **`.gitignore`** com `.env*` se não existir

O bootstrap acontece silenciosamente na primeira interação. Conforme o trabalho avança, Claude atualiza o CLAUDE.md com informações descobertas (novos comandos, decisões de arquitetura, padrões do projeto).
