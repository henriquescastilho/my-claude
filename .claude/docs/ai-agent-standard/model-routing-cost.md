# Model Routing and Cost Policy

## Princípio
Custo total = tokens + retrabalho + tempo humano.
Modelos melhores costumam reduzir custo final em tarefas críticas.

## Política de roteamento
- Planejamento/arquitetura: modelo forte.
- Implementação repetitiva: modelo médio.
- Revisão de segurança e decisões críticas: modelo forte.
- Reformatação e tarefas mecânicas: modelo econômico.

## Estratégia operacional
- Router decide modelo por tipo de tarefa, risco e prazo.
- Registrar decisão de roteamento por task_id.
- Reavaliar política semanalmente por métricas reais.

## Métricas mínimas
- taxa de retrabalho por tarefa
- tempo até merge
- custo por entrega concluída
- falhas de qualidade pós-merge
