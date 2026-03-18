# /agent-standard-bootstrap

Inicializa um projeto no padrão multiagente seguro.

Argumentos: `$ARGUMENTS` (nome do projeto)

## Passos
1. Criar `PRD.md` usando `docs/ai-agent-standard/templates/PRD_TEMPLATE.md`.
2. Criar `progress.txt` usando `docs/ai-agent-standard/templates/PROGRESS_TEMPLATE.txt`.
3. Definir mapa de subagentes com base em `examples/subagents.yaml`.
4. Definir política de roteamento com `examples/router-policy.yaml`.
5. Rodar auditoria: `python3 ~/.claude/tools/agent_standard_audit.py --root <project_dir>`.

## Resultado esperado
- Projeto com governança mínima de agentes
- Segurança baseline ativa
- Loop Ralph preparado para execução
