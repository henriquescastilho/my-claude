# Plano: Atualizar códigos de fabricante via Playwright + PDF

## Contexto
Os produtos em `products.json` têm campo `code` com o código interno SDE (ex: "10279") e campo `manufacturerCode` com o código do fabricante (ex: "4581218"). O usuário quer que `code` seja substituído pelo código do fabricante. 7 dos 1.218 produtos não têm `manufacturerCode` preenchido. O PDF de orçamento já exibe `manufacturerCode` — precisamos garantir que todos os produtos tenham esse campo preenchido.

## Etapas

### 1. Instalar Playwright
- `npm install playwright` no diretório `sde-prototype`
- Instalar browsers: `npx playwright install chromium`

### 2. Criar script de scraping (`scripts/scrape-manufacturer-codes.ts`)
Script Node.js com Playwright que:
- Lê `products.json`
- Filtra os 7 produtos sem `manufacturerCode`
- Para cada um, acessa o `link` do produto no site `loja.sdedistribuidora.com.br`
- Extrai o texto do seletor `li.product__features--sku` (formato: "Código do Fabricante: XXXXXX")
- Parseia o código numérico
- Atualiza `products.json` com os códigos extraídos
- Também atualiza o campo `code` de TODOS os produtos para usar `manufacturerCode`

### 3. Atualizar o campo `code` de todos os produtos
No mesmo script, após scraping dos 7 faltantes:
- Para cada produto: `product.code = product.manufacturerCode`

### 4. Verificar/ajustar o PDF
- O PDF em `src/lib/pdf/orcamento.ts` já exibe `manufacturerCode` na coluna "Cód. Fabricante" (linha 188)
- Verificar se outros locais usam `product.code` e se precisam ser atualizados

### Arquivos a modificar
- `sde-prototype/src/data/products.json` — atualizar `code` e preencher `manufacturerCode` faltantes
- `sde-prototype/scripts/scrape-manufacturer-codes.ts` — novo script Playwright
- `sde-prototype/package.json` — adicionar dependência playwright

### Arquivos a verificar (sem modificação provável)
- `sde-prototype/src/lib/pdf/orcamento.ts` — já usa `manufacturerCode`
- `sde-prototype/src/types/product.ts` — tipo já tem ambos os campos

### Verificação
1. Rodar o script e confirmar que os 7 produtos faltantes foram preenchidos
2. Confirmar que todos os 1.218 produtos têm `code === manufacturerCode`
3. Testar geração do PDF no app e verificar que o código do fabricante aparece corretamente
