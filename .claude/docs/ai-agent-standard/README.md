# AI Agent Standard

Padrão operacional para construir software com agentes de IA com velocidade, segurança e previsibilidade.

## Escopo
- Orquestração multi-agente com responsabilidades claras.
- Segurança por isolamento + privilégio mínimo.
- Loop anti-context-rot (Ralph Loop / Half Loop).
- Roteamento de modelos por tarefa e custo.
- Papel humano como gerente de arquitetura e qualidade.

## Arquivos deste padrão
- `architecture-multi-agent.md`
- `security-baseline.md`
- `ralph-loop.md`
- `model-routing-cost.md`
- `manager-playbook.md`
- `templates/*`
- `examples/*`

## Regra principal
Nenhum agente deve operar com acesso amplo sem guardrails. Todo fluxo deve ter:
1. objetivo explícito
2. escopo mínimo de permissão
3. checkpoint de validação
4. rollback claro
