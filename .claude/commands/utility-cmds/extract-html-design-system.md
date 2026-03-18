Extrair `design-system.html` de um HTML de referência com fidelidade máxima.

Argumentos: `$ARGUMENTS` (caminho para `index.html`)

Passos:
1. Ler `~/.claude/docs/frontend-vibe/DESIGN_SYSTEM_EXTRACTION_PROMPT.md`.
2. Aplicar as instruções ao arquivo de referência informado em `$ARGUMENTS`.
3. Gerar `design-system.html` no mesmo diretório do arquivo de entrada.
4. Validar visualmente que hero/layout/classes/anim estão fiéis.

Critério de sucesso:
- `design-system.html` parece parte do mesmo produto, não um redesign.
