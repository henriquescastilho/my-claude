---
name: Padrão de Segurança DME
description: OWASP Top 10 detalhado, checklist de segurança por entrega, e pentest mindset para revisão de código
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## OWASP Top 10 (sempre verificar)

1. **Injection** — Usar queries parametrizadas. NUNCA concatenar input do usuário em SQL/comandos.
2. **Broken Authentication** — Tokens com expiração, refresh tokens rotacionados, rate limiting em login.
3. **Sensitive Data Exposure** — HTTPS everywhere. Nunca logar senhas, tokens, ou PII. Env vars para secrets.
4. **XXE** — Desabilitar processamento de entidades externas em XML parsers.
5. **Broken Access Control** — Verificar permissões server-side. Nunca confiar no client.
6. **Security Misconfiguration** — Headers de segurança (CSP, HSTS, X-Frame-Options). Remover defaults.
7. **XSS** — Sanitizar todo output. Usar frameworks que escapam por padrão (React, Vue).
8. **Insecure Deserialization** — Validar e tipar todo input. Usar schemas (Zod, Pydantic).
9. **Using Components with Known Vulnerabilities** — Checar `npm audit` / `pip audit` antes de deploy.
10. **Insufficient Logging** — Logar tentativas de auth falhadas, acessos negados, erros 500.

## Checklist de Segurança por Entrega

- [ ] Variáveis sensíveis em env vars (nunca hardcoded)
- [ ] CORS configurado (nunca `*` em produção)
- [ ] Rate limiting em endpoints públicos
- [ ] Input validation em toda boundary (API routes, forms)
- [ ] Senhas com hash (bcrypt/argon2, nunca MD5/SHA)
- [ ] JWT com expiração curta + refresh token
- [ ] SQL injection protegido (ORM ou prepared statements)
- [ ] XSS protegido (escape automático do framework)
- [ ] CSRF tokens em formulários stateful
- [ ] Headers de segurança configurados
- [ ] Dependências sem CVEs conhecidas
- [ ] Logs sem dados sensíveis
- [ ] Erros não expõem stack traces ao cliente

## Pentest Mindset

Ao revisar código, pensar como atacante:
- "Se eu mandar 10.000 requests em 1 segundo, o que acontece?"
- "Se eu alterar o ID na URL, consigo ver dados de outro usuário?"
- "Se eu mandar um payload com `<script>`, ele executa?"
- "Se eu interceptar o token, ele expira quando?"
- "Se eu mandar um body malformado, o servidor crasha?"
