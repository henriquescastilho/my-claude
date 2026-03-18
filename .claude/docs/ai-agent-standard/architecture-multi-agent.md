# Architecture: Multi-Agent

## Problema que resolve
Um único agente para tudo causa:
- confusão de contexto
- baixa qualidade em tarefas longas
- aumento de custo e retrabalho

## Topologia padrão
- `orchestrator`: recebe PRD, decompõe tarefas, define ordem e valida entregáveis.
- `backend-agent`: domínio, API, dados, testes de serviço.
- `frontend-agent`: UI, estados, acessibilidade, performance.
- `security-agent`: threat model, segredos, policy checks.
- `review-agent`: revisão cruzada, regressão, cobertura.
- `ops-agent`: CI/CD, observabilidade, deploy seguro.

## Contrato entre agentes
Cada agente deve receber:
- contexto mínimo necessário
- entrada estruturada (task_id, objetivo, critérios)
- saída obrigatória (resultado, evidência, riscos, próximos passos)

## Regras de coordenação
- Orquestrador nunca delega tarefa ambígua.
- Toda tarefa maior que 2h vira subtarefas.
- Toda entrega de agente passa por outro agente de revisão.
- Tarefas bloqueadas retornam para planejamento, não para tentativa infinita.
