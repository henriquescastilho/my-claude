# Plano: KYC Próprio com Validação por IA (Gemini)

## Contexto

Precisamos de um KYC próprio da PaymentsLine, independente do Asaas. O KYC acontece logo após a confirmação de email, antes de acessar o dashboard. A subconta Asaas continua sendo criada apenas após o pagamento, mas usando os dados já validados pelo nosso KYC.

**Fluxo completo:**
```
Registro → Confirmar email → KYC (dados + docs + validação IA) → Dashboard (view only)
                                                                  → Pagamento → Subconta Asaas (com dados KYC) → Operações financeiras
```

## O que o KYC coleta e valida

### Etapa 1: Dados complementares (`/cadastro/endereco`)
- **CEP** → auto-fill via ViaCEP
- **Endereço** (rua, número, complemento, bairro, cidade, estado)
- **Renda/faturamento mensal**
- **Tipo de empresa** (só PJ: MEI, LTDA, Individual, Associação)
- **Data de nascimento** (só PF)

### Etapa 2: Documentos (`/cadastro/documentos`) — já existe
- **Documento com foto (frente)** — RG ou CNH
- **Documento (verso)**
- **Selfie segurando documento**

### Etapa 3: Validação automática por IA (Gemini)
Após upload dos 3 docs, o backend usa Gemini Vision para:
1. **Validar documento:** É um RG/CNH legítimo? Está legível? Não está cortado?
2. **Extrair dados:** Nome, CPF/RG, data de nascimento do documento
3. **Comparar selfie:** A pessoa na selfie é a mesma do documento?
4. **Cross-check:** Nome/CPF do documento bate com o cadastro?
5. **Resultado:** APPROVED, NEEDS_REVIEW, ou REJECTED (com motivo)

## Passos de implementação

### 1. Novos campos no modelo Tenant

**Arquivo:** `backend/services/shared/models.py`

```python
# KYC fields
address = Column(String, nullable=True)
address_number = Column(String, nullable=True)
complement = Column(String, nullable=True)
province = Column(String, nullable=True)
postal_code = Column(String, nullable=True)
city = Column(String, nullable=True)
state = Column(String, nullable=True)
income_value = Column(Float, nullable=True)
company_type = Column(String, nullable=True)
birth_date = Column(String, nullable=True)
kyc_status = Column(String, default="PENDING")  # PENDING, IN_REVIEW, APPROVED, REJECTED
kyc_rejection_reason = Column(String, nullable=True)
kyc_completed_at = Column(DateTime, nullable=True)
```

### 2. Migration SQL

**Arquivo:** `backend/migrations/add_kyc_fields.sql` (CRIAR)

### 3. Serviço de validação KYC com Gemini

**Arquivo:** `backend/services/shared/kyc_validator.py` (CRIAR)

Usa Gemini Vision (já integrado no projeto via `google-genai`) para:

```python
class KYCValidator:
    def validate_document(self, doc_front: bytes, doc_back: bytes) -> KYCDocResult:
        """Valida se o documento é legítimo e extrai dados"""

    def validate_selfie_match(self, selfie: bytes, doc_front: bytes) -> KYCSelfieResult:
        """Compara selfie com foto do documento"""

    def cross_check(self, extracted: KYCDocResult, tenant: Tenant) -> KYCCrossCheckResult:
        """Verifica se dados do documento batem com cadastro"""

    def run_full_kyc(self, tenant_id, doc_front, doc_back, selfie) -> KYCResult:
        """Orquestra validação completa"""
```

Reutiliza: `backend/services/worker_extract/gemini_client.py` como referência para chamadas Gemini.

### 4. Endpoint de dados KYC

**Arquivo:** `backend/services/api/routers/auth.py` (MODIFICAR)

```
POST /api/auth/kyc-data
```
→ Salva dados no Tenant, retorna ok.

### 5. Endpoint de validação KYC (trigger após upload dos 3 docs)

**Arquivo:** `backend/services/api/routers/user_settings.py` (MODIFICAR)

```
POST /api/account/validate-kyc
```
→ Baixa os 3 docs do GCS, roda `KYCValidator.run_full_kyc()`, atualiza `kyc_status`, retorna resultado.

### 6. Nova página `/cadastro/endereco`

**Arquivo:** `frontend/src/app/(dashboard)/cadastro/endereco/page.tsx` (CRIAR)

### 7. Atualizar fluxo de cadastro existente

- `cadastro/cnpj` — adicionar company_type, redirect para `/cadastro/endereco`
- `cadastro/pf` — adicionar birth_date, redirect para `/cadastro/endereco`
- `cadastro/documentos` — trigger validação KYC + mostrar resultado

### 8. Atualizar AccountGate / RouteGuard

- Checar `kyc_status` do usuário
- Se não APPROVED: redirecionar para etapa pendente do KYC

### 9. Atualizar `onboard_tenant()` para usar dados KYC

- Usar dados reais do Tenant ao criar subconta Asaas (após pagamento)
- Sem mais defaults hardcoded

## Arquivos a criar
- `frontend/src/app/(dashboard)/cadastro/endereco/page.tsx`
- `backend/services/shared/kyc_validator.py`
- `backend/migrations/add_kyc_fields.sql`

## Arquivos a modificar
- `backend/services/shared/models.py`
- `backend/services/api/routers/auth.py`
- `backend/services/api/routers/user_settings.py`
- `backend/services/shared/tenant_onboarding_service.py`
- `frontend/src/app/(dashboard)/cadastro/cnpj/page.tsx`
- `frontend/src/app/(dashboard)/cadastro/pf/page.tsx`
- `frontend/src/app/(dashboard)/cadastro/documentos/page.tsx`
- `frontend/src/components/auth/account-gate.tsx`

## Verificação
1. `cd frontend && npm run build` — compila sem erros
2. `python3 -c "import ast; ast.parse(...)"` — todos os .py sem erro de sintaxe
3. Fluxo manual: cadastro → email → endereço (CEP auto-fill) → docs → validação IA → dashboard
4. Testar com doc válido → APPROVED
5. Testar com selfie de outra pessoa → REJECTED
6. Verificar que após pagamento, subconta Asaas é criada com dados reais (sem defaults)
