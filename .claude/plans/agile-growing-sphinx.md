# Plano: Novo Site SDE Distribuidora (Protótipo)

## Contexto
O dono da SDE Distribuidora quer permitir que seus revendedores criem orçamentos personalizados com logo própria e preços de revenda. O site atual roda na plataforma Agile B2B (SaaS) e não permite essa customização. Vamos construir um protótipo do zero, repaginado com anime.js, mantendo as cores e logos da SDE, para apresentar ao dono como ficaria a funcionalidade.

## Stack (simplificada para protótipo)
- **Next.js 14** (App Router) + **Tailwind CSS** + **anime.js v4.3.6**
- **JSON local** para dados de produtos (sem banco externo)
- **localStorage** para carrinho e dados do usuário
- **jsPDF + html2canvas** para gerar PDF do orçamento
- Sem autenticação real — login mockado para demo

## Cores e identidade (NÃO MUDAR)
- Verde SDE: `#00a651` (primário)
- Verde escuro: `#008c44` (hover)
- Dark: `#19191a`
- Branco: `#FFFFFF`
- Gray bg: `#f5f5f5`
- Font: Roboto
- Logo: `https://sdedistribuidora.agilecdn.com.br/imgs/sde1-173949490711111111-1749483846.png`

---

## Fases de Implementação

### Fase 1: Scraping de Todos os Produtos
**Objetivo**: Extrair todos os produtos de todas as 7 categorias via Playwright

**Categorias para varrer**:
1. `/comunicacao`
2. `/controle-de-acessso`
3. `/energia`
4. `/energia-solar`
5. `/incendio-e-iluminacao`
6. `/redes`
7. `/seguranca-eletronica`

**Script**: `scripts/scrape-products.ts`
- Navegar para cada categoria
- Pegar todos os product cards (`.product-card`)
- Extrair: nome, código, preço, marca, imagem URL, subcategoria
- Lidar com paginação (scroll/load more ou `?page=N`)
- Salvar em `data/products.json`

**Script**: `scripts/scrape-categories.ts`
- Extrair sidebar de subcategorias com contagem
- Salvar em `data/categories.json`

**Arquivos de saída**:
- `data/products.json` — array de todos os produtos
- `data/categories.json` — árvore de categorias/subcategorias

### Fase 2: Setup do Projeto
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `package.json` | Next.js 14, Tailwind, anime.js@4.3.6, jspdf, html2canvas, zustand |
| `tailwind.config.ts` | Paleta SDE, font Roboto |
| `next.config.ts` | remotePatterns para `sdedistribuidora.agilecdn.com.br` |
| `src/styles/globals.css` | Tailwind directives + custom styles |
| `public/logo-sde.png` | Logo baixada do CDN |

### Fase 3: Layout Base + Animações
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/lib/anime/animations.ts` | Presets reutilizáveis de animação |
| `src/hooks/useAnimateOnScroll.ts` | Hook IntersectionObserver + anime.js |
| `src/components/layout/Header.tsx` | Logo, busca, ícones carrinho/perfil |
| `src/components/layout/CategoryNav.tsx` | Barra verde horizontal com 7 categorias |
| `src/components/layout/Footer.tsx` | 3 colunas: Institucional, Unidades, Contato |
| `src/components/layout/MobileMenu.tsx` | Menu slide-in mobile |
| `src/app/layout.tsx` | Root layout compondo Header + CategoryNav + Footer |

**Animações anime.js nesta fase**:
- Logo entrance (scale + opacity no load)
- Category nav underline animada no hover
- Footer stagger reveal no scroll

### Fase 4: Home Page
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/components/home/HeroBanner.tsx` | Carousel com transições anime.js |
| `src/components/home/InfoBanners.tsx` | Frete grátis, Pagamento, Primeiro Acesso |
| `src/components/home/OffersSection.tsx` | Grid "AS MELHORES OFERTAS" |
| `src/components/home/LaunchSection.tsx` | Grid "LANÇAMENTOS" |
| `src/app/page.tsx` | Composição da home |

**Animações**:
- Hero slide transitions (translateX + opacity)
- Section headings slide-in
- Product cards stagger reveal no scroll

### Fase 5: Produtos (Card, Grid, Detalhe, Categoria)
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/components/product/ProductCard.tsx` | Card: imagem, nome, marca, preço, botão comprar |
| `src/components/product/ProductGrid.tsx` | Grid responsivo (4/3/2/1 colunas) |
| `src/components/product/ProductDetail.tsx` | View completa do produto |
| `src/components/product/ProductSearch.tsx` | Busca com sugestões |
| `src/app/[category]/page.tsx` | Listagem por categoria com filtros |
| `src/app/produto/[slug]/page.tsx` | Página de detalhe do produto |

**Animações**:
- Card hover: scale(1.03) + shadow verde
- Grid stagger: cards entram com delay escalonado
- Badge bounce ao adicionar ao carrinho

### Fase 6: Perfil do Usuário + Upload de Logo (FEATURE NOVA)
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/components/profile/ProfileForm.tsx` | Dados da empresa (mockados) |
| `src/components/profile/LogoUpload.tsx` | Drag-and-drop upload, preview, salva em localStorage como base64 |
| `src/components/profile/AccountSidebar.tsx` | Menu lateral: Mix, Pedidos, Dados, etc |
| `src/app/minha-conta/page.tsx` | Página de perfil |
| `src/app/minha-conta/meus-dados/page.tsx` | Dados + Logo upload |

### Fase 7: Carrinho com Preço Duplo (FEATURE NOVA)
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/hooks/useCart.ts` | Zustand store: items, addItem, removeItem, updateQty, updatePrecoRevenda |
| `src/components/cart/CartItem.tsx` | Linha: imagem, nome, Preço SDE (read-only), Preço Revenda (editável), qtd, subtotal |
| `src/components/cart/CartTable.tsx` | Tabela completa com header |
| `src/components/cart/CartSummary.tsx` | Totais SDE vs Revenda, margem %, botão "Gerar Orçamento" |
| `src/app/carrinho/page.tsx` | Página do carrinho |

**Colunas do carrinho**:
| Imagem | Produto | Preço SDE | Preço Revenda | Qtd | Subtotal | X |
|--------|---------|-----------|---------------|-----|----------|---|

**Animações**:
- Input preço revenda: borda verde ao focar
- Badge carrinho: bounce ao adicionar item
- Linha do produto: fade-in ao adicionar

### Fase 8: Gerador de Orçamento/PDF (FEATURE NOVA)
**Arquivos**:
| Arquivo | Descrição |
|---------|-----------|
| `src/lib/pdf/orcamento.ts` | Lógica de geração do PDF com jsPDF |
| `src/app/orcamento/page.tsx` | Preview do orçamento em HTML antes de gerar PDF |

**Layout do PDF**:
1. **Header**: Logo do REVENDEDOR (não da SDE!), nome fantasia, CNPJ, endereço
2. **Título**: "Orçamento" + número + data
3. **Tabela**: Produto, Código, Qtd, Preço Unitário (revenda), Subtotal
4. **Footer**: Total geral, validade, condições

### Fase 9: Polish e Responsividade
- Testar todas as animações
- Responsividade mobile/tablet
- Loading states e skeletons
- Micro-interações finais

---

## Estrutura de Diretórios Final

```
new_site/
├── data/
│   ├── products.json          # Produtos scrapeados
│   └── categories.json        # Categorias
├── scripts/
│   ├── scrape-products.ts     # Scraper Playwright
│   └── scrape-categories.ts   # Scraper de categorias
├── public/
│   └── logo-sde.png           # Logo SDE
├── src/
│   ├── lib/
│   │   ├── anime/animations.ts
│   │   ├── pdf/orcamento.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useCart.ts
│   │   └── useAnimateOnScroll.ts
│   ├── components/
│   │   ├── layout/ (Header, CategoryNav, Footer, MobileMenu)
│   │   ├── home/ (HeroBanner, InfoBanners, OffersSection, LaunchSection)
│   │   ├── product/ (ProductCard, ProductGrid, ProductDetail, ProductSearch)
│   │   ├── cart/ (CartItem, CartTable, CartSummary)
│   │   ├── profile/ (ProfileForm, LogoUpload, AccountSidebar)
│   │   └── ui/ (Button, Input, Modal)
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx (home)
│   │   ├── [category]/page.tsx
│   │   ├── produto/[slug]/page.tsx
│   │   ├── carrinho/page.tsx
│   │   ├── orcamento/page.tsx
│   │   └── minha-conta/
│   │       ├── page.tsx
│   │       └── meus-dados/page.tsx
│   └── styles/globals.css
├── tailwind.config.ts
├── next.config.ts
└── package.json
```

## Referências (arquivos capturados do site atual)
- `home.html` — estrutura da home, categorias do menu, logo URL
- `seguranca-eletronica.html` — estrutura dos product cards (`.product-card`, `.product-card__name`, `.product-card__new-price`, `.product-card__addtocart`)
- `carrinho-com-produto.html` — estrutura do carrinho (`.cart-table`, colunas, resumo, endereços)
- `produto-detalhe.html` — detalhe do produto (código, NCM, marca, preço, estoque)
- `meus-dados.html` — perfil do usuário (Razão Social, Nome Fantasia, CNPJ, endereço)
- `meus-pedidos.html` — histórico de pedidos

## Verificação
1. Rodar `npm run dev` e navegar por todas as páginas
2. Buscar um produto e ver resultado
3. Adicionar produto ao carrinho → ver preço SDE
4. Editar preço de revenda → ver margem calculada
5. Fazer upload de logo no perfil
6. Clicar "Gerar Orçamento" → PDF baixa com logo do revendedor e preços de revenda
7. Verificar animações anime.js em: scroll, hover, page load
8. Testar responsividade mobile
