# Website Downloader Workflow

Repo base: `https://github.com/asimov-academy/Website-Downloader`

## O que o projeto entrega
- Renderização com Playwright para capturar sites com JS.
- Reescrita de assets para modo offline.
- Ajustes de scroll/visibilidade para páginas com Lenis/Locomotive.
- Export em `.zip` para biblioteca de referências local.

## Setup local
```bash
cd /tmp/Website-Downloader
uv sync
uv run playwright install chromium
uv run python app.py
```

Servidor: `http://localhost:5001`

## Pipeline recomendado para o seu fluxo
1. Escolher 1 site-alvo por vez (evitar mistura de estilos no mesmo ciclo).
2. Baixar com Website Downloader.
3. Salvar zip extraído em uma pasta de referências versionada.
4. Rodar comando de extração para gerar `design-system.html` fiel.
5. Promover padrões úteis para sua biblioteca (`hero`, `cards`, `forms`, `dash widgets`).

## Prompt-base para extração fiel (resumo)
- Reusar classes/anim/efeitos exatos.
- Não redesenhar.
- Gerar `design-system.html` no mesmo diretório do `index.html`.
- Seção obrigatória: hero clone + tipografia + cores/surfaces + componentes + layout + motion + ícones (se existir).

## Guardrails operacionais
- Nunca consumir referência sem revisar licenças/uso.
- Remover tracking/scripts externos desnecessários.
- Sempre validar offline e mobile antes de promover para biblioteca.
