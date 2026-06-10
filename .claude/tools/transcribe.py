#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "faster-whisper>=1.0.3",
# ]
# ///
"""Transcrever audios locais com faster-whisper (PT-BR por padrao).

Uso:
    uv run ~/.claude/tools/transcribe.py <arquivo1> [arquivo2 ...]
    uv run ~/.claude/tools/transcribe.py --model small --lang pt arquivo.ogg

Modelos: tiny | base | small | medium | large-v3 (default: small, bom custo/qualidade pra PT)
Saida: stdout com bloco por arquivo + cabecalho.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Transcrever audio local com faster-whisper")
    parser.add_argument("files", nargs="+", help="Arquivos de audio (.ogg, .mp3, .m4a, .wav, ...)")
    parser.add_argument("--model", default="small", help="Tamanho do modelo whisper")
    parser.add_argument("--lang", default="pt", help="Idioma (pt, en, es, ...)")
    parser.add_argument("--device", default="cpu", help="cpu ou cuda")
    parser.add_argument("--compute", default="int8", help="int8, float16, float32")
    args = parser.parse_args()

    from faster_whisper import WhisperModel

    print(f"[transcribe] carregando modelo '{args.model}' ({args.compute} em {args.device})...", file=sys.stderr)
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute)

    for raw_path in args.files:
        path = Path(raw_path).expanduser()
        if not path.exists():
            print(f"\n=== {path} === [ERRO: arquivo nao encontrado]\n", flush=True)
            continue

        print(f"[transcribe] processando {path.name}...", file=sys.stderr)
        segments, info = model.transcribe(
            str(path),
            language=args.lang,
            vad_filter=True,
            beam_size=5,
        )

        print(f"\n=== {path.name} ===")
        print(f"[lang={info.language} prob={info.language_probability:.2f} dur={info.duration:.1f}s]")
        full_text = []
        for seg in segments:
            ts = f"[{seg.start:6.1f}s]"
            line = seg.text.strip()
            print(f"{ts} {line}")
            full_text.append(line)
        print("\n--- texto contínuo ---")
        print(" ".join(full_text))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
