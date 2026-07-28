"""Discover languages and patterns from the patterns directory."""

from __future__ import annotations

from pathlib import Path


PatternRegistry = dict[str, dict[str, Path]]


def discover_patterns(patterns_dir: Path) -> PatternRegistry:
    """Scan valid pattern plugins at runtime."""
    registry: PatternRegistry = {}
    if not patterns_dir.is_dir():
        return registry

    for language_dir in sorted(patterns_dir.iterdir()):
        if not language_dir.is_dir() or language_dir.name.startswith((".", "_")):
            continue

        patterns: dict[str, Path] = {}
        for pattern_dir in sorted(language_dir.iterdir()):
            if not pattern_dir.is_dir() or pattern_dir.name.startswith((".", "_")):
                continue
            if (
                (pattern_dir / "meta.yaml").is_file()
                and (pattern_dir / "key.yaml.tmpl").is_file()
                and (pattern_dir / "templates").is_dir()
            ):
                patterns[pattern_dir.name] = pattern_dir

        if patterns:
            registry[language_dir.name] = patterns

    return registry
