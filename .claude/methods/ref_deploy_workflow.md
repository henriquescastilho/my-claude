---
name: Deploy Workflow DME
description: Regras de inferência de deploy target por projeto e pre-deploy checklist completo
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## Inferência de Deploy Target

Cada projeto tem seu target. Verificar no CLAUDE.md local ou inferir do código:
- `railway.json` ou `railway.toml` → Railway
- `vercel.json` ou `next.config` → Vercel
- `Dockerfile` + `cloudbuild.yaml` → GCP Cloud Run
- Na dúvida, perguntar.

## Pre-deploy Checklist

1. `git status` — nenhum arquivo uncommitted
2. Type-check passa (`tsc --noEmit` ou equivalente)
3. Lint passa (ESLint / ruff / equivalente)
4. Build passa localmente
5. Env vars conferidas para o ambiente alvo
6. Testes passam
7. Sem CVEs críticas (`npm audit` / `pip audit`)
