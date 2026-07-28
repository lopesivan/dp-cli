"""Command-line entrypoint for the design pattern generator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from core.config import (
    ConfigError,
    create_config,
    load_config,
    load_meta,
    merge_missing_defaults,
    save_config,
)
from core.registry import PatternRegistry, discover_patterns
from core.renderer import RenderError, render_outputs


PROJECT_DIR = Path(__file__).resolve().parent
PATTERNS_DIR = PROJECT_DIR / "patterns"


def build_parser(registry: PatternRegistry) -> argparse.ArgumentParser:
    """Build the CLI parser from the discovered languages."""
    parser = argparse.ArgumentParser(
        prog="dp",
        description="Gera scaffolding de padrões de projeto.",
    )
    languages = parser.add_mutually_exclusive_group()
    for language in sorted(registry):
        languages.add_argument(
            f"--{language}",
            action="store_const",
            const=language,
            dest="language",
            help=f"gera um padrão em {language}",
        )

    parser.add_argument("pattern", nargs="?", help="padrão de projeto")
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_patterns",
        help="lista linguagens e padrões disponíveis",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="força a regeneração das saídas existentes",
    )
    return parser


def print_registry(registry: PatternRegistry) -> None:
    """Print all discovered languages and patterns."""
    for language in sorted(registry):
        patterns = ", ".join(sorted(registry[language]))
        print(f"{language}: {patterns}")


def display_path(path: Path, working_dir: Path) -> str:
    """Return a concise path for CLI output."""
    try:
        return str(path.relative_to(working_dir))
    except ValueError:
        return str(path)


def validate_selection(
    parser: argparse.ArgumentParser,
    registry: PatternRegistry,
    language: str | None,
    pattern: str | None,
) -> tuple[str, str]:
    """Validate and return the selected language and pattern."""
    if language is None or pattern is None:
        parser.error("informe uma linguagem e um padrão")

    if pattern not in registry.get(language, {}):
        available = ", ".join(sorted(registry.get(language, {})))
        parser.error(
            f"padrão '{pattern}' não disponível para {language}"
            + (f"; disponíveis: {available}" if available else "")
        )

    return language, pattern


def run_generation(
    registry: PatternRegistry,
    language: str,
    pattern: str,
    working_dir: Path,
    force: bool,
) -> int:
    """Create the editable config or render the selected pattern."""
    pattern_dir = registry[language][pattern]
    meta = load_meta(pattern_dir / "meta.yaml")
    config_path = working_dir / "key.yaml"

    if not config_path.exists():
        create_config(
            template_path=pattern_dir / "key.yaml.tmpl",
            destination=config_path,
            meta=meta,
            language=language,
            pattern=pattern,
        )
        print("Criado: key.yaml")
        print("Edite o arquivo e execute o comando novamente.")
        return 0

    config = load_config(config_path)
    config, missing = merge_missing_defaults(
        config=config,
        meta=meta,
        language=language,
        pattern=pattern,
    )

    configured_language = config.get("language")
    configured_pattern = config.get("pattern")
    if configured_language != language or configured_pattern != pattern:
        raise ConfigError(
            "key.yaml pertence a "
            f"{configured_language}/{configured_pattern}, não a {language}/{pattern}"
        )

    if missing:
        save_config(config_path, config)
        for field in missing:
            print(f"Campo ausente: {field}; usando o valor padrão.")

    generated = render_outputs(
        pattern_dir=pattern_dir,
        meta=meta,
        context=config,
        destination_dir=working_dir,
        force=force,
    )
    for output in generated:
        print(f"Gerado: {display_path(output, working_dir)}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""
    registry = discover_patterns(PATTERNS_DIR)
    parser = build_parser(registry)
    args = parser.parse_args(argv)

    if args.list_patterns:
        print_registry(registry)
        return 0

    language, pattern = validate_selection(
        parser,
        registry,
        args.language,
        args.pattern,
    )

    try:
        return run_generation(
            registry=registry,
            language=language,
            pattern=pattern,
            working_dir=Path.cwd(),
            force=args.force,
        )
    except (ConfigError, RenderError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
