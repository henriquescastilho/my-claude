# /agent-standard-audit

Audita se um projeto está aderente ao padrão AI Agent Standard.

Argumentos: `$ARGUMENTS` (path do projeto)

## Execução
```bash
python3 ~/.claude/tools/agent_standard_audit.py --root "$ARGUMENTS"
```

## O que verifica
- PRD e progresso
- presença de contratos de subagente
- política de roteamento
- baseline de segurança mínima
- existência de plano de rollback
