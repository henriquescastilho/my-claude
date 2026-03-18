Extrair inteligência frontend de uma pasta de referências HTML.

Argumentos: `$ARGUMENTS`

Fluxo:
1. Interpretar `$ARGUMENTS` como caminho de pasta contendo `referencias/*/index.html`.
2. Executar `~/.claude/tools/vibe_pack_builder.py --refs "$ARGUMENTS" --out ~/.claude/docs/frontend-vibe/generated/vibe-extraction-report.md`.
3. Gerar resumo executivo com:
- padrões repetidos de tipografia, layout, motion e superfície
- componentes reutilizáveis imediatos
- riscos de consistência visual
4. Sugerir plano de implementação em 3 sprints curtos.

Saída esperada:
- `~/.claude/docs/frontend-vibe/generated/vibe-extraction-report.md`
- recomendação prática priorizada (quick wins primeiro)
