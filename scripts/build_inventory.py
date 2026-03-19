#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / ".claude"
CODEX = ROOT / ".codex"
OUT = ROOT / "docs" / "inventory"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        return {}
    try:
        _, body = text.split("---\n", 1)
        frontmatter, _ = body.split("\n---\n", 1)
    except ValueError:
        return {}
    out: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip('"')
    return out


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_agents() -> None:
    rows = []
    for path in sorted((CLAUDE / "agents").glob("*.md")):
        meta = parse_frontmatter(path)
        rows.append(
            (
                meta.get("name", path.stem),
                meta.get("description", ""),
                meta.get("model", ""),
                meta.get("memory", ""),
                path.name,
            )
        )
    lines = [
        "# Agents",
        "",
        f"Total: {len(rows)}",
        "",
        "| Name | Model | Memory | File | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, description, model, memory, filename in rows:
        lines.append(
            f"| `{name}` | `{model or '-'}` | `{memory or '-'}` | `{filename}` | {description or '-'} |"
        )
    write(OUT / "agents.md", "\n".join(lines))


def build_skills() -> None:
    rows = []
    for path in sorted((CLAUDE / "skills").glob("*/SKILL.md")):
        meta = parse_frontmatter(path)
        rows.append((path.parent.name, meta.get("description", "")))
    lines = [
        "# Skills",
        "",
        f"Total: {len(rows)}",
        "",
        "| Skill | Description |",
        "| --- | --- |",
    ]
    for name, description in rows:
        lines.append(f"| `{name}` | {description or '-'} |")
    write(OUT / "skills.md", "\n".join(lines))


def build_commands() -> None:
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in sorted((CLAUDE / "commands").glob("*/*")):
        if path.is_file():
            grouped[path.parent.name].append(path.name)
    lines = ["# Commands", ""]
    total = sum(len(v) for v in grouped.values())
    lines.append(f"Total: {total}")
    lines.append("")
    for group in sorted(grouped):
        files = grouped[group]
        lines.append(f"## {group}")
        lines.append("")
        lines.append(f"Count: {len(files)}")
        lines.append("")
        for file in files:
            lines.append(f"- `{file}`")
        lines.append("")
    write(OUT / "commands.md", "\n".join(lines))


def build_plugins() -> None:
    installed = json.loads(read_text(CLAUDE / "plugins" / "installed_plugins.json"))
    marketplaces = json.loads(read_text(CLAUDE / "plugins" / "known_marketplaces.json"))
    settings = json.loads(read_text(CLAUDE / "settings.json"))

    profile_data = {}
    for path in sorted((CLAUDE / "profiles").glob("*.json")):
        if ".bak" in path.name:
            continue
        profile = json.loads(read_text(path))
        enabled = sorted(k for k, v in profile.get("enabledPlugins", {}).items() if v)
        profile_data[path.stem] = {
            "model": profile.get("model", ""),
            "enabled": enabled,
        }

    plugins = installed.get("plugins", {})
    by_marketplace: dict[str, list[str]] = defaultdict(list)
    for name in sorted(plugins):
        _, marketplace = name.split("@", 1)
        by_marketplace[marketplace].append(name)

    lines = [
        "# Plugins",
        "",
        f"Installed plugins: {len(plugins)}",
        f"Known marketplaces: {len(marketplaces)}",
        "",
        "## Global Enabled Plugins",
        "",
    ]
    for name in sorted(k for k, v in settings.get("enabledPlugins", {}).items() if v):
        lines.append(f"- `{name}`")

    lines.extend(["", "## Marketplaces", ""])
    for marketplace in sorted(marketplaces):
        source = marketplaces[marketplace]["source"]["repo"]
        lines.append(f"- `{marketplace}` -> `{source}`")

    lines.extend(["", "## Installed Plugins By Marketplace", ""])
    for marketplace in sorted(by_marketplace):
        lines.append(f"### {marketplace}")
        lines.append("")
        for name in by_marketplace[marketplace]:
            entries = plugins[name]
            latest = entries[-1]
            version = latest.get("version", "-")
            sha = latest.get("gitCommitSha", "-")
            lines.append(f"- `{name}` | version `{version}` | sha `{sha}`")
        lines.append("")

    lines.append("## Profile Matrix")
    lines.append("")
    for profile_name, data in profile_data.items():
        lines.append(f"### {profile_name}")
        lines.append("")
        lines.append(f"- model: `{data['model']}`")
        lines.append(f"- enabled plugin count: {len(data['enabled'])}")
        for name in data["enabled"]:
            lines.append(f"- `{name}`")
        lines.append("")

    write(OUT / "plugins.md", "\n".join(lines))


def build_profiles() -> None:
    global_settings = json.loads(read_text(CLAUDE / "settings.json"))
    lines = [
        "# Profiles",
        "",
        "## Global Settings",
        "",
        f"- model: `{global_settings.get('model', '-')}`",
        f"- enabled plugins: {sum(1 for value in global_settings.get('enabledPlugins', {}).values() if value)}",
        f"- extra marketplaces: {len(global_settings.get('extraKnownMarketplaces', {}))}",
        "",
        "## Profiles",
        "",
    ]
    for path in sorted((CLAUDE / "profiles").glob("*.json")):
        if ".bak" in path.name:
            continue
        profile = json.loads(read_text(path))
        enabled = sorted(k for k, v in profile.get("enabledPlugins", {}).items() if v)
        lines.append(f"### {path.stem}")
        lines.append("")
        lines.append(f"- model: `{profile.get('model', '-')}`")
        for key, value in sorted(profile.get("env", {}).items()):
            lines.append(f"- env `{key}` = `{value}`")
        lines.append(f"- enabled plugins: {len(enabled)}")
        lines.append("")
    write(OUT / "profiles.md", "\n".join(lines))


def build_archives() -> None:
    lines = ["# Archives", ""]
    for folder in ["agents-archive", "agents-backups"]:
        base = CLAUDE / folder
        files = sorted(p for p in base.rglob("*.md") if ".bak." not in p.name)
        lines.append(f"## {folder}")
        lines.append("")
        lines.append(f"Count: {len(files)}")
        lines.append("")
        for path in files[:200]:
            lines.append(f"- `{path.relative_to(ROOT)}`")
        if len(files) > 200:
            lines.append(f"- `... and {len(files) - 200} more`")
        lines.append("")
    write(OUT / "archives.md", "\n".join(lines))


def build_codex_agents() -> None:
    rows = []
    for path in sorted((CODEX / "agents").glob("*.md")):
        if ".bak." in path.name:
            continue
        meta = parse_frontmatter(path)
        rows.append((meta.get("name", path.stem), meta.get("description", ""), path.name))
    lines = [
        "# Codex Agents",
        "",
        f"Total: {len(rows)}",
        "",
        "| Name | File | Description |",
        "| --- | --- | --- |",
    ]
    for name, description, filename in rows:
        lines.append(f"| `{name}` | `{filename}` | {description or '-'} |")
    write(OUT / "codex-agents.md", "\n".join(lines))


def build_codex_skills() -> None:
    rows = []
    for path in sorted(CODEX.glob("skills/**/SKILL.md")):
        meta = parse_frontmatter(path)
        rows.append((str(path.parent.relative_to(CODEX)), meta.get("description", "")))
    lines = [
        "# Codex Skills",
        "",
        f"Total: {len(rows)}",
        "",
        "| Skill Path | Description |",
        "| --- | --- |",
    ]
    for name, description in rows:
        lines.append(f"| `{name}` | {description or '-'} |")
    write(OUT / "codex-skills.md", "\n".join(lines))


def build_codex_vendors() -> None:
    skill_roots = sorted((CODEX / "vendor_imports" / "skills" / "skills").glob("*"))
    marketplaces = sorted((CODEX / "vendor_imports" / "claude" / "marketplaces").glob("*"))
    lines = [
        "# Codex Vendors",
        "",
        f"Curated skills roots: {len(skill_roots)}",
        f"Claude marketplaces: {len(marketplaces)}",
        "",
        "## Claude Marketplaces",
        "",
    ]
    for path in marketplaces:
        if path.is_dir():
            lines.append(f"- `{path.name}`")
    lines.extend(["", "## Curated Skills", ""])
    for path in skill_roots:
        if path.is_dir():
            lines.append(f"- `{path.name}`")
    write(OUT / "codex-vendors.md", "\n".join(lines))


def main() -> int:
    build_agents()
    build_skills()
    build_commands()
    build_plugins()
    build_profiles()
    build_archives()
    build_codex_agents()
    build_codex_skills()
    build_codex_vendors()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
