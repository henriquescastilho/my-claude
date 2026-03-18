# /vibe-download-reference

Baixar referência de frontend com o Website-Downloader e preparar para extração.

Argumentos: `$ARGUMENTS` (URL do site)

## Execução recomendada
```bash
cd /tmp/Website-Downloader
uv sync
uv run playwright install chromium
uv run python app.py
```

Depois no browser (`http://localhost:5001`):
1. Enviar URL.
2. Aguardar logs de processamento.
3. Baixar zip final.
4. Extrair em pasta local de referências.

## Pós-processamento
- Rodar `/vibe-extract <pasta_de_referencias>`.
- Rodar `/extract-html-design-system <caminho/index.html>`.
- Promover padrões para biblioteca do projeto.
