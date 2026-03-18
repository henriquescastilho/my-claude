# Ralph Loop (Half Loop)

## Objetivo
Evitar degradação de contexto em tarefas longas.

## Entradas obrigatórias
- `PRD.md` (fonte da verdade)
- `progress.txt` (estado atual)
- `task_queue` (tarefas pequenas e verificáveis)

## Ciclo
1. Ler PRD e progresso atual.
2. Selecionar 1 tarefa de menor risco e escopo fechado.
3. Executar + validar + registrar evidência.
4. Atualizar `progress.txt` com o que foi feito e pendências.
5. Reset de contexto do agente.
6. Recomeçar próximo ciclo.

## Regras
- Não carregar histórico gigante entre ciclos.
- Não iniciar nova tarefa sem registrar a anterior.
- Se houver falha, registrar causa raiz e rollback.
