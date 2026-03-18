# Security Baseline for Agents

## Princípios obrigatórios
- Rodar agentes em ambiente isolado (Dev Container ou VPS).
- Proibir execução com bypass global de permissões.
- Segredos fora do código e fora de prompts.
- Privilégio mínimo em todos os tokens e integrações.

## Runtime seguro
- Ambiente efêmero para execução arriscada.
- Usuário sem privilégios de administrador por padrão.
- Bloqueio de comandos destrutivos sem aprovação humana.

## Security Service (proxy de credenciais)
Em vez de dar credenciais reais ao agente:
- agente chama API interna com token de escopo reduzido
- API valida policy e executa ação sensível
- API registra auditoria e retorna resposta sanitizada

## Checklist antes de produção
- [ ] sem segredos em repositório
- [ ] sem chaves em logs
- [ ] rotação de tokens definida
- [ ] política de rollback documentada
- [ ] trilha de auditoria habilitada
