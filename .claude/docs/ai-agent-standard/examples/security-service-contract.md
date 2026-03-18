# Security Service Contract (example)

## Purpose
Permitir que agentes acionem operações sensíveis sem acesso direto a credenciais reais.

## Endpoint
`POST /v1/secure-action`

## Input
```json
{
  "action": "db_read_only_query",
  "resource": "orders",
  "requester": "backend-agent",
  "reason": "validate task T-102"
}
```

## Policy
- valida escopo do requester
- aplica least privilege
- audita request_id, actor, timestamp, action

## Output
Resposta sanitizada sem segredos e sem dados sensíveis desnecessários.
