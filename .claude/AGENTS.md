# Agents — DME / Henrique

Time de agentes Claude Code disponíveis. Roteamento automático por descrição.

## Quick routing

| Tarefa | Agent | Modelo |
|---|---|---|
| Buscar/explorar código | scout | Haiku |
| Implementar feature / fix bug | implementer | Sonnet |
| Arquitetura/PRD/decisão complexa de software | architect | Opus |
| **Arquitetura cloud/infra (GCP, Terraform, multi-tenant)** | **infra-architect** | **Opus** |
| Review de código | reviewer | Sonnet |
| Testes | tester | Sonnet |
| Audit de segurança | security-auditor | Sonnet |
| Pre-deploy validation | deployer | Haiku |

## Quando cada um auto-dispara

- **scout** — qualquer file search, grep, lookup de símbolos, exploração inicial
- **implementer** — "implementa X", "corrige Y", "adiciona Z" em código
- **architect** — "como deveria ser X", "design da feature Y", "decisão sobre Z" (software)
- **infra-architect** — "infra", "cloud", "GCP", "Cloud Run", "terraform", "multi-tenant", "VPC", "IAM", "deploy strategy", "cost", "scale"
- **reviewer** — após implementação, antes de commit/PR, "revisa X"
- **tester** — "gera testes", "cobertura", "fix tests"
- **security-auditor** — "audit", "segurança", após features sensíveis, antes de deploy
- **deployer** — antes de qualquer deploy, valida envs/build/testes

## Princípios DME

1. **NUNCA Opus para tarefa que Sonnet/Haiku resolve.** Custo importa.
2. **scout primeiro** quando exploração é necessária (Haiku, baixo custo).
3. **infra-architect lê tenant.yaml** antes de comandos gcloud — multi-empresa isolation crítico.
4. **reviewer + security-auditor** obrigatórios antes de PR ready em código de produção.
5. **deployer** obrigatório antes de qualquer `gcloud run deploy` ou `vercel --prod`.

## Agents customizados (DME)

- **infra-architect** (`~/.claude/agents/infra-architect.md`) — adicionado 2026-05-18. Resolve gap de design cloud específico DME (GCP-default, multi-empresa, anti-3-opções).

## Padrão para criar novos agents

Use SKILL.md pattern com `description` denso e triggers explícitos em PT+EN. Exemplo: `infra-architect.md`.
