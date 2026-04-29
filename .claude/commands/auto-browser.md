---
name: auto-browser
description: Browser real com human-in-the-loop para automacao web. Usar automaticamente quando precisar navegar sites, fazer login, extrair dados de paginas protegidas, testar UI, ou qualquer tarefa que precise de um browser real alem de fetch HTML. Cobre 3 caminhos -- setup/deploy do Auto Browser, integracao MCP, e automacao de tarefas web.
---

# Auto Browser -- Browser Real para Agentes AI

Voce tem acesso ao Auto Browser, um MCP server nativo com Playwright + Chromium + noVNC.

## Quando usar

- Navegar sites que requerem login/autenticacao
- Extrair dados de plataformas protegidas (dashboards, areas de aluno, admin panels)
- Testar UI/UX de aplicacoes web locais ou remotas
- Preencher formularios complexos
- Capturar screenshots para analise visual
- Qualquer tarefa que um `fetch` simples nao resolve

## Stack do Auto Browser

- **Repo:** ~/Desktop/dme/projects/auto-browser
- **API:** http://127.0.0.1:8000
- **noVNC (visual takeover):** http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale
- **MCP endpoint:** http://127.0.0.1:8000/mcp

## Caminho 1: Setup e Deploy

### Verificar se esta rodando

```bash
curl -s http://127.0.0.1:8000/healthz 2>&1
```

Se retornar `{"status":"ok"}`, o stack esta ativo. Pule para o Caminho 2 ou 3.

### Subir o stack

```bash
cd ~/Desktop/dme/projects/auto-browser
docker compose up -d
```

### Configurar hosts permitidos

Edite `~/Desktop/dme/projects/auto-browser/.env`:
```
ALLOWED_HOSTS=seusite.com,outrosite.com,localhost,127.0.0.1
```

Depois reinicie:
```bash
cd ~/Desktop/dme/projects/auto-browser && docker compose restart controller
```

### Derrubar o stack

```bash
cd ~/Desktop/dme/projects/auto-browser && docker compose down
```

## Caminho 2: Integracao MCP

O Auto Browser expoe 72 ferramentas via MCP. As principais:

### Sessoes
- `browser.create_session` -- criar sessao com URL inicial
- `browser.get_session` -- estado atual da sessao
- `browser.close_session` -- encerrar sessao
- `browser.list_sessions` -- listar sessoes ativas

### Observacao
- `browser.observe` -- estado completo (URL, titulo, elementos interativeis, DOM)
- `browser.find_elements` -- buscar elementos por CSS selector
- `browser.screenshot` -- capturar screenshot
- `browser.eval_js` -- executar JavaScript na pagina

### Acoes
- `browser.execute_action` -- click, type, navigate, scroll, select, hover, press
- `browser.wait_for_selector` -- esperar elemento aparecer
- `browser.drag_drop` -- arrastar e soltar

### Autenticacao
- `browser.save_auth_profile` -- salvar estado de login para reuso
- `browser.get_auth_profile` -- carregar perfil de auth salvo
- `browser.list_auth_profiles` -- listar perfis salvos

### Rede e Debug
- `browser.get_console` -- logs do console do browser
- `browser.get_network_log` -- requisicoes de rede
- `browser.get_page_errors` -- erros da pagina
- `browser.get_cookies` -- cookies da sessao

## Caminho 3: Automacao Web

### Padrao de uso para qualquer site

```bash
# 1. Verificar se stack esta ativo
HEALTH=$(curl -s http://127.0.0.1:8000/healthz 2>&1)
if [ "$HEALTH" != '{"status":"ok"}' ]; then
  cd ~/Desktop/dme/projects/auto-browser && docker compose up -d
  sleep 15
fi

# 2. Verificar se o host esta na allowlist
# Se nao, adicionar ao .env e reiniciar

# 3. Criar sessao
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.create_session","arguments":{"name":"NOME","start_url":"URL"}}'

# 4. Para login: preencher via eval_js (mais confiavel que execute_action type)
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.eval_js","arguments":{"session_id":"ID","expression":"...JS..."}}'

# 5. Navegar e extrair dados
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.execute_action","arguments":{"session_id":"ID","action":"navigate","url":"URL"}}'

# 6. Extrair conteudo estruturado via eval_js
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.eval_js","arguments":{"session_id":"ID","expression":"JSON.stringify({url:location.href,title:document.title,headings:Array.from(document.querySelectorAll(\"h1,h2,h3\")).map(h=>h.textContent?.trim()),links:Array.from(document.querySelectorAll(\"a[href]\")).map(a=>({text:a.textContent?.trim()?.substring(0,60),href:a.href})).filter(a=>a.text),bodyText:document.body?.innerText?.substring(0,5000)})"}}'
```

### Dica critica: parsing de JSON

O rtk hook pode truncar outputs grandes. Para resultados seguros, SEMPRE salve em arquivo e parse com Python:

```bash
curl -s ... > /tmp/ab_result.json
python3 -c "
import json
with open('/tmp/ab_result.json','rb') as f:
    data = json.loads(f.read(), strict=False)
for item in data.get('content',[]):
    if item.get('type')=='text':
        inner = json.loads(item['text'], strict=False)
        if 'result' in inner:
            r = json.loads(inner['result'], strict=False)
            print(json.dumps(r, indent=2, ensure_ascii=False)[:5000])
"
```

### Perfis de auth salvos

Apos login bem-sucedido, SEMPRE salvar o perfil para reuso:

```bash
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.save_auth_profile","arguments":{"session_id":"ID","profile_name":"NOME"}}'
```

Para reusar:

```bash
curl -s http://127.0.0.1:8000/mcp/tools/call \
  -X POST -H 'content-type: application/json' \
  -d '{"name":"browser.create_session","arguments":{"name":"NOME","start_url":"URL","auth_profile":"NOME_PERFIL"}}'
```

## Perfis de Auth Disponiveis

- `clubedovalor-marcus` -- aluno.clubedovalor.com.br (Marcus Bonaldi)

## Regras

1. NUNCA armazenar senhas em arquivos commitados
2. SEMPRE salvar auth profile apos login bem-sucedido
3. Preferir eval_js para preencher formularios (mais confiavel que execute_action type)
4. SEMPRE verificar ALLOWED_HOSTS antes de navegar para novos dominios
5. Usar `strict=False` ao parsear JSON do Auto Browser (pode conter control chars)
6. Para sites novos, adicionar o host ao .env e reiniciar o controller
