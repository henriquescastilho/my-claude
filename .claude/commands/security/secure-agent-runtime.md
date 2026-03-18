# /secure-agent-runtime

Aplica baseline de segurança para execução de agentes.

Argumentos: `$ARGUMENTS`

## Controles obrigatórios
- Ambiente isolado (Dev Container ou VPS).
- Proibição de bypass global de permissões.
- Segredos somente por variáveis gerenciadas.
- Bloqueio de operações destrutivas sem aprovação humana.

## Verificações
- sem credenciais no repo
- sem logs com tokens
- política de rollback definida
- trilha de auditoria habilitada

## Referência
`~/.claude/docs/ai-agent-standard/security-baseline.md`
