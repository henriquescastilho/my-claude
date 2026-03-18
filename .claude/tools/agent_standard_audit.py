#!/usr/bin/env python3
"""Audit project compliance with ~/.claude/docs/ai-agent-standard."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

CHECKS = [
    ("PRD exists", lambda root: (root / "PRD.md").exists()),
    ("progress exists", lambda root: (root / "progress.txt").exists()),
    ("router policy exists", lambda root: any((root / p).exists() for p in ["router-policy.yaml", ".ai/router-policy.yaml", "config/router-policy.yaml"])),
    ("subagent contract exists", lambda root: any((root / p).exists() for p in ["SUBAGENT_TASK_CONTRACT.md", "docs/SUBAGENT_TASK_CONTRACT.md", ".ai/SUBAGENT_TASK_CONTRACT.md"])),
    ("rollback plan mentioned in PRD", lambda root: _prd_has_rollback(root)),
    ("security baseline referenced", lambda root: _has_security_reference(root)),
]


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _prd_has_rollback(root: pathlib.Path) -> bool:
    prd = root / "PRD.md"
    if not prd.exists():
        return False
    text = _read_text(prd).lower()
    return "rollback" in text or "revers" in text


def _has_security_reference(root: pathlib.Path) -> bool:
    candidates = [root / "PRD.md", root / "README.md", root / "docs" / "README.md"]
    blob = "\n".join(_read_text(p) for p in candidates if p.exists()).lower()
    return any(k in blob for k in ["security", "seguran", "secret", "credential", "least privilege"])


def audit(root: pathlib.Path) -> int:
    print(f"Audit root: {root}")

    passed = 0
    for name, fn in CHECKS:
        ok = bool(fn(root))
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}")
        if ok:
            passed += 1

    total = len(CHECKS)
    print(f"\nScore: {passed}/{total}")

    if passed == total:
        print("Status: compliant")
        return 0
    if passed >= total - 2:
        print("Status: partially compliant")
        return 1

    print("Status: non-compliant")
    return 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit project against AI Agent Standard")
    parser.add_argument("--root", required=True, help="Project root directory")
    args = parser.parse_args()

    root = pathlib.Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Invalid root: {root}", file=sys.stderr)
        raise SystemExit(2)

    raise SystemExit(audit(root))


if __name__ == "__main__":
    main()
